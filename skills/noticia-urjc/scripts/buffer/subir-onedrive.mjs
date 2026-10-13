#!/usr/bin/env node
// Sube un fichero local (p. ej. un vídeo para las redes) a TU OneDrive (la cuenta y el navegador de usuario.json),
// crea un vínculo de solo lectura para cualquier persona y devuelve una URL de descarga directa, que funciona
// sin sesión ni cookies: es la que necesita Buffer para adjuntar el fichero.
//
// Uso: node subir-onedrive.mjs <fichero> <usuario.json>   (normalmente desde subir-onedrive.sh)
//
// No usa los menús de OneDrive: abre la página de OneDrive de la cuenta para tener su sesión, entrega el fichero
// a un <input type=file> propio con DOM.setFileInputFiles (por ruta, sin el límite de 50 MB de Playwright por CDP)
// y lo sube con la API REST de SharePoint, por trozos, a la carpeta onedrive.carpeta («noticia-urjc») de «Mis archivos».
//
// Imprime un JSON con { archivo, bytes, vinculo, descarga }.
// Códigos de salida: 0 ok · 3 sin sesión (tiempo de espera agotado) · 4 no se puede crear el vínculo público
// (la organización no lo permite) · 5 la subida ha fallado · 6 la URL de descarga no devuelve el fichero · 1 otro.

import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(path.join(process.env.PLAYWRIGHT_CORE_DIR || '.', 'x.js'));
const { chromium } = require('playwright-core');

const LOGIN_WAIT_MS = 5 * 60 * 1000;
const TROZO = 8 * 1024 * 1024;

function fail(code, msg) {
  console.error(`ERROR ${msg}`);
  process.exit(code);
}

async function main() {
  const [fichero, usuarioPath] = process.argv.slice(2);
  if (!fichero || !usuarioPath) fail(1, 'uso: node subir-onedrive.mjs <fichero> <usuario.json>');
  if (!fs.existsSync(fichero)) fail(1, `no existe ${fichero}`);
  const usuario = JSON.parse(fs.readFileSync(usuarioPath, 'utf8'));
  if (!usuario.navegador?.puerto) fail(1, `falta navegador.puerto en ${usuarioPath}`);
  const od = { sitio: 'https://urjc-my.sharepoint.com', carpeta: 'noticia-urjc', ...(usuario.onedrive || {}) };
  const carpeta = od.carpeta;

  const browser = await chromium.connectOverCDP(`http://localhost:${usuario.navegador.puerto}`);
  const ctx = browser.contexts()[0];
  const page = await ctx.newPage();
  await page.goto(`${od.sitio.replace(/\/$/, '')}/my`, { waitUntil: 'domcontentloaded' });

  // Espera a la sesión de OneDrive (la persona inicia sesión en la ventana si hace falta).
  const limite = Date.now() + LOGIN_WAIT_MS;
  let avisado = false;
  while (!(await page.evaluate(() => !!window._spPageContextInfo?.webAbsoluteUrl).catch(() => false))) {
    if (Date.now() > limite) fail(3, `no hay sesión de OneDrive en ${page.url()}`);
    if (!avisado && /login\.microsoftonline\.com|identifica\.urjc\.es/.test(page.url())) {
      console.log('ESPERANDO: inicia sesión en OneDrive en la ventana de Chrome (hasta 5 minutos)…');
      avisado = true;
    }
    await page.waitForTimeout(1500);
  }

  // Entrega el fichero a un <input type=file> propio, por ruta.
  await page.evaluate(() => {
    const i = document.createElement('input');
    i.type = 'file'; i.id = 'noticia-urjc-subida'; i.style.display = 'none';
    document.body.appendChild(i);
  });
  const cdp = await ctx.newCDPSession(page);
  const { root } = await cdp.send('DOM.getDocument', { depth: 0 });
  const { nodeId } = await cdp.send('DOM.querySelector', { nodeId: root.nodeId, selector: '#noticia-urjc-subida' });
  await cdp.send('DOM.setFileInputFiles', { nodeId, files: [path.resolve(fichero)] });

  const r = await page.evaluate(async ({ carpeta, TROZO }) => {
    const web = _spPageContextInfo.webAbsoluteUrl, rel = _spPageContextInfo.webServerRelativeUrl;
    const h = { Accept: 'application/json;odata=nometadata', 'Content-Type': 'application/json;odata=nometadata' };
    const ruta = p => encodeURIComponent(p.replace(/'/g, "''"));
    const digest = (await (await fetch(web + '/_api/contextinfo', { method: 'POST', headers: h })).json()).FormDigestValue;
    const post = (url, body) => fetch(web + url, { method: 'POST', headers: { ...h, 'X-RequestDigest': digest }, body });
    const file = document.getElementById('noticia-urjc-subida').files[0];
    const dir = `${rel}/Documents/${carpeta}`;
    const destino = `${dir}/${file.name}`;

    const existe = await (await fetch(web + `/_api/web/GetFolderByServerRelativePath(decodedurl='${ruta(dir)}')?$select=Exists`, { headers: h })).json();
    if (!existe.Exists) {
      const c = await post(`/_api/web/folders/AddUsingPath(decodedurl='${ruta(dir)}')`);
      if (!c.ok) return { error: 'subida', detalle: `no se pudo crear la carpeta ${dir}: ${c.status}` };
    }
    let resp = await post(`/_api/web/GetFolderByServerRelativePath(decodedurl='${ruta(dir)}')/Files/AddUsingPath(decodedurl='${ruta(file.name)}',overwrite=true)`,
      file.size <= TROZO ? file : new Blob([]));
    if (!resp.ok) return { error: 'subida', detalle: `AddUsingPath: ${resp.status} ${await resp.text()}` };
    if (file.size > TROZO) {
      const id = crypto.randomUUID();
      const base = `/_api/web/GetFileByServerRelativePath(decodedurl='${ruta(destino)}')`;
      for (let off = 0; off < file.size; off += TROZO) {
        const trozo = file.slice(off, Math.min(off + TROZO, file.size));
        const ultimo = off + TROZO >= file.size;
        const op = off === 0 ? `StartUpload(uploadId=guid'${id}')`
          : ultimo ? `FinishUpload(uploadId=guid'${id}',fileOffset=${off})` : `ContinueUpload(uploadId=guid'${id}',fileOffset=${off})`;
        resp = await post(`${base}/${op}`, trozo);
        if (!resp.ok) return { error: 'subida', detalle: `${op.split('(')[0]} en ${off}: ${resp.status} ${await resp.text()}` };
        if (off === 0 && ultimo) break;
      }
    }
    const info = await (await fetch(web + `/_api/web/GetFileByServerRelativePath(decodedurl='${ruta(destino)}')?$select=Length,ServerRelativeUrl`, { headers: h })).json();
    if (Number(info.Length) !== file.size) return { error: 'subida', detalle: `tamaño en OneDrive ${info.Length} ≠ ${file.size}` };

    const s = await post(`/_api/web/GetFileByServerRelativePath(decodedurl='${ruta(destino)}')/ListItemAllFields/ShareLink`,
      JSON.stringify({ request: { createLink: true, settings: { linkKind: 4, expiration: null } } }));
    const sj = await s.json();
    const vinculo = sj.sharingLinkInfo?.Url;
    if (!s.ok || !vinculo || sj.sharingLinkInfo.LinkKind !== 4)
      return { error: 'vinculo', detalle: JSON.stringify(sj['odata.error'] || sj.error || sj).slice(0, 300) };
    const token = new URL(vinculo).pathname.split('/').pop();
    return { archivo: info.ServerRelativeUrl, bytes: file.size, vinculo, descarga: `${web}/_layouts/15/download.aspx?share=${token}` };
  }, { carpeta, TROZO });

  await page.close();
  if (r.error === 'subida') fail(5, r.detalle);
  if (r.error === 'vinculo') fail(4, `no se ha podido crear un vínculo para cualquier persona: ${r.detalle}`);

  // Comprueba, sin sesión, que la URL de descarga devuelve el fichero.
  const t = await fetch(r.descarga, { headers: { Range: 'bytes=0-1023' }, redirect: 'follow' });
  const tipo = t.headers.get('content-type') || '';
  if (![200, 206].includes(t.status) || /text\/html|text\/plain/.test(tipo))
    fail(6, `la URL de descarga responde ${t.status} ${tipo}: ${r.descarga}`);
  console.log(JSON.stringify({ ...r, tipo }, null, 2));
  process.exit(0);
}

main().catch(e => fail(1, e.message.split('\n')[0]));
