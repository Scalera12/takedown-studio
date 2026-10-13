# Worker du formulaire de soumission · Takedown Studio

Reçoit le formulaire de `/contact` (multipart, fichiers joints), garde les fichiers,
envoie un courriel à l'atelier avec toutes les infos et des liens de téléchargement signés.

- Essai : `https://takedown-soumission.jack-mobile.workers.dev/api/soumission`
  (le sous-domaine workers.dev du compte Scalera s'appelle « jack-mobile » : le renommer casserait Jack Mobile, on garde)
- Compte Cloudflare : info@scalera.ca (`66af920c9f23ce05fd9c829f3191788e`, épinglé dans `wrangler.jsonc`)
- Déployer : `./deployer.sh` (refuse de partir si le compte n'est pas Scalera)

## Ce qu'il fait

| Quoi | Comment |
| --- | --- |
| Origines permises (CORS) | takedownstudio.com, www, scalera12.github.io, localhost:8766 ; toute autre origine = 403 |
| Champs requis | nom, courriel valide, service (slug connu), produit, quantite, date, description ; sinon 400 + liste `champs` |
| Champ piège `site_web` | rempli = 200 `{ok:true}` sans rien garder ni envoyer |
| Limite de débit | 5 envois par minute par IP (liaison Rate Limiting) + 5 par 10 minutes (compteur KV) ; sinon 429 |
| Fichiers | max 8, 10 Mo chacun, 25 Mo en tout ; extensions ai eps pdf svg png jpg jpeg webp heic psd ; sinon 413 / 415 |
| Stockage | KV `takedown-fichiers` (180 jours). Passe à R2 tout seul dès que la liaison `FICHIERS_R2` existe |
| Liens de fichiers | `/f/<id>/<n>?t=<HMAC>` servis par le Worker, jeton signé avec le secret `SIGNATURE_SECRET` |
| Sauvegarde | chaque soumission est aussi gardée en KV `takedown-soumissions` (`soumission:<id>`, 180 jours), même si le courriel ne part pas |
| Sans JavaScript | `Accept: text/html` = redirection 303 vers `SITE/merci` (ou `SITE/contact?erreur=...`) |
| Copie au client | seulement si la case est cochée ET `COPIE_CLIENT = "oui"` |

## Envoi du courriel : à brancher (décision d'Alex)

Aucun service d'envoi n'existe encore chez Scalera (Jack Mobile passe par GHL, pas par courriel),
et les options Cloudflare ne marchent pas ici :
- Email Routing / `send_email` exige que la zone soit sur Cloudflare et remplace les MX : takedownstudio.com est chez Squarespace avec Google Workspace, on n'y touche pas.
- R2 n'est pas activé sur le compte (Cloudflare demande une carte au dossier pour l'activer) : fichiers en KV en attendant.

**Recommandé : Resend, forfait gratuit** (3 000 courriels/mois, 100/jour, aucune carte).
1. Alex crée le compte Resend avec info@scalera.ca et une clé d'API « Sending access ».
2. Poser la clé (elle reste chez Cloudflare, jamais dans le dépôt) :
   ```sh
   cd ~/Scalera/Clients/takedown-studio/site-web/worker-soumission
   npx wrangler@4 secret put RESEND_API_KEY
   ```
   Tant que le domaine n'est pas vérifié, l'expéditeur `onboarding@resend.dev` peut seulement écrire
   au courriel du compte Resend (info@scalera.ca) : c'est exactement la config d'essai actuelle.
   Test : remplir le formulaire de l'aperçu, la réponse doit contenir `"envoi":"envoye"`.
3. Pour la production, vérifier le domaine dans Resend (Domains → Add → `takedownstudio.com`, région us-east-1).
   Resend donne des enregistrements DKIM (TXT `resend._domainkey`) et SPF/retour (MX + TXT sur le sous-domaine `send`).
   Les ajouter dans Squarespace Domains (compte du client, code par courriel). **Aucun changement aux MX de la racine (Google).**

## Mise en production (avec l'OK d'Alex)

1. Domaine vérifié dans Resend (étape 3 ci-dessus).
2. Dans `wrangler.jsonc`, remplacer les vars :
   ```jsonc
   "DESTINATAIRE": "info@takedownstudio.com",
   "COPIE_CLIENT": "oui",
   "EXPEDITEUR": "Site Takedown Studio <site@takedownstudio.com>",
   "SITE": "https://takedownstudio.com"
   ```
3. Redéployer : `./deployer.sh`
4. Faire UN envoi réel de test avec l'accord du client (ou garder DESTINATAIRE sur info@scalera.ca le temps d'un dernier essai).
5. Facultatif : activer R2 sur le compte Scalera, créer le bucket puis décommenter `r2_buckets` dans `wrangler.jsonc` :
   ```sh
   npx wrangler@4 r2 bucket create takedown-soumissions
   ```

## Secrets

- `SIGNATURE_SECRET` : posé (valeur aussi dans `.secrets.local`, ignoré par git). Le changer invalide les anciens liens.
- `RESEND_API_KEY` : à poser (voir plus haut).
