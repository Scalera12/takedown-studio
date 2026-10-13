// Worker « takedown-soumission » : reçoit le formulaire de soumission du site
// de Takedown Studio (page /contact), garde les fichiers joints et envoie un
// courriel à l'atelier avec toutes les infos et des liens de téléchargement.
//
// Routes
//   POST /api/soumission        le formulaire (multipart/form-data)
//   GET  /f/<id>/<n>?t=<sig>    télécharge le fichier n de la soumission <id>
//   GET  /                      petit état de santé (aucune donnée)
//
// Stockage : bucket R2 « takedown-soumissions » (liaison FICHIERS_R2) s'il est
// branché, sinon KV (liaison FICHIERS_KV). R2 n'est pas encore activé sur le
// compte Scalera (2026-10-13), donc l'essai roule sur KV.
//
// Envoi du courriel : Resend (clé dans le secret RESEND_API_KEY). Sans clé,
// la soumission est quand même gardée en KV (soumission:<id>) et la réponse
// indique envoi « non-configure ».

const SERVICES = {
  'je-sais-pas': 'Je ne sais pas encore',
  'vetements-personnalises': 'Vêtements personnalisés',
  'broderie': 'Broderie',
  'serigraphie': 'Sérigraphie',
  'impression-dtf': 'Impression numérique DTF',
  'casquettes-tuques': 'Casquettes et tuques personnalisées',
  'patches-ecussons': 'Patches et écussons',
  'autocollants': 'Autocollants personnalisés',
  'vetements-sport-sublimation': 'Vêtements de sport et sublimation',
  'produits-sur-mesure': 'Produits sur mesure',
};

const ORIGINES = [
  'https://takedownstudio.com',
  'https://www.takedownstudio.com',
  'https://scalera12.github.io',
  'http://localhost:8766',
];

const EXTENSIONS = ['ai', 'eps', 'pdf', 'svg', 'png', 'jpg', 'jpeg', 'webp', 'heic', 'psd'];
const MAX_FICHIER = 10 * 1024 * 1024;   // 10 Mo par fichier
const MAX_TOTAL = 25 * 1024 * 1024;     // 25 Mo en tout
const MAX_FICHIERS = 8;
const LIMITE_ENVOIS = 5;                // par adresse IP...
const FENETRE = 600;                    // ...par tranche de 10 minutes
const CONSERVATION = 180 * 24 * 3600;   // fichiers et soumissions gardés 180 jours (KV)

const REQUIS = {
  nom: 'Nom',
  courriel: 'Courriel',
  service: 'Service recherché',
  produit: 'Produit recherché',
  quantite: 'Quantité approximative',
  date: 'Date souhaitée',
  description: 'Description du projet',
};

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const origine = req.headers.get('Origin') || '';
    const cors = enTetesCors(origine);

    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });

    if (url.pathname === '/api/soumission' || url.pathname === '/api/soumission/') {
      if (req.method !== 'POST') return json({ ok: false, erreur: 'methode' }, 405, cors);
      try {
        return await soumission(req, env, ctx, cors, origine);
      } catch (e) {
        console.error('soumission', e && e.stack || e);
        return repondre(req, env, { ok: false, erreur: 'serveur' }, 500, cors);
      }
    }

    const m = url.pathname.match(/^\/f\/([a-f0-9-]{36})\/(\d{1,2})$/);
    if (m && req.method === 'GET') return telecharger(env, m[1], Number(m[2]), url.searchParams.get('t') || '');

    if (url.pathname === '/') return new Response('takedown-soumission ok\n', { headers: { 'content-type': 'text/plain; charset=utf-8' } });
    return new Response('Introuvable', { status: 404 });
  },
};

// ------------------------------------------------------------------ formulaire
async function soumission(req, env, ctx, cors, origine) {
  // Un navigateur envoie toujours Origin sur un POST : on refuse les sites inconnus.
  if (origine && !ORIGINES.includes(origine)) return json({ ok: false, erreur: 'origine' }, 403, cors);

  const type = req.headers.get('content-type') || '';
  if (!type.includes('multipart/form-data') && !type.includes('application/x-www-form-urlencoded')) {
    return repondre(req, env, { ok: false, erreur: 'format' }, 415, cors);
  }
  const longueur = Number(req.headers.get('content-length') || 0);
  if (longueur > MAX_TOTAL + 1024 * 1024) return repondre(req, env, { ok: false, erreur: 'trop-gros' }, 413, cors);

  // Limite de débit par IP
  const ip = req.headers.get('cf-connecting-ip') || 'inconnue';
  if (await tropDEnvois(env, ip)) return repondre(req, env, { ok: false, erreur: 'trop-d-envois' }, 429, cors);

  const fd = await req.formData();
  const val = (k) => String(fd.get(k) || '').trim().slice(0, k === 'description' ? 5000 : 300);

  // Champ piège : un robot le remplit, une personne le voit pas. On fait semblant que ça a marché.
  if (val('site_web')) return repondre(req, env, { ok: true }, 200, cors);

  const d = {};
  for (const k of ['nom', 'entreprise', 'courriel', 'telephone', 'service', 'produit', 'quantite', 'date', 'budget', 'description', 'source', 'copie', 'page']) d[k] = val(k);

  const manquants = Object.keys(REQUIS).filter((k) => !d[k]);
  if (manquants.length) return repondre(req, env, { ok: false, erreur: 'champs', champs: manquants }, 400, cors);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.courriel)) return repondre(req, env, { ok: false, erreur: 'courriel', champs: ['courriel'] }, 400, cors);
  if (!SERVICES[d.service]) return repondre(req, env, { ok: false, erreur: 'service', champs: ['service'] }, 400, cors);

  // Fichiers
  const fichiers = fd.getAll('fichiers').filter((f) => f && typeof f === 'object' && f.size > 0);
  if (fichiers.length > MAX_FICHIERS) return repondre(req, env, { ok: false, erreur: 'trop-de-fichiers', max: MAX_FICHIERS }, 413, cors);
  let total = 0;
  for (const f of fichiers) {
    const ext = (f.name.split('.').pop() || '').toLowerCase();
    if (!EXTENSIONS.includes(ext)) return repondre(req, env, { ok: false, erreur: 'type-fichier', fichier: f.name }, 415, cors);
    if (f.size > MAX_FICHIER) return repondre(req, env, { ok: false, erreur: 'fichier-trop-gros', fichier: f.name, max: '10 Mo' }, 413, cors);
    total += f.size;
  }
  if (total > MAX_TOTAL) return repondre(req, env, { ok: false, erreur: 'trop-gros', max: '25 Mo' }, 413, cors);

  const id = crypto.randomUUID();
  const base = new URL(req.url).origin;
  const liens = [];
  for (let i = 0; i < fichiers.length; i++) {
    const f = fichiers[i];
    const nom = nettoyerNom(f.name);
    const donnees = await f.arrayBuffer();
    await stocker(env, `${id}/${i}`, donnees, { nom, type: f.type || 'application/octet-stream', taille: f.size });
    liens.push({ nom, taille: f.size, url: `${base}/f/${id}/${i}?t=${await signer(env, `${id}/${i}`)}` });
  }

  const courriel = composer(d, liens, id);
  const fiche = { id, recu: new Date().toISOString(), ip, ...d, service_nom: SERVICES[d.service], fichiers: liens };
  if (env.SOUMISSIONS) ctx.waitUntil(env.SOUMISSIONS.put(`soumission:${id}`, JSON.stringify(fiche), { expirationTtl: CONSERVATION }));

  const envoi = await envoyer(env, {
    a: env.DESTINATAIRE,
    sujet: courriel.sujet,
    html: courriel.html,
    texte: courriel.texte,
    repondreA: d.courriel,
  });
  if (envoi === 'echec') return repondre(req, env, { ok: false, erreur: 'envoi' }, 502, cors);

  // Copie au client (COPIE_CLIENT = "oui" en production seulement)
  if (d.copie === 'oui' && env.COPIE_CLIENT === 'oui' && envoi === 'envoye') {
    const copie = composerCopie(d);
    ctx.waitUntil(envoyer(env, { a: d.courriel, sujet: copie.sujet, html: copie.html, texte: copie.texte, repondreA: env.DESTINATAIRE }));
  }

  return repondre(req, env, { ok: true, id, envoi }, 200, cors);
}

// ------------------------------------------------------------------ stockage
async function stocker(env, cle, donnees, meta) {
  if (env.FICHIERS_R2) {
    await env.FICHIERS_R2.put(cle, donnees, { httpMetadata: { contentType: meta.type }, customMetadata: { nom: meta.nom } });
  } else {
    await env.FICHIERS_KV.put(`fichier:${cle}`, donnees, { metadata: meta, expirationTtl: CONSERVATION });
  }
}

async function telecharger(env, id, n, t) {
  const cle = `${id}/${n}`;
  if (!t || !(await egal(t, await signer(env, cle)))) return new Response('Lien invalide', { status: 403 });
  let corps, nom, type;
  if (env.FICHIERS_R2) {
    const o = await env.FICHIERS_R2.get(cle);
    if (!o) return new Response('Fichier introuvable ou expiré', { status: 404 });
    corps = o.body; nom = o.customMetadata?.nom || 'fichier'; type = o.httpMetadata?.contentType;
  } else {
    const o = await env.FICHIERS_KV.getWithMetadata(`fichier:${cle}`, 'arrayBuffer');
    if (!o.value) return new Response('Fichier introuvable ou expiré', { status: 404 });
    corps = o.value; nom = o.metadata?.nom || 'fichier'; type = o.metadata?.type;
  }
  return new Response(corps, {
    headers: {
      'content-type': type || 'application/octet-stream',
      'content-disposition': `attachment; filename="${nom.replace(/"/g, '')}"; filename*=UTF-8''${encodeURIComponent(nom)}`,
      'cache-control': 'private, no-store',
      'x-content-type-options': 'nosniff',
    },
  });
}

// ------------------------------------------------------------------ envoi
// Retourne 'envoye', 'non-configure' ou 'echec'.
async function envoyer(env, { a, sujet, html, texte, repondreA }) {
  if (!env.RESEND_API_KEY) {
    console.log('ENVOI NON CONFIGURÉ (aucune clé Resend) :', sujet, '→', a);
    return 'non-configure';
  }
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: env.EXPEDITEUR, to: [a], subject: sujet, html, text: texte, reply_to: repondreA }),
  });
  if (!r.ok) {
    console.error('Resend', r.status, await r.text());
    return 'echec';
  }
  return 'envoye';
}

// ------------------------------------------------------------------ courriels
function composer(d, liens, id) {
  const service = SERVICES[d.service];
  const lignes = [
    ['Nom', d.nom], ['Entreprise', d.entreprise], ['Courriel', d.courriel], ['Téléphone', d.telephone],
    ['Service', service], ['Produit', d.produit], ['Quantité', d.quantite], ['Date souhaitée', d.date],
    ['Budget', d.budget], ['Nous a connus par', d.source], ['Copie demandée', d.copie === 'oui' ? 'Oui' : 'Non'],
  ].filter(([, v]) => v);
  const sujet = `Nouvelle soumission · ${service} · ${d.nom}${d.entreprise ? ' (' + d.entreprise + ')' : ''}`;

  const td = 'padding:8px 12px;border-bottom:1px solid #e5e5e5;vertical-align:top;font:14px/1.45 Arial,Helvetica,sans-serif';
  const tableau = lignes.map(([k, v]) => `<tr><td style="${td};color:#666;width:150px">${esc(k)}</td><td style="${td};color:#111">${k === 'Courriel' ? `<a href="mailto:${esc(v)}">${esc(v)}</a>` : k === 'Téléphone' ? `<a href="tel:${esc(v.replace(/[^\d+]/g, ''))}">${esc(v)}</a>` : esc(v)}</td></tr>`).join('');
  const fichiersHtml = liens.length
    ? `<ul style="padding-left:18px;margin:8px 0">${liens.map((l) => `<li style="margin:4px 0;font:14px Arial,Helvetica,sans-serif"><a href="${l.url}">${esc(l.nom)}</a> <span style="color:#888">(${taille(l.taille)})</span></li>`).join('')}</ul><p style="font:12px Arial,Helvetica,sans-serif;color:#888">Liens valides 180 jours. Télécharge les fichiers que tu veux garder.</p>`
    : '<p style="font:14px Arial,Helvetica,sans-serif;color:#666">Aucun fichier joint.</p>';

  const html = `<!doctype html><html lang="fr-CA"><body style="margin:0;background:#f4f4f4;padding:24px">
<table role="presentation" width="100%" style="max-width:640px;margin:0 auto;background:#fff;border:1px solid #ddd;border-collapse:collapse">
<tr><td style="background:#000;color:#fff;padding:18px 20px;font:bold 16px Arial,Helvetica,sans-serif;letter-spacing:.04em">TAKEDOWN STUDIO · NOUVELLE SOUMISSION</td></tr>
<tr><td style="padding:20px">
<p style="font:15px/1.5 Arial,Helvetica,sans-serif;margin:0 0 14px">Une demande de soumission vient d’arriver par le site. Réponds directement à ce courriel pour écrire à ${esc(d.nom)}.</p>
<table role="presentation" width="100%" style="border-collapse:collapse">${tableau}</table>
<h3 style="font:bold 14px Arial,Helvetica,sans-serif;margin:22px 0 6px;text-transform:uppercase;letter-spacing:.05em">Description du projet</h3>
<p style="font:14px/1.55 Arial,Helvetica,sans-serif;white-space:pre-wrap;margin:0;background:#f7f7f7;padding:12px">${esc(d.description)}</p>
<h3 style="font:bold 14px Arial,Helvetica,sans-serif;margin:22px 0 6px;text-transform:uppercase;letter-spacing:.05em">Fichiers</h3>
${fichiersHtml}
<p style="font:11px Arial,Helvetica,sans-serif;color:#aaa;margin-top:24px">Réf. ${id}${d.page ? ' · page d’origine : ' + esc(d.page) : ''}</p>
</td></tr></table></body></html>`;

  const texte = `NOUVELLE SOUMISSION · TAKEDOWN STUDIO\n\n${lignes.map(([k, v]) => `${k} : ${v}`).join('\n')}\n\nDescription du projet :\n${d.description}\n\nFichiers :\n${liens.length ? liens.map((l) => `- ${l.nom} (${taille(l.taille)}) : ${l.url}`).join('\n') + '\n(liens valides 180 jours)' : 'Aucun fichier joint.'}\n\nRéf. ${id}\n`;
  return { sujet, html, texte };
}

function composerCopie(d) {
  const sujet = 'Ta demande de soumission chez Takedown Studio';
  const texte = `Salut ${d.nom},\n\nMerci pour ta demande. Voici ce que tu nous as envoyé :\n\nService : ${SERVICES[d.service]}\nProduit : ${d.produit}\nQuantité : ${d.quantite}\nDate souhaitée : ${d.date}\n\n${d.description}\n\nOn regarde ça et on te revient par courriel ou par téléphone.\n\nTakedown Studio\n50, chemin de Gaspé, bloc C, local 5, Bromont\n579 488-0321 · info@takedownstudio.com\n`;
  const html = `<!doctype html><html lang="fr-CA"><body style="font:15px/1.55 Arial,Helvetica,sans-serif;color:#111">${esc(texte).replace(/\n/g, '<br>')}</body></html>`;
  return { sujet, html, texte };
}

// ------------------------------------------------------------------ outils
function enTetesCors(origine) {
  const h = { 'Vary': 'Origin' };
  if (ORIGINES.includes(origine)) {
    h['Access-Control-Allow-Origin'] = origine;
    h['Access-Control-Allow-Methods'] = 'POST, OPTIONS';
    h['Access-Control-Allow-Headers'] = 'Content-Type';
    h['Access-Control-Max-Age'] = '86400';
  }
  return h;
}

function json(obj, statut, h = {}) {
  return new Response(JSON.stringify(obj), { status: statut, headers: { ...h, 'content-type': 'application/json; charset=utf-8' } });
}

// Formulaire envoyé sans JavaScript (le navigateur demande du HTML) : on redirige vers une page du site.
function repondre(req, env, obj, statut, h) {
  const accepte = req.headers.get('accept') || '';
  if (accepte.includes('text/html')) {
    const site = env.SITE || 'https://takedownstudio.com';
    const cible = obj.ok ? `${site}/merci` : `${site}/contact?erreur=${encodeURIComponent(obj.erreur || 'envoi')}`;
    return new Response(null, { status: 303, headers: { ...h, Location: cible } });
  }
  return json(obj, statut, h);
}

// Limite de débit : liaison Rate Limiting de Cloudflare (rafales, 5 par minute) puis
// compteur KV sur 10 minutes. (La Cache API ne marche pas sur workers.dev.)
async function tropDEnvois(env, ip) {
  if (env.LIMITE) {
    const { success } = await env.LIMITE.limit({ key: ip });
    if (!success) return true;
  }
  if (!env.SOUMISSIONS) return false;
  const cle = `limite:${ip}:${Math.floor(Date.now() / 1000 / FENETRE)}`;
  const n = Number(await env.SOUMISSIONS.get(cle)) || 0;
  if (n >= LIMITE_ENVOIS) return true;
  await env.SOUMISSIONS.put(cle, String(n + 1), { expirationTtl: FENETRE + 60 });
  return false;
}

async function signer(env, texte) {
  const cle = await crypto.subtle.importKey('raw', new TextEncoder().encode(env.SIGNATURE_SECRET), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', cle, new TextEncoder().encode(texte));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, '0')).join('').slice(0, 40);
}

async function egal(a, b) {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

function nettoyerNom(n) {
  return String(n || 'fichier').replace(/[\\/\x00-\x1f]/g, '_').slice(-120);
}

function taille(n) {
  return n > 1048576 ? (n / 1048576).toFixed(1).replace('.', ',') + ' Mo' : Math.max(1, Math.round(n / 1024)) + ' Ko';
}

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
