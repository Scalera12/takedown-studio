# Lancement · site Takedown Studio (SCA-2026-059)

État au 2026-10-13, branche `dessins-services` (pas poussée). Les 12 pages du contrat sont faites,
plus `/merci` (confirmation du formulaire, hors sitemap) et la 404.

## 1. Ce qui manque du client

| Quoi | Pourquoi | Où ça va |
| --- | --- | --- |
| **Photos de réalisations en bonne résolution** (15 à 25, idéalement 3 par service) | Instagram sans connexion ne montre que 12 publications, en 640 px max, surtout des couvertures de reels avec le bouton lecture. Inutilisable sur le site. Leur demander un dossier (Drive / WeTransfer) des originaux, ou un OK d'Alex pour une session Instagram connectée. | Déposer les JPG dans `statique/img/photos/`, une ligne par photo dans `realisations.csv`, relancer la construction. Les pages de services les prennent seules. |
| Autorisation d'utiliser les photos de projets clients | Étape 2 du plan de contenu | Confirmation écrite (courriel ou texto) |
| Logo en vectoriel (AI / SVG / PDF) | Le logo et les dessins sont tirés de captures | `marque/` puis `convertir-dessins.py` |
| Régions desservies | Étape 20 ; le schema dit seulement Bromont + Estrie | `entreprise_ld()` dans `construire-site.py` |
| Heures / disponibilités | Étape 2 ; rien d'affiché pour l'instant | ajouter `openingHours` au schema + pied de page |
| Code postal exact | Le site dit **J2L 2N8** (donné par le client), OpenStreetMap donne J2L 1C4 pour le 50 ch. de Gaspé (CLSC dans le même complexe). À confirmer avec Postes Canada / le client. | `ENTREPRISE['cp']` |
| Validation des 3 services de l'étape 15 (sublimation, sur mesure, fiches techniques) | Affichés sur la page Vêtements (`AFFICHER_EXTRAS = True`) | mettre `False` si refusés |
| Informations commerciales de l'étape 20 (minimums, délais, livraison, garanties) | Rien n'est affiché tant que Takedown ne confirme pas par écrit | textes des services |
| Lien Facebook, s'il existe | sameAs du schema | `ENTREPRISE['reseaux']` |

**Version anglaise : PAS faite.** Promise par Alex au client le 2026-10-07, jamais cadrée. Pas dans le contrat SCA-2026-059 (12 pages en français). À décider par Alex : hors contrat (85 $/h) ou geste commercial, et la structure (`/en/...` avec hreflang).

## 2. Formulaire de soumission

Branché sur le Worker d'essai `https://takedown-soumission.jack-mobile.workers.dev/api/soumission`
(détails et tests : `worker-soumission/README.md`). Il valide, bloque le pourriel, garde les fichiers et la demande en KV.

Avant la mise en ligne, il faut que le courriel parte vraiment :
1. Alex crée un compte **Resend gratuit** (aucune carte) avec info@scalera.ca et pose la clé :
   `cd ~/Scalera/Clients/takedown-studio/site-web/worker-soumission && npx wrangler@4 secret put RESEND_API_KEY`
2. Test vers info@scalera.ca (config actuelle) : remplir `/contact` de l'aperçu, la réponse doit dire `"envoi":"envoye"`.
3. Vérifier takedownstudio.com dans Resend : ajouter dans Squarespace Domains les enregistrements DKIM (TXT `resend._domainkey`) et ceux du sous-domaine `send` (MX + TXT). **Ne pas toucher aux MX de la racine (Google Workspace).** Squarespace envoie un code au Hotmail du client à chaque modification.
4. Dans `worker-soumission/wrangler.jsonc` : `DESTINATAIRE` = `info@takedownstudio.com`, `COPIE_CLIENT` = `oui`, `EXPEDITEUR` = `Site Takedown Studio <site@takedownstudio.com>`, puis `./deployer.sh`.
5. Facultatif : activer R2 sur le compte Scalera (demande une carte) pour sortir les fichiers de KV.

À noter : le helper `cf` n'a pas encore de jeton « scalera » (`cf ajouter scalera`) ; `deployer.sh` vérifie quand même le compte avant de partir.

## 3. Mettre le vrai site sur takedownstudio.com

Le DNS pointe DÉJÀ sur GitHub Pages (A @ 185.199.108-111.153, CNAME www → scalera12.github.io, MX Google intacts).
**Aucun changement DNS.** On déplace seulement le domaine personnalisé d'un dépôt GitHub à l'autre :
`Scalera12/takedown-construction` (page « en construction », en ligne) → `Scalera12/takedown-studio` (le vrai site).

```sh
# 0. compte GitHub d'Alex
gh auth switch -u Scalera12

# 1. le site sur main (avance rapide), avec la variable qui le sert à la racine et indexable
cd ~/Scalera/Clients/takedown-studio/site-web
git checkout main && git merge --ff-only dessins-services
gh variable set EN_LIGNE --body oui -R Scalera12/takedown-studio
git push origin main
gh run watch -R Scalera12/takedown-studio      # attendre la fin du déploiement Pages

# 2. libérer le domaine sur le dépôt « en construction »
gh api -X PUT repos/Scalera12/takedown-construction/pages --input - <<< '{"cname":null}'

# 3. le poser sur le vrai site
gh api -X PUT repos/Scalera12/takedown-studio/pages --input - <<< '{"cname":"takedownstudio.com"}'

# 4. quand le certificat est émis (quelques minutes) : forcer HTTPS
gh api repos/Scalera12/takedown-studio/pages --jq '.https_certificate.state'   # attendre « approved »
gh api -X PUT repos/Scalera12/takedown-studio/pages --input - <<< '{"https_enforced":true}'
```

Vérifier ensuite : `https://takedownstudio.com/`, `/services/broderie`, `/contact?service=patches-ecussons`,
`https://www.takedownstudio.com` (doit rediriger vers la racine), `/robots.txt`, `/sitemap.xml`, et qu'aucune page n'a `noindex` (sauf /merci et la 404).

Retour en arrière (si besoin) : remettre le cname sur `takedown-construction` et l'enlever de `takedown-studio` (mêmes commandes, inversées).
Tant que `EN_LIGNE=oui`, l'aperçu `scalera12.github.io/takedown-studio/` n'existe plus : c'est voulu.

Après la mise en ligne :
- Google Search Console : ajouter takedownstudio.com, soumettre `https://takedownstudio.com/sitemap.xml`.
- Fiche Google du studio : mettre le lien du site (et vers `/contact` pour les soumissions).
- Mettre le lien du site dans la bio Instagram si ce n'est pas déjà fait.

## 4. Vérifié le 2026-10-13

- 0 lien mort (81 adresses testées), 0 image sans `alt`, 1 seul `h1` par page, titres et descriptions sous ~65 / 155 caractères.
- Bureau 1440 et cell 390 : aucun débordement horizontal, aucune image cassée. Poids des images par page : 22 à 480 Ko sur bureau, 41 à 884 Ko sur cell (accueil).
- Schema `ProfessionalService` (adresse, téléphone, geo, sameAs Instagram), `Service` par page, `BreadcrumbList`, `ItemList` ; Open Graph + image 1200 x 630 ; canonique sur takedownstudio.com.
- Captures : `captures-finition/` (bureau et cell, hauteur d'écran).
