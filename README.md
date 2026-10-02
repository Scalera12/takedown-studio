# Takedown Studio · site web

Site de **Takedown Studio**, agence de branding en vêtements et produits
personnalisés à Bromont. Mandat Scalera SCA-2026-059 : 12 pages.

## Structure

| Chemin | Quoi |
| --- | --- |
| `construire-site.py` | Génère TOUT le site dans `site/` : pages, SEO, JSON-LD, sitemap, robots, icônes |
| `statique/site.css` | La feuille de style commune (direction B2, tout carré) |
| `statique/site.js` | Menu cell, carrousel, quotes, filtres des réalisations, formulaire |
| `statique/img/` | Logo et dessins en PNG transparent (tirés de captures, vectoriels à recevoir) |
| `site/` | Le site construit (ne pas éditer à la main, il est écrasé) |
| `serveur-local.py` | Aperçu local qui sert `/services/broderie` comme Cloudflare le fera |
| `../contenu/texte-1-plan-de-contenu.md` | Le plan de contenu du client, source des textes |

## Travailler

```sh
python3 construire-site.py      # reconstruit site/
python3 serveur-local.py 8766   # http://localhost:8766
```

Ajouter `?apercu` à une adresse coupe les animations d'apparition (utile pour les captures).

## Aperçu en ligne

Chaque push sur `main` reconstruit le site et le publie sur GitHub Pages
(`.github/workflows/pages.yml`), sous `/takedown-studio/`, bloqué pour Google.
`marque/` garde les originaux du logo et des dessins, `contenu/` le plan de contenu.

## Règles du client

- Fond noir, **aucun coin arrondi**.
- Le header de l'accueil est celui de la maquette B v1 : on n'y touche pas.
- Tutoiement partout, aucun tiret cadratin (le script refuse de construire s'il en trouve un).
- Aucun minimum, délai ni garantie affiché avant confirmation écrite de Takedown.

## À faire avant la mise en ligne

- [ ] Domaine final (`BASE` dans le script, mis à `https://takedownstudio.com` en attendant).
- [ ] Brancher `/api/soumission` : Worker Cloudflare, fichiers dans R2, courriel à Takedown + copie au client.
- [ ] Vraies photos, classées par service, avec légendes et textes alternatifs.
- [ ] Logo en vectoriel.
- [ ] Valider les 3 services de l'étape 15 (`AFFICHER_EXTRAS`).
- [ ] Informations commerciales de l'étape 20.
