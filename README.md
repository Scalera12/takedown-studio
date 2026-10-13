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
| `convertir-dessins.py` | Dessins du client (`marque/client-2026-10-07-dessins/`) → `statique/img/dessins/*-blanc.png` (blanc sur transparent) |
| `site/` | Le site construit (ne pas éditer à la main, il est écrasé) |
| `serveur-local.py` | Aperçu local qui sert `/services/broderie` comme Cloudflare le fera |
| `../contenu/texte-1-plan-de-contenu.md` | Le plan de contenu du client, source des textes |

## Travailler

```sh
SANS_CONSTRUCTION=1 python3 construire-site.py   # reconstruit site/ sans toucher à ../site-construction
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

## Avant la mise en ligne

Tout est dans `lancement.md` : ce qui manque du client, le branchement du courriel du formulaire
(`worker-soumission/`) et la procédure exacte pour remplacer la page « en construction » sur takedownstudio.com.

Réalisations : une ligne par photo dans `realisations.csv` (photo dans `statique/img/photos/<photo>.jpg`).
