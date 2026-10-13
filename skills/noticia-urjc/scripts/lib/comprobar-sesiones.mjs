#!/usr/bin/env node
// Comprueba, sin esperar a que la persona haga nada, si la ventana del navegador (puerto CDP de usuario.json)
// tiene sesión en la intranet de la web (eris.urjc.es) y en OneDrive. Lo usa comprobar.sh.
//
// Uso: node comprobar-sesiones.mjs <usuario.json> <slugCMS|-> <eris|onedrive>...
//
// Imprime una línea por comprobación: «OK …», «FALTA …» o «AVISO …». Si falta iniciar sesión, deja esa pestaña
// abierta y al frente, en la pantalla de login, para que la persona entre; si no, cierra lo que ha abierto.

import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(path.join(process.env.PLAYWRIGHT_CORE_DIR || '.', 'x.js'));
const { chromium } = require('playwright-core');

const ESPERA_MS = 20000;
const LOGIN = /identifica\.urjc\.es|login\.microsoftonline\.com/;

async function esperar(page, cond) {
  const limite = Date.now() + ESPERA_MS;
  while (Date.now() < limite) {
    const r = await cond().catch(() => null);
    if (r) return r;
    await page.waitForTimeout(1000);
  }
  return null;
}

async function comprobarEris(ctx, slug) {
  const page = await ctx.newPage();
  try {
    await page.goto(`https://eris.urjc.es/${slug}`, { waitUntil: 'domcontentloaded', timeout: 20000 });
  } catch (e) {
    await page.close();
    return /ERR_NAME_NOT_RESOLVED|ERR_CONNECTION|ERR_TIMED_OUT|Timeout/.test(e.message)
      ? 'FALTA vpn: eris.urjc.es no responde; conecta la VPN de la Universidad'
      : `FALTA web: no se puede abrir eris.urjc.es (${e.message.split('\n')[0]})`;
  }
  const [popup] = await Promise.all([
    ctx.waitForEvent('page', { timeout: 5000 }).catch(() => null),
    page.getByRole('link', { name: /^intranet$/i }).first().click(),
  ]);
  const p = popup || page;
  const estado = await esperar(p, async () => {
    if (/\/intranet-inicio/.test(p.url())) return 'ok';
    const texto = await p.locator('body').innerText();
    if (/Permisos inadecuados/i.test(texto)) return 'permisos';
    if (LOGIN.test(p.url()) && /Credenciales|Iniciar sesión|Sign in|Contraseña|Password/i.test(texto)) return 'login';
    // Formulario de login propio de Joomla en eris (cuando el SSO no entra solo): «Por favor, identifíquese primero».
    if (/eris\.urjc\.es\/login/.test(p.url()) && await p.locator('form[action*="task=user.login"] input[name=password]').count()) return 'login';
    return null;
  });
  if (estado === 'ok') {
    if (popup) await popup.close();
    await page.close();
    return 'OK sesión en la intranet de la web (eris.urjc.es)';
  }
  if (popup) await page.close();
  if (estado === 'login') {
    await p.bringToFront();
    return 'FALTA sesión en la intranet: inicia sesión en la ventana del navegador (está en la pantalla de login)';
  }
  if (estado === 'permisos') return 'FALTA permisos: la cuenta de este navegador no es editora de la web («Permisos inadecuados»)';
  return `AVISO intranet: no se ha podido confirmar la sesión (se quedó en ${p.url()})`;
}

async function comprobarOneDrive(ctx, sitio) {
  const page = await ctx.newPage();
  try {
    await page.goto(`${sitio.replace(/\/$/, '')}/my`, { waitUntil: 'domcontentloaded', timeout: 20000 });
  } catch (e) {
    await page.close();
    return `FALTA onedrive: no se puede abrir ${sitio} (${e.message.split('\n')[0]})`;
  }
  const estado = await esperar(page, async () => {
    if (await page.evaluate(() => !!window._spPageContextInfo?.webAbsoluteUrl)) return 'ok';
    if (LOGIN.test(page.url())) return 'login';
    return null;
  });
  if (estado === 'ok') {
    await page.close();
    return 'OK sesión en OneDrive';
  }
  if (estado === 'login') {
    await page.bringToFront();
    return 'FALTA sesión en OneDrive: inicia sesión en la ventana del navegador (está en la pantalla de login)';
  }
  return `AVISO onedrive: no se ha podido confirmar la sesión (se quedó en ${page.url()})`;
}

const [usuarioPath, slug, ...que] = process.argv.slice(2);
const usuario = JSON.parse(fs.readFileSync(usuarioPath, 'utf8'));
const browser = await chromium.connectOverCDP(`http://localhost:${usuario.navegador.puerto}`);
const ctx = browser.contexts()[0];
for (const q of que) {
  if (q === 'eris') console.log(slug && slug !== '-' ? await comprobarEris(ctx, slug) : 'AVISO intranet: sin Escuela configurada, no se comprueba');
  if (q === 'onedrive') console.log(await comprobarOneDrive(ctx, usuario.onedrive?.sitio || 'https://urjc-my.sharepoint.com'));
}
process.exit(0);
