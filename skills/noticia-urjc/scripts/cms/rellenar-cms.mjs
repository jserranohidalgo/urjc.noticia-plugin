#!/usr/bin/env node
// Rellena el formulario "Editar ítem" del CMS (Joomla/K2) de la web de una Escuela con el contenido de
// noticia.md, sobre tu ventana de Chrome ya abierta en el puerto CDP de usuario.json (navegador.puerto). NO pulsa Guardar ni
// Cerrar: en este CMS "Publicado" viene en "Sí", así que Guardar publica, y ese clic es de la persona.
// Hace falta pulsar Guardar y después Cerrar: solo con Guardar el ítem ya tiene URL, pero no aparece en la
// portada de la Escuela hasta que se cierra el formulario.
//
// Uso: node rellenar-cms.mjs <carpeta-noticia> <escuela.json> <usuario.json>
// Normalmente se invoca desde rellenar-cms.sh, que instala playwright-core y abre la ventana.
//
// Ruta de entrada (comprobada): eris.urjc.es/<slug> → Intranet (ventana emergente, resuelve el SSO) →
// intranet-inicio → «Panel administración editores…» → administracion-facultades → «Publicar»
// (ventana emergente) → nuevo-articulo. Por www.urjc.es el panel carga, pero «Publicar» no abre el formulario.
//
// Códigos de salida: 0 ok · 2 sin VPN · 3 sin sesión (tiempo de espera agotado) · 4 la cuenta no tiene
// permisos · 5 la página no es la esperada · 6 el formulario no ha quedado como se esperaba · 1 otro error.

import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(process.env.PLAYWRIGHT_CORE_DIR ? path.join(process.env.PLAYWRIGHT_CORE_DIR, 'x.js') : import.meta.url);
const { chromium } = require('playwright-core');

const LOGIN_WAIT_MS = 5 * 60 * 1000;

function fail(code, msg) {
  console.error(`ERROR ${msg}`);
  process.exit(code);
}

function leerNoticia(dir) {
  const md = fs.readFileSync(path.join(dir, 'noticia.md'), 'utf8');
  const titulo = md.match(/^# (.+)$/m)?.[1].trim();
  const seccion = h => md.split(`\n## ${h}\n`)[1]?.split('\n## ')[0].trim();
  const imagen = seccion('Imagen') || '';
  const linea = k => imagen.match(new RegExp(`^${k}:\\s*(.+)$`, 'mi'))?.[1].trim();
  const intro = seccion('Texto intro');
  const completo = seccion('Texto completo');
  if (!titulo || !intro || !completo) fail(1, `noticia.md incompleto en ${dir} (título, Texto intro o Texto completo)`);
  const archivo = path.join(dir, linea('Archivo') || 'imagen-1200x800.png');
  return {
    titulo,
    intro: intro.startsWith('<p') ? intro : `<p>${intro}</p>`,
    completo,
    imagen: fs.existsSync(archivo) ? archivo : null,
    pie: linea('Pie de foto') || linea('Créditos / pie de foto') || '',
    creditos: linea('Créditos') || '',
  };
}

// Pulsa un enlace que puede abrir una ventana emergente o navegar en la misma; devuelve la página resultante.
async function pulsar(page, locator) {
  const ctx = page.context();
  const [popup] = await Promise.all([
    ctx.waitForEvent('page', { timeout: 5000 }).catch(() => null),
    locator.click(),
  ]);
  const p = popup || page;
  await p.waitForLoadState('domcontentloaded');
  return p;
}

// Espera a que la página llegue a `destino`, dando tiempo a que la persona inicie sesión si hace falta.
async function esperarDestino(page, destino) {
  const limite = Date.now() + LOGIN_WAIT_MS;
  let avisado = false;
  while (Date.now() < limite) {
    const url = page.url();
    if (destino.test(url)) return;
    const texto = await page.locator('body').innerText().catch(() => '');
    if (/Permisos inadecuados/i.test(texto)) fail(4, 'la cuenta de esta ventana no tiene permisos para la Intranet de la URJC (no es editora de la web)');
    if (!avisado && /identifica\.urjc\.es|login\.microsoftonline\.com/.test(url) && /Credenciales|Iniciar sesión|Sign in/i.test(texto)) {
      console.log('ESPERANDO: no hay sesión iniciada. Inicia sesión en la ventana de Chrome (hasta 5 minutos)…');
      avisado = true;
    }
    await page.waitForTimeout(1500);
  }
  fail(avisado ? 3 : 5, `no se ha llegado a ${destino} (última URL: ${page.url()})`);
}

async function main() {
  const [dirNoticia, escuelaPath, usuarioPath] = process.argv.slice(2);
  if (!dirNoticia || !escuelaPath || !usuarioPath) fail(1, 'uso: node rellenar-cms.mjs <carpeta-noticia> <escuela.json> <usuario.json>');
  const escuela = JSON.parse(fs.readFileSync(escuelaPath, 'utf8'));
  const nav = JSON.parse(fs.readFileSync(usuarioPath, 'utf8')).navegador;
  if (!nav?.puerto) fail(1, `falta navegador.puerto en ${usuarioPath}`);
  const noticia = leerNoticia(dirNoticia);

  const browser = await chromium.connectOverCDP(`http://localhost:${nav.puerto}`);
  const ctx = browser.contexts()[0];
  let page = await ctx.newPage();

  try {
    await page.goto(`https://eris.urjc.es/${escuela.slugCMS}`, { waitUntil: 'domcontentloaded' });
  } catch (e) {
    if (/ERR_NAME_NOT_RESOLVED|ERR_CONNECTION/.test(e.message)) fail(2, 'eris.urjc.es no responde: conecta la VPN de la Universidad');
    throw e;
  }

  page = await pulsar(page, page.getByRole('link', { name: /^intranet$/i }).first());
  await esperarDestino(page, /\/intranet-inicio/);

  page = await pulsar(page, page.getByRole('link', { name: /Panel administración editores/i }));
  await esperarDestino(page, /\/administracion-facultades/);

  page = await pulsar(page, page.getByRole('link', { name: 'Publicar', exact: true }));
  await esperarDestino(page, /\/nuevo-articulo/);
  await page.locator('#title').waitFor({ timeout: 20000 }).catch(() => fail(5, 'nuevo-articulo no muestra el formulario "Editar ítem"'));
  await page.waitForFunction(() => window.Joomla?.editors?.instances?.introtext && window.Joomla.editors.instances.fulltext, null, { timeout: 20000 });

  // Contenido. Los <select> de categoría y etiquetas están envueltos por Chosen (ocultos), así que se fijan por JS.
  await page.fill('#title', noticia.titulo);
  const r = await page.evaluate(({ categoria, etiqueta, intro, completo }) => {
    const norm = s => s.replace(/^[-\s]+/, '').trim();
    const cat = document.getElementById('catid');
    const optCat = Array.from(cat.options).find(o => norm(o.text) === categoria);
    if (optCat) {
      cat.value = optCat.value;
      cat.dispatchEvent(new Event('change', { bubbles: true }));
      if (window.jQuery) jQuery(cat).trigger('liszt:updated').trigger('chosen:updated');
    }
    const tags = document.getElementById('tags');
    const optTag = Array.from(tags.options).find(o => o.text.trim() === etiqueta);
    if (optTag) {
      Array.from(tags.options).forEach(o => { o.selected = o === optTag; });
      document.getElementById('addTagButton').click();
    }
    Joomla.editors.instances.introtext.setValue(intro);
    Joomla.editors.instances.fulltext.setValue(completo);
    return { categoria: !!optCat, etiqueta: !!optTag };
  }, { categoria: escuela.categoriaCMS, etiqueta: escuela.etiquetaCMS, intro: noticia.intro, completo: noticia.completo });
  if (!r.categoria) fail(6, `no existe la categoría «${escuela.categoriaCMS}» en el desplegable del CMS`);
  if (!r.etiqueta) fail(6, `no existe la etiqueta «${escuela.etiquetaCMS}» en el CMS`);

  // Imagen (pestaña «Imagen»: los campos de texto solo se pueden rellenar con la pestaña visible).
  if (noticia.imagen) {
    await page.getByRole('link', { name: 'Imagen' }).first().click();
    await page.setInputFiles('input[type=file][name=image]', noticia.imagen);
    await page.fill('input[name=image_caption]', noticia.pie);
    await page.fill('input[name=image_credits]', noticia.creditos);
    await page.getByRole('link', { name: 'Contenido' }).first().click();
  }

  const estado = await page.evaluate(() => ({
    titulo: document.getElementById('title').value,
    categoria: document.getElementById('catid').selectedOptions[0]?.text.replace(/^[-\s]+/, '').trim(),
    etiquetas: Array.from(document.getElementById('selectedTags').options).map(o => o.text.trim()),
    publicado: document.querySelector('input[name=published]:checked')?.value === '1' ? 'Sí' : 'No',
    inicioPublicacion: document.getElementById('publish_up').value,
    parrafosIntro: (Joomla.editors.instances.introtext.getValue().match(/<p[\s>]/g) || []).length,
    parrafosCompleto: (Joomla.editors.instances.fulltext.getValue().match(/<p[\s>]/g) || []).length,
    imagen: document.querySelector('input[name=image]').files[0]?.name || null,
    pie: document.querySelector('input[name=image_caption]').value,
    creditos: document.querySelector('input[name=image_credits]').value,
  }));
  const esperado = estado.titulo === noticia.titulo && estado.categoria === escuela.categoriaCMS
    && estado.etiquetas.includes(escuela.etiquetaCMS) && estado.parrafosCompleto > 0
    && (!noticia.imagen || estado.imagen === path.basename(noticia.imagen));

  await page.bringToFront();
  await page.evaluate(() => window.scrollTo(0, 0));
  console.log(JSON.stringify(estado, null, 2));
  if (!noticia.imagen) console.log('AVISO: no hay imagen en la carpeta de la noticia; el formulario queda sin imagen');
  if (!esperado) fail(6, 'el formulario no ha quedado como se esperaba; revísalo en la ventana');
  console.log(`LISTO: formulario relleno y sin guardar. «Publicado: ${estado.publicado}»: ` +
    (estado.publicado === 'Sí' ? 'al pulsar Guardar, la noticia se publica' : 'al pulsar Guardar, queda guardada sin publicar') +
    '. Después hay que pulsar Cerrar para que aparezca en la portada de la Escuela.');
  process.exit(0);
}

main().catch(e => fail(1, e.message.split('\n')[0]));
