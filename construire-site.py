# -*- coding: utf-8 -*-
"""Construit le site de Takedown Studio dans site/, avec tout le SEO.

Toutes les pages sortent d'ici : on modifie CE fichier puis on le relance,
jamais les pages générées (elles sont écrasées à chaque construction).
Les textes viennent du plan de contenu du client
(../contenu/texte-1-plan-de-contenu.md), au tutoiement, sans tiret cadratin.

Règles fixées par le client (2026-09-30) :
  - direction B2, fond noir, AUCUN coin arrondi ;
  - le header de l'accueil est celui de la maquette B v1, on n'y touche pas ;
  - aucun minimum, délai ni garantie affiché avant confirmation écrite.

Usage : python3 construire-site.py
"""
import io, os, json, shutil, datetime, html as H
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, 'site')
BASE = 'https://takedownstudio.com'   # À CONFIRMER : domaine final du site
AUJ = datetime.date.today().isoformat()
import hashlib
V = hashlib.sha1(open(os.path.join(ICI, 'statique', 'site.js'), 'rb').read()).hexdigest()[:8]   # change dès que le JS change

# Les 3 services de l'étape 15 doivent être validés par Takedown avant la mise en ligne.
AFFICHER_EXTRAS = True

ENTREPRISE = {
    'nom': 'Takedown Studio',
    'tel': '579 488-0321', 'tel_intl': '+15794880321',
    'courriel': 'info@takedownstudio.com',
    'rue': '50, chemin de Gaspé, bloc C, local 5', 'ville': 'Bromont', 'region': 'QC', 'cp': 'J2L 2N8',
}

def e(s):
    return H.escape(s, quote=True)

# ---------------------------------------------------------------- services
SERVICES = [
    dict(slug='vetements-personnalises', nom='Vêtements personnalisés', filtre='vetements', ton='#2e3a47',
         tag='T-shirts, hoodies, polos', court='Les bons vêtements pour ton projet, avec ton logo.',
         texte='T-shirts, hoodies, crewnecks, polos ou manteaux : on t’aide à choisir les bons vêtements pour ton projet. On regarde la coupe, le confort et le budget, puis on ajoute ton logo avec la technique qui convient le mieux. Pour habiller ton équipe ou créer du merch, on te guide du début à la fin.',
         plus='Beaucoup de choix, plusieurs gammes de prix et des vêtements adaptés à l’utilisation que tu veux en faire.',
         prevoir='Les tailles, les couleurs et les stocks varient selon le modèle. Une petite commande coûte généralement plus cher par morceau.',
         exemples=['T-shirts d’entreprise', 'Hoodies de marque', 'Polos brodés', 'Vêtements de travail'],
         bouton='Demander une soumission pour des vêtements personnalisés',
         liens=['broderie', 'serigraphie', 'impression-dtf', 'casquettes-tuques', 'patches-ecussons'],
         seo='Vêtements personnalisés avec ton logo à Bromont | Takedown Studio',
         desc='T-shirts, hoodies, polos et manteaux personnalisés avec ton logo. On t’aide à choisir les vêtements et la technique selon ton budget. Bromont et environs.'),
    dict(slug='broderie', nom='Broderie', filtre='broderie', ton='#3b4634',
         tag='Gros plan · fil et relief', court='Ton logo cousu dans le vêtement, avec du relief.',
         texte='La broderie, c’est ton logo cousu directement dans le vêtement avec du fil. Ça donne du relief et une belle finition. C’est une bonne option pour les casquettes, les tuques, les polos, les crewnecks et les manteaux.',
         plus='Un look soigné, du relief et une bonne durabilité lorsque le vêtement est bien entretenu.',
         prevoir='Les petits textes et les détails très fins peuvent devoir être simplifiés. Un gros logo rempli demande plus de points et coûte plus cher. Certains tissus très minces s’y prêtent moins bien.',
         exemples=['Logo sur la poitrine', 'Casquette brodée', 'Tuque avec broderie', 'Polo brodé', 'Manteau personnalisé'],
         bouton='Demander une soumission pour de la broderie',
         liens=['casquettes-tuques', 'patches-ecussons', 'vetements-personnalises'],
         seo='Broderie personnalisée à Bromont | Takedown Studio',
         desc='Broderie de logo sur casquettes, tuques, polos, crewnecks et manteaux. Un look soigné avec du relief. Demande ta soumission à Takedown Studio, Bromont.'),
    dict(slug='serigraphie', nom='Sérigraphie', filtre='serigraphie', ton='#6b4a2c',
         tag='Écran et encre', court='Un beau rendu qui devient intéressant en quantité.',
         texte='La sérigraphie, c’est une impression à l’encre directement sur le vêtement, à l’aide d’écrans. Chaque couleur demande sa préparation. C’est une bonne option quand tu veux plusieurs morceaux avec le même visuel, surtout si ton design a peu de couleurs.',
         plus='Un beau rendu, une bonne tenue avec un entretien adapté et un prix par morceau qui devient intéressant en quantité.',
         prevoir='La préparation coûte plus cher pour les petites commandes. Le nombre de couleurs et les emplacements d’impression font varier le prix.',
         exemples=['T-shirts d’équipe', 'Merch pour un événement', 'Hoodies imprimés', 'Impression une couleur', 'Impression multicolore'],
         bouton='Demander une soumission pour de la sérigraphie',
         liens=['vetements-personnalises', 'impression-dtf', 'casquettes-tuques'],
         seo='Sérigraphie sur vêtements à Bromont | Takedown Studio',
         desc='Sérigraphie sur t-shirts et hoodies pour ton équipe, ton événement ou ton merch. Un beau rendu à l’encre, intéressant en quantité. Takedown Studio, Bromont.'),
    dict(slug='impression-dtf', nom='Impression numérique DTF', filtre='dtf', ton='#4a3a55',
         tag='Visuel multicolore', court='Plein de couleurs et de détails, même en petite quantité.',
         texte='Le DTF, c’est ton visuel imprimé sur un film, puis transféré sur le vêtement avec une presse à chaleur. C’est pratique pour les petites quantités, les images avec plusieurs couleurs et les dégradés.',
         plus='Beaucoup de couleurs dans le même visuel, une bonne reproduction des détails et une option pratique pour les petits projets.',
         prevoir='L’impression se sent au toucher. Un grand visuel plein peut être plus épais et moins respirant. La qualité du fichier et le respect des consignes de lavage comptent beaucoup.',
         exemples=['T-shirt multicolore', 'Petit lot de vêtements', 'Échantillon avant une plus grosse commande', 'Visuel avec dégradé', 'Logo détaillé'],
         bouton='Demander une soumission pour une impression DTF',
         liens=['vetements-personnalises', 'serigraphie', 'casquettes-tuques'],
         seo='Impression DTF sur vêtements | Takedown Studio',
         desc='Impression numérique DTF sur vêtements : plein de couleurs, des dégradés et des détails, même pour un petit lot. Demande ta soumission à Takedown Studio.'),
    dict(slug='casquettes-tuques', nom='Casquettes et tuques personnalisées', court_nom='Casquettes et tuques', filtre='casquettes-tuques', ton='#2b2d31',
         tag='Dad cap brodée', court='Brodées, avec patch ou imprimées selon le modèle.',
         texte='On t’aide à choisir la bonne casquette ou la bonne tuque selon le style que tu recherches. Ensuite, on regarde comment ajouter ton logo : broderie, patch ou impression lorsque le modèle le permet.',
         plus='Un accessoire facile à porter, un logo bien visible et plusieurs styles pour représenter ta marque.',
         prevoir='L’espace pour le logo est limité. Les coutures, la forme de la casquette et la maille d’une tuque peuvent demander d’adapter le visuel. Les minimums varient selon la méthode choisie.',
         exemples=['Dad caps', 'Casquettes structurées', 'Tuques personnalisées', 'Casquettes brodées', 'Casquettes avec patch'],
         bouton='Demander une soumission pour des casquettes ou des tuques',
         liens=['broderie', 'patches-ecussons', 'vetements-personnalises'],
         seo='Casquettes et tuques personnalisées | Takedown Studio',
         desc='Casquettes et tuques avec ton logo : broderie, patch ou impression selon le modèle. Dad caps, casquettes structurées, tuques. Takedown Studio, Bromont.'),
    dict(slug='patches-ecussons', nom='Patches et écussons', filtre='patches', ton='#5a2f24',
         tag='Patch sur veste', court='Un logo ou un nom en format écusson.',
         texte='Un patch, c’est un écusson personnalisé qu’on ajoute sur une casquette, une chemise, un manteau ou un autre produit compatible. C’est une belle option pour donner un style différent à ton logo ou ajouter un nom sur un vêtement.',
         plus='Un look distinctif, plusieurs possibilités de finition et une bonne option pour les noms ou les logos en format écusson.',
         prevoir='Les petits détails doivent parfois être adaptés au type de patch. La fabrication et l’installation sont deux étapes à prévoir dans le prix et le délai.',
         exemples=['Patch de logo', 'Écusson avec prénom', 'Casquette avec patch', 'Patch thermocollant', 'Patch cousu sur un vêtement'],
         bouton='Demander une soumission pour des patches',
         liens=['casquettes-tuques', 'broderie', 'vetements-personnalises'],
         seo='Patches et écussons personnalisés | Takedown Studio',
         desc='Patches et écussons personnalisés pour casquettes, chemises et manteaux. Ton logo ou un nom en format écusson. Demande ta soumission à Takedown Studio.'),
    dict(slug='autocollants', nom='Autocollants personnalisés', filtre='autocollants', ton='#5c5646',
         tag='Autocollants sur emballage', court='Pour tes emballages, tes commandes et tes événements.',
         texte='On fait produire tes autocollants avec ton logo ou ton visuel. Pour tes emballages, tes commandes ou tes événements, on t’aide à choisir le format et la finition selon l’utilisation prévue.',
         plus='Faciles à distribuer, pratiques pour personnaliser tes emballages et disponibles dans différents formats.',
         prevoir='La dimension, la matière et la finition influencent le prix. Pour l’extérieur, l’eau ou une surface particulière, il faut choisir un matériau et un adhésif adaptés.',
         exemples=['Autocollants de logo', 'Fermeture d’emballage', 'Autocollants remis avec une commande', 'Autocollants pour événement', 'Autocollants résistants à l’extérieur'],
         bouton='Demander une soumission pour des autocollants',
         liens=[],
         seo='Autocollants personnalisés avec ton logo | Takedown Studio',
         desc='Autocollants personnalisés avec ton logo pour tes emballages, tes commandes et tes événements. On t’aide à choisir le format et la finition. Bromont.'),
]
PAR_SLUG = {s['slug']: s for s in SERVICES}
def nom_court(s):
    return s.get('court_nom', s['nom'])

EXTRAS = [
    dict(id='sublimation', val='vetements-sport-sublimation', titre='Vêtements de sport et sublimation',
         texte='Pour ton équipe sportive, on peut t’accompagner dans la commande de jerseys et d’ensembles personnalisés auprès de nos partenaires. La sublimation permet d’intégrer les couleurs et les visuels dans un tissu compatible, souvent en polyester.',
         plus='Beaucoup de liberté dans le design et un motif qui ne forme pas une couche épaisse sur le tissu.',
         prevoir='Les tissus, les modèles, les minimums et les délais dépendent du programme de fabrication. Ce procédé ne convient pas à tous les vêtements.'),
    dict(id='sur-mesure', val='produits-sur-mesure', titre='Produits sur mesure',
         texte='Tu cherches quelque chose qui sort du catalogue habituel? On peut regarder les possibilités avec nos partenaires pour développer un produit à ton image, comme des bas, des sandales ou des accessoires personnalisés.',
         plus='Un produit qui se démarque et davantage de possibilités de personnalisation, selon le fabricant.',
         prevoir='Des minimums souvent plus élevés, des délais plus longs et parfois des frais d’échantillon ou de développement.'),
    dict(id='fiches-techniques', val='je-sais-pas', titre='Fiches techniques et préparation à la production',
         texte='On rassemble les informations nécessaires pour expliquer ton projet au fabricant : dimensions, couleurs, placements et détails de personnalisation. Le but est que tout soit clair avant la production.',
         plus='Moins de zones grises et un document de référence pour le suivi du projet.',
         prevoir='Il faut confirmer les détails du produit. Une fiche technique ne remplace pas un échantillon lorsque celui-ci est nécessaire.'),
]

# Emplacements de réalisations : remplacés par les vraies photos de Takedown.
REALISATIONS = [
    dict(titre='Hoodie personnalisé', produit='Hoodie', tech='Impression DTF', c='vetements dtf', svc='impression-dtf', ton='#1d2126', desc='Hoodie personnalisé avec impression DTF.'),
    dict(titre='Casquette avec logo brodé', produit='Casquette', tech='Broderie', c='broderie casquettes-tuques', svc='broderie', ton='#18191c', desc='Casquette personnalisée avec logo brodé pour une entreprise locale.'),
    dict(titre='T-shirts d’équipe', produit='T-shirt', tech='Sérigraphie', c='vetements serigraphie', svc='serigraphie', ton='#241d16', desc='T-shirts d’équipe imprimés en sérigraphie.'),
    dict(titre='Patch sur une veste', produit='Veste', tech='Patch', c='patches vetements', svc='patches-ecussons', ton='#261714', desc='Patch personnalisé appliqué sur une veste.'),
    dict(titre='Autocollants de logo', produit='Autocollant', tech='Autocollants', c='autocollants', svc='autocollants', ton='#22211b', desc='Autocollants de logo pour emballages.'),
    dict(titre='Tuques personnalisées', produit='Tuque', tech='Broderie', c='broderie casquettes-tuques', svc='casquettes-tuques', ton='#1a1f27', desc='Tuques personnalisées avec broderie.'),
    dict(titre='Polos brodés', produit='Polo', tech='Broderie', c='broderie vetements', svc='broderie', ton='#1f2420', desc='Polos brodés pour une équipe.'),
    dict(titre='Merch d’événement', produit='T-shirt et hoodie', tech='Sérigraphie', c='serigraphie vetements', svc='serigraphie', ton='#221b1b', desc='Merch imprimé en sérigraphie pour un événement.'),
    dict(titre='Casquettes avec patch', produit='Casquette', tech='Patch', c='patches casquettes-tuques', svc='patches-ecussons', ton='#1c1c20', desc='Casquettes structurées avec patch de logo.'),
]
FILTRES = [('tous', 'Tous'), ('vetements', 'Vêtements'), ('broderie', 'Broderie'), ('serigraphie', 'Sérigraphie'),
           ('dtf', 'DTF'), ('casquettes-tuques', 'Casquettes et tuques'), ('patches', 'Patches'), ('autocollants', 'Autocollants')]

CHOIX_SERVICE = [('je-sais-pas', 'Je ne sais pas encore')] + [(s['slug'], s['nom']) for s in SERVICES] + \
                [('vetements-sport-sublimation', 'Vêtements de sport et sublimation'), ('produits-sur-mesure', 'Produits sur mesure')]

DESSINS = ['illustration-pinceau', 'illustration-encre', 'logo-complet-lutteurs']

# ---------------------------------------------------------------- morceaux communs
MENU = [('/', 'Accueil'), ('/agence-branding', 'L’agence'), ('/services', 'Nos services'),
        ('/realisations', 'Réalisations'), ('/contact', 'Contact')]

def soum(slug=None):
    return '/contact' + (f'?service={slug}' if slug else '')

def nav(courant):
    liens = ''.join(
        f'<li><a href="{u}"{" aria-current=\"page\"" if u == courant else ""}>{t}</a></li>' for u, t in MENU)
    mob = ''.join(f'<a href="{u}">{t}</a>' for u, t in MENU)
    return f'''<a class="skip" href="#contenu">Aller au contenu</a>
<header class="nav">
  <div class="wrap">
    <a class="logo" href="/" aria-label="Takedown Studio, accueil"><img src="/assets/img/logo-texte-blanc.png" alt="Takedown Studio" width="130" height="17"></a>
    <nav aria-label="Menu principal"><ul>{liens}</ul></nav>
    <div class="right"><a class="btn btn-w" href="/contact"><span class="lg">Demander une&nbsp;</span>soumission</a><button class="burger" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="menu-m"><span></span><span></span></button></div>
  </div>
</header>
<nav class="menu-m" id="menu-m" aria-label="Menu cellulaire">{mob}<a class="btn btn-w" href="/contact">Demander une soumission</a></nav>'''

def pied(court=False):
    services = ''.join(f'<a href="/services/{s["slug"]}">{nom_court(s)}</a>' for s in SERVICES)
    tete = '' if court else '''<p class="mono" style="color:var(--mute)">Demander une soumission</p>
        <h2 class="x"><span class="ind">On regarde ton</span><br>projet ensemble!</h2>'''
    appel = '' if court else '''<div>
            <p>Envoie-nous ton idée, ton logo et la quantité que tu as en tête. On va te guider pour la suite.</p>
            <a class="btn btn-w" href="/contact">Demander une soumission <span class="arr">→</span></a>
          </div>'''
    return f'''<footer class="foot{' court' if court else ''}">
  <div class="wrap">
    <div class="grid-f">
      <div>
        {tete}
        <div class="lead">
          {appel}
          <div class="cols">
            <div><h4>Services</h4>{services}</div>
            <div><h4>Studio</h4><a href="/agence-branding">L’agence</a><a href="/realisations">Réalisations</a><a href="/contact">Contact</a>
              <h4 style="margin-top:22px">Nous joindre</h4><a href="tel:{ENTREPRISE['tel_intl']}">{ENTREPRISE['tel']}</a><a href="mailto:{ENTREPRISE['courriel']}">{ENTREPRISE['courriel']}</a></div>
          </div>
        </div>
      </div>
    </div>
    <div class="legal">
      <img src="/assets/img/logo-texte-blanc.png" alt="Takedown Studio" width="122" height="16" loading="lazy">
      <span>{ENTREPRISE['rue']}, {ENTREPRISE['ville']} (Québec) {ENTREPRISE['cp']}</span>
      <span>© {AUJ[:4]} Takedown Studio · Site par Scalera</span>
    </div>
  </div>
</footer>'''

def hesite():
    return '''<section class="hesite">
  <div class="wrap">
    <div><h2 class="x rv">Tu hésites entre plusieurs options?</h2>
    <p class="rv">Envoie-nous ton idée et les informations que tu as. On va t’aider à choisir la bonne combinaison de produits et de techniques.</p></div>
    <a class="btn btn-w rv" href="/contact">Demander une soumission <span class="arr">→</span></a>
  </div>
</section>'''

def photo(n, alt, cls='', style='', pos='50% 50%', eager=False, sizes='100vw'):
    """Vraie photo de l'atelier, en WebP 600 et 1086 px (générés par optimiser_images)."""
    charge = 'fetchpriority="high"' if eager else 'loading="lazy"'
    base = f'/assets/img/photos/atelier-{n}'
    return (f'<div class="ph {cls}" style="{style}">'
            f'<img src="{base}-1086.webp" srcset="{base}-600.webp 600w, {base}-1086.webp 1086w" sizes="{sizes}" '
            f'alt="{e(alt)}" width="1086" height="1448" {charge} decoding="async" style="object-position:{pos}">'
            f'</div>')

TRIO = '(max-width:980px) 50vw, 33vw'

def ph(tag, ton, cls='', style=''):
    return f'<div class="ph {cls}" style="--t:{ton};{style}"><span class="tag">{e(tag)}</span></div>'

def tuile(s, titre_tag='h3'):
    # Dessin maison dans le style Takedown (statique/img/services/), comme la case « Tu sais pas quelle technique choisir? »
    return (f'<a class="tile dessin rv" href="/services/{s["slug"]}">'
            f'<div class="art"><img src="/assets/img/services/{s["slug"]}-blanc.png" alt="" loading="lazy"></div>'
            f'<div class="lab"><div><{titre_tag}>{nom_court(s)}</{titre_tag}><p>{s["court"]}</p></div>'
            f'<span class="go" aria-hidden="true">→</span></div></a>')

def tuile_aide():
    return '''<a class="tile help rv" href="/contact?service=je-sais-pas"><div><h3>Tu sais pas quelle technique choisir?</h3><p>Envoie-nous ton idée. On t’aide à trouver la bonne combinaison de produits et de techniques.</p></div><div class="bas"><span class="go" aria-hidden="true">→</span><img src="/assets/img/illustration-encre-noir.png" alt="" loading="lazy" width="300" height="230"></div></a>'''

def crumb(chemin):
    morceaux = ['<a href="/">Accueil</a>']
    for u, t in chemin[:-1]:
        morceaux.append(f'<a href="{u}">{t}</a>')
    morceaux.append(f'<span aria-current="page">{chemin[-1][1]}</span>')
    return '<nav class="crumb mono" aria-label="Fil d’Ariane">' + '<span aria-hidden="true">/</span>'.join(morceaux) + '</nav>'

def phead(chemin, titre, intro, ctas='', dessin=None):
    fig = f'<img class="fig" src="/assets/img/{dessin}-blanc.png" alt="" aria-hidden="true">' if dessin else ''
    return f'''<section class="phead">
  <div class="wrap">
    {crumb(chemin)}
    <h1 class="x">{titre}</h1>
    <p class="intro">{intro}</p>
    {f'<div class="ctas">{ctas}</div>' if ctas else ''}
  </div>
  {fig}
</section>'''

def plus_prevoir(plus, prevoir):
    return f'''<div class="pp rv">
      <div class="plus"><span class="lbl mono"><i>+</i>Les plus</span><p>{plus}</p></div>
      <div><span class="lbl mono"><i>!</i>À prévoir</span><p>{prevoir}</p></div>
    </div>'''

def etapes():
    return '''<section class="how wrap">
    <div class="top">
      <div><p class="mono rv" style="color:var(--mute)">Le processus</p><h2 class="h2 rv" style="margin-top:12px">Comment ça fonctionne</h2>
      <p class="rv">Tu nous expliques ton projet. On choisit les produits et on prépare la soumission. Tu approuves le visuel. On lance la production selon les conditions confirmées.</p></div>
      <img class="rv" src="/assets/img/illustration-encre-blanc.png" alt="" loading="lazy" width="250" height="192">
    </div>
    <ol class="steps" style="list-style:none">
      <li style="display:contents"><div class="rv"><b>01</b><p>Tu nous expliques ton projet.</p></div></li>
      <li style="display:contents"><div class="rv"><b>02</b><p>On choisit les produits et la technique.</p></div></li>
      <li style="display:contents"><div class="rv"><b>03</b><p>Tu approuves le visuel et la soumission.</p></div></li>
      <li style="display:contents"><div class="rv"><b>04</b><p>On lance la production.</p></div></li>
    </ol>
  </section>'''

# ---------------------------------------------------------------- SEO
def entreprise_ld():
    return {
        '@type': 'ProfessionalService', '@id': BASE + '/#entreprise', 'name': ENTREPRISE['nom'],
        'description': 'Agence de branding spécialisée en vêtements et produits personnalisés à Bromont.',
        'url': BASE + '/', 'logo': BASE + '/assets/img/icone-512.png', 'image': BASE + '/assets/img/partage.png',
        'telephone': ENTREPRISE['tel_intl'], 'email': ENTREPRISE['courriel'],
        'address': {'@type': 'PostalAddress', 'streetAddress': ENTREPRISE['rue'], 'addressLocality': ENTREPRISE['ville'],
                    'addressRegion': ENTREPRISE['region'], 'postalCode': ENTREPRISE['cp'], 'addressCountry': 'CA'},
        'areaServed': [{'@type': 'City', 'name': 'Bromont'}, {'@type': 'AdministrativeArea', 'name': 'Estrie'}],
        'knowsAbout': [s['nom'] for s in SERVICES],
    }

def page(chemin_url, titre_seo, desc, corps, fil=None, extra_ld=None, js=True):
    url = BASE + (chemin_url if chemin_url != '/' else '/')
    graph = [entreprise_ld(), {'@type': 'WebPage', '@id': url + '#page', 'url': url, 'name': titre_seo,
                                'description': desc, 'inLanguage': 'fr-CA', 'isPartOf': {'@id': BASE + '/#site'},
                                'about': {'@id': BASE + '/#entreprise'}},
             {'@type': 'WebSite', '@id': BASE + '/#site', 'url': BASE + '/', 'name': 'Takedown Studio', 'inLanguage': 'fr-CA'}]
    if fil:
        items = [{'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': BASE + '/'}]
        for i, (u, t) in enumerate(fil, start=2):
            items.append({'@type': 'ListItem', 'position': i, 'name': H.unescape(t), 'item': BASE + u})
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': items})
    if extra_ld:
        graph += extra_ld
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)
    return f'''<!doctype html>
<html lang="fr-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre_seo)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#000000">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_CA">
<meta property="og:site_name" content="Takedown Studio">
<meta property="og:title" content="{e(titre_seo)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/img/partage.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/img/icone-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/assets/img/icone-180.png">
<link rel="preload" href="/assets/polices/archivo-400-800.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
<script>if(!location.search.includes('apercu'))document.documentElement.classList.add('js')</script>
<script type="application/ld+json">{ld}</script>
</head>
<body>
{corps}
{'<script src="/assets/site.js?v=' + V + '" defer></script>' if js else ''}
</body>
</html>
'''

# ---------------------------------------------------------------- pages
def accueil():
    tuiles = ''.join(tuile(s) for s in SERVICES) + tuile_aide()
    corps = f'''{nav('/')}
<main id="contenu">
  <section class="hero">
    <img class="mark" src="/assets/img/logo-complet-lutteurs-blanc.png" alt="Takedown Studio" width="1000" height="799" fetchpriority="high">
    <h1 class="sr">Takedown Studio, agence de branding à Bromont</h1>
    <p class="sub fade" style="animation-delay:1.3s">Vêtements et produits personnalisés à Bromont</p>
    <p class="pos fade" style="animation-delay:1.4s">Agence de branding spécialisée en vêtements et produits personnalisés.</p>
    <div class="ctas fade" style="animation-delay:1.55s">
      <a class="btn btn-w" href="/services">Découvrir nos services</a>
      <a class="btn btn-g" href="/contact">Parle-nous de ton projet</a>
    </div>
  </section>

  <section class="mission" aria-labelledby="t-presentation">
    {photo(4, 'L’atelier de Takedown Studio à Bromont, avec les presses à chaleur et le séchoir de sérigraphie', pos='50% 62%')}
    <div class="wrap in">
      <h2 class="sr" id="t-presentation">L’agence</h2>
      <p class="big rv">On t’aide à mettre ta marque sur des vêtements et des produits que les gens vont aimer utiliser.</p>
      <p class="small rv">Du choix du modèle au placement de ton logo, on te conseille selon ton idée, ton budget et la quantité dont tu as besoin. Broderie, sérigraphie ou impression numérique : on trouve la bonne option pour ton projet.</p>
      <a class="lien rv" href="/agence-branding">Découvrir l’agence <span class="arr">→</span></a>
    </div>
  </section>

  <section class="sec wrap" id="services" aria-labelledby="t-services">
    <div class="head">
      <h2 class="h2 rv" id="t-services">Nos services</h2>
      <div class="links rv"><a href="/services">Tous les services <span class="arr">→</span></a></div>
    </div>
    <div class="grid">{tuiles}</div>
  </section>

  {etapes()}

  <section class="words wrap" aria-label="Nos techniques">
    <div class="line x"><span>Du fil.</span><small>Broderie<br>Casquettes, polos</small></div>
    <div class="line x"><span>De l’encre.</span><small>Sérigraphie<br>En quantité</small></div>
    <div class="line x"><span>De la chaleur.</span><small>Impression DTF<br>Petits lots</small></div>
    <div class="line x"><span>Ta marque.</span><small>Takedown Studio<br>Bromont</small></div>
  </section>
</main>
{pied()}'''
    return page('/', 'Takedown Studio | Vêtements et produits personnalisés à Bromont',
                'Agence de branding à Bromont. On met ta marque sur des vêtements et des produits : broderie, sérigraphie, DTF, casquettes, patches et autocollants.',
                corps)

def agence():
    corps = f'''{nav('/agence-branding')}
<main id="contenu">
  {phead([('/agence-branding', 'L’agence')], 'Agence de branding à Bromont',
         'Chez Takedown Studio, on t’aide à donner une image cohérente à tes vêtements et à tes produits. Que ce soit pour ton entreprise, ton équipe, un événement ou ta propre marque, on prend le temps de comprendre ce que tu cherches. On t’accompagne dans le choix des produits, des couleurs, des placements et de la bonne méthode de personnalisation.',
         '<a class="btn btn-w" href="/contact">Parle-nous de ton projet</a><a class="btn btn-g" href="/services">Nos services</a>',
         'logo-complet-lutteurs')}
  <section class="sec wrap">
    <div class="trio">
      {photo(1, 'Étagères de vêtements vierges et presse de sérigraphie dans l’atelier Takedown', 'rv', sizes=TRIO)}
      {photo(2, 'Espace de travail de l’atelier avec machine à coudre, presse à chaleur et planches de skate au mur', 'rv', sizes=TRIO)}
      {photo(3, 'Comptoir d’accueil de Takedown Studio avec casquettes et vêtements personnalisés', 'rv', sizes=TRIO)}
    </div>
  </section>
  <section class="sec wrap">
    {plus_prevoir('Un même contact pour ton projet, des conseils concrets et des produits qui vont bien ensemble.',
                  'Un projet qui regroupe plusieurs produits demande plus de préparation. Le budget et les délais dépendent des articles choisis.')}
  </section>
  <section class="words wrap" aria-label="Nos techniques">
    <div class="line x"><span>Du fil.</span><small>Broderie</small></div>
    <div class="line x"><span>De l’encre.</span><small>Sérigraphie</small></div>
    <div class="line x"><span>De la chaleur.</span><small>Impression DTF</small></div>
    <div class="line x"><span>Ta marque.</span><small>Takedown Studio</small></div>
  </section>
  {etapes()}
</main>
{hesite()}
{pied()}'''
    return page('/agence-branding', 'Agence de branding à Bromont | Takedown Studio',
                'Takedown Studio t’aide à donner une image cohérente à tes vêtements et à tes produits : choix des produits, des couleurs, des placements et de la technique.',
                corps, fil=[('/agence-branding', 'L’agence')])

def services_index():
    blocs = ''
    for s in SERVICES:
        phrase = s['texte'].split('. ')[0].rstrip('.') + '.'
        blocs += f'''<article class="svc rv">
      {ph(s['tag'], s['ton'])}
      <div class="txt"><span class="mono" style="color:var(--mute)">{e(s['court'])}</span><h2>{s['nom']}</h2><p>{phrase}</p>
      <div><a class="btn btn-g" href="/services/{s['slug']}">Découvrir le service <span class="arr">→</span></a></div></div>
    </article>'''
    extras = ''
    if AFFICHER_EXTRAS:
        liens = ''.join(f'<a class="lien" href="/services/vetements-personnalises#{x["id"]}">{x["titre"]} <span class="arr">→</span></a>' for x in EXTRAS)
        extras = f'''<section class="sec wrap"><div class="head"><h2 class="h2 rv">Aussi possible</h2></div>
      <div class="rv" style="display:flex;gap:28px;flex-wrap:wrap">{liens}</div></section>'''
    corps = f'''{nav('/services')}
<main id="contenu">
  {phead([('/services', 'Nos services')], 'Nos services',
         'On t’aide à choisir les bons produits et la bonne technique pour représenter ta marque. Explore nos services pour voir les possibilités, les avantages et les éléments à prévoir.',
         '<a class="btn btn-w" href="/contact?service=je-sais-pas">Je sais pas quelle technique choisir</a>', 'illustration-pinceau')}
  <section class="sec">{blocs}</section>
  {extras}
</main>
{hesite()}
{pied()}'''
    ld = [{'@type': 'ItemList', 'name': 'Nos services', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': s['nom'], 'url': f'{BASE}/services/{s["slug"]}'} for i, s in enumerate(SERVICES)]}]
    return page('/services', 'Vêtements et produits personnalisés | Takedown Studio',
                'Vêtements personnalisés, broderie, sérigraphie, impression DTF, casquettes et tuques, patches et autocollants. Découvre nos services à Bromont.',
                corps, fil=[('/services', 'Nos services')], extra_ld=ld)

def service(s, i):
    exemples = ''.join(f'<figure class="rv">{ph("Photo à venir", s["ton"])}<figcaption>{x}</figcaption></figure>' for x in s['exemples'])
    extras = ''
    if s['slug'] == 'vetements-personnalises' and AFFICHER_EXTRAS:
        extras = '<section class="sec wrap"><div class="head"><h2 class="h2 rv">Aussi possible</h2><p class="note rv">Avec nos partenaires, pour les projets qui sortent de l’ordinaire.</p></div>' + ''.join(f'''
      <article class="extra rv" id="{x['id']}">
        <div><span class="mono">Sur demande</span><h3>{x['titre']}</h3></div>
        <div><p>{x['texte']}</p>
          <dl><div><dt>Les plus</dt><dd>{x['plus']}</dd></div><div><dt>À prévoir</dt><dd>{x['prevoir']}</dd></div></dl>
          <p style="margin-top:22px"><a class="lien" href="{soum(x['val'])}">Demander une soumission <span class="arr">→</span></a></p></div>
      </article>''' for x in EXTRAS) + '</section>'
    assoc = ''
    if s['liens']:
        assoc = f'''<section class="sec wrap"><div class="head"><h2 class="h2 rv">Services associés</h2>
      <div class="links rv"><a href="/services">Tous les services <span class="arr">→</span></a></div></div>
      <div class="grid g3">{''.join(tuile(PAR_SLUG[l]) for l in s['liens'][:3])}</div>
      {('<div class="rv" style="display:flex;gap:28px;flex-wrap:wrap;margin-top:24px">' + ''.join(f'<a class="lien" href="/services/{l}">{nom_court(PAR_SLUG[l])} <span class="arr">→</span></a>' for l in s['liens'][3:]) + '</div>') if len(s['liens']) > 3 else ''}
    </section>'''
    ctas = (f'<a class="btn btn-w" href="{soum(s["slug"])}">{s["bouton"]}</a>'
            f'<a class="btn btn-g" href="/realisations?f={s["filtre"]}">Voir les réalisations</a>')
    corps = f'''{nav('/services')}
<main id="contenu">
  {phead([('/services', 'Nos services'), ('/services/' + s['slug'], s['nom'])], s['nom'], s['texte'], ctas, DESSINS[i % 3])}
  <section class="sec wrap">{ph('Grande photo principale · ' + s['tag'], s['ton'], 'rv', 'aspect-ratio:16/7')}</section>
  <section class="sec wrap">{plus_prevoir(s['plus'], s['prevoir'])}</section>
  <section class="sec wrap"><div class="head"><h2 class="h2 rv">Exemples</h2>
    <div class="links rv"><a href="/realisations?f={s['filtre']}">Voir les réalisations <span class="arr">→</span></a></div></div>
    <div class="ex">{exemples}</div>
    <p class="rv" style="margin-top:40px"><a class="btn btn-w" href="{soum(s['slug'])}">{s['bouton']} <span class="arr">→</span></a></p>
  </section>
  {extras}
  {assoc}
</main>
{hesite()}
{pied()}'''
    ld = [{'@type': 'Service', 'name': s['nom'], 'serviceType': s['nom'], 'description': s['texte'],
           'provider': {'@id': BASE + '/#entreprise'}, 'areaServed': {'@type': 'City', 'name': 'Bromont'},
           'url': f'{BASE}/services/{s["slug"]}'}]
    return page('/services/' + s['slug'], s['seo'], s['desc'], corps,
                fil=[('/services', 'Nos services'), ('/services/' + s['slug'], s['nom'])], extra_ld=ld)

def realisations():
    chips = ''.join(f'<button class="chip" type="button" data-f="{k}" aria-pressed="{str(k == "tous").lower()}">{t}</button>' for k, t in FILTRES)
    items = ''.join(f'''<article class="real rv" data-c="{r['c']}">
      <div class="ph" style="--t:{r['ton']}"><span class="tag">Photo à venir</span></div>
      <h3>{r['titre']}</h3>
      <div class="meta mono"><span>{r['produit']}</span><span>{r['tech']}</span></div>
      <p>{r['desc']}</p>
      <a class="lien" href="/services/{r['svc']}">{nom_court(PAR_SLUG[r['svc']])} <span class="arr">→</span></a>
    </article>''' for r in REALISATIONS)
    corps = f'''{nav('/realisations')}
<main id="contenu">
  {phead([('/realisations', 'Réalisations')], 'Nos réalisations',
         'Découvre quelques projets réalisés par Takedown Studio. Chaque projet est différent, et la technique utilisée dépend du produit, du visuel, de la quantité et du résultat recherché.',
         '', 'illustration-encre')}
  <section class="sec wrap">
    <div class="chips" role="group" aria-label="Filtrer par technique">{chips}</div>
    <div class="reals">{items}</div>
    <p style="margin-top:56px"><a class="btn btn-w" href="/contact">Parle-nous de ton projet <span class="arr">→</span></a></p>
  </section>
</main>
{hesite()}
{pied()}'''
    return page('/realisations', 'Nos réalisations | Takedown Studio',
                'Des projets de Takedown Studio : vêtements brodés, t-shirts en sérigraphie, impression DTF, casquettes, patches et autocollants personnalisés.',
                corps, fil=[('/realisations', 'Réalisations')])

def contact():
    options = ''.join(f'<option value="{v}">{t}</option>' for v, t in CHOIX_SERVICE)
    def champ(id_, lab, typ='text', req=True, full=False, extra='', ph_=''):
        opt = '' if req else ' <em>(facultatif)</em>'
        r = ' required aria-required="true"' if req else ''
        return (f'<div class="champ{" full" if full else ""}"><label for="{id_}">{lab}{opt}</label>'
                f'<input id="{id_}" name="{id_}" type="{typ}"{r}{extra}{f" placeholder=\"{ph_}\"" if ph_ else ""}>'
                f'<span class="msg">Ce champ est obligatoire.</span></div>')
    corps = f'''{nav('/contact')}
<main id="contenu">
  {phead([('/contact', 'Contact')], 'Demander une soumission',
         'Envoie-nous ton idée, ton logo et la quantité que tu as en tête. On va regarder les possibilités avec toi et te guider vers les bons produits et la bonne technique.')}
  <section class="wrap formgrid">
    <div>
      <form id="soumission" class="form" action="/api/soumission" method="post" enctype="multipart/form-data" novalidate>
        {champ('nom', 'Nom', extra=' autocomplete="name"')}
        {champ('entreprise', 'Entreprise', req=False, extra=' autocomplete="organization"')}
        {champ('courriel', 'Courriel', 'email', extra=' autocomplete="email" inputmode="email"')}
        {champ('telephone', 'Téléphone', 'tel', req=False, extra=' autocomplete="tel" inputmode="tel"')}
        <div class="champ full"><label for="service">Service recherché</label>
          <select id="service" name="service" required aria-required="true"><option value="">Choisis un service</option>{options}</select>
          <span class="msg">Choisis un service, ou coche la case en dessous.</span>
          <label class="coche" style="margin-top:12px;text-transform:none;letter-spacing:0;font-family:inherit;font-size:15px;color:#d6d6d9"><input type="checkbox" id="sais-pas"> Je ne sais pas quelle technique choisir</label>
        </div>
        {champ('produit', 'Produit recherché', ph_='Ex. hoodies, casquettes, autocollants')}
        {champ('quantite', 'Quantité approximative', ph_='Ex. 50 morceaux', extra=' inputmode="numeric"')}
        {champ('date', 'Date souhaitée', 'date')}
        {champ('budget', 'Budget approximatif', req=False)}
        <div class="champ full"><label for="description">Description du projet</label>
          <textarea id="description" name="description" required aria-required="true" placeholder="Ton idée, les couleurs, les placements, l’utilisation prévue…"></textarea>
          <span class="msg">Décris-nous ton projet en quelques mots.</span></div>
        <div class="champ full"><span class="lab">Tes fichiers <em style="color:var(--mute);text-transform:none;letter-spacing:0">(logo, visuel, croquis)</em></span>
          <label class="depot" tabindex="0" for="fichiers"><input id="fichiers" name="fichiers" type="file" multiple accept=".ai,.eps,.pdf,.svg,.png,.jpg,.jpeg,.webp,.heic,.psd,image/*,application/pdf">
            <b>Glisse tes fichiers ici</b> ou clique pour les choisir</label>
          <ul class="fichiers" aria-live="polite"></ul></div>
        <div class="champ full"><label for="source">Comment tu nous as connus <em>(facultatif)</em></label>
          <select id="source" name="source"><option value="">Choisis une option</option><option>Instagram</option><option>Facebook</option><option>Google</option><option>Bouche-à-oreille</option><option>Un client de Takedown</option><option>Autre</option></select></div>
        <div class="miel" aria-hidden="true"><label for="site_web">Ne pas remplir</label><input id="site_web" name="site_web" type="text" tabindex="-1" autocomplete="off"></div>
        <label class="coche full"><input type="checkbox" name="copie" value="oui"> Envoie-moi une copie de ma demande par courriel</label>
        <div class="envoi full"><button class="btn btn-w" type="submit">Envoyer ma demande</button><small>On te répond par courriel ou par téléphone.</small></div>
      </form>
      <div id="etat" class="etat" role="status" aria-live="polite"></div>
    </div>
    <aside class="aside">
      <div class="bloc"><h3>Pour aller plus vite</h3><ol><li>Ton logo ou ton visuel</li><li>La quantité que tu as en tête</li><li>La date où tu en as besoin</li></ol></div>
      <div class="bloc"><h3>Nous joindre</h3><a href="mailto:{ENTREPRISE['courriel']}">{ENTREPRISE['courriel']}</a><a href="tel:{ENTREPRISE['tel_intl']}">{ENTREPRISE['tel']}</a></div>
      <div class="bloc"><h3>Le studio</h3><p>{ENTREPRISE['rue']}<br>{ENTREPRISE['ville']} (Québec) {ENTREPRISE['cp']}</p></div>
      {photo(3, 'Le comptoir d’accueil de Takedown Studio, 50 chemin de Gaspé à Bromont', 'studio', sizes='(max-width:980px) 90vw, 420px')}
    </aside>
  </section>
</main>
{pied(court=True)}'''
    return page('/contact', 'Demander une soumission | Takedown Studio',
                'Envoie ton idée, ton logo et la quantité que tu as en tête. Takedown Studio te guide vers les bons produits et la bonne technique. Bromont.',
                corps, fil=[('/contact', 'Contact')])

def construction():
    """Page « site en construction » pour www.takedownstudio.com, en attendant le vrai site.
    Même header que l'accueil (et la même intro), plus les coordonnées. Pas de menu."""
    corps = f'''<main id="contenu">
  <section class="hero bientot">
    <img class="mark" src="/assets/img/logo-complet-lutteurs-blanc.png" alt="Takedown Studio" width="1000" height="799" fetchpriority="high">
    <h1 class="sr">Takedown Studio, agence de branding à Bromont</h1>
    <p class="mono etiquette fade" style="animation-delay:1.25s">Site en construction</p>
    <p class="sub fade" style="animation-delay:1.3s">Notre nouveau site s’en vient.</p>
    <p class="pos fade" style="animation-delay:1.4s">Agence de branding spécialisée en vêtements et produits personnalisés, à Bromont. Broderie, sérigraphie, impression DTF, casquettes, patches et autocollants.</p>
    <div class="ctas fade" style="animation-delay:1.55s">
      <a class="btn btn-w" href="mailto:{ENTREPRISE['courriel']}?subject=Mon%20projet%20avec%20Takedown">Écris-nous ton projet</a>
      <a class="btn btn-g" href="tel:{ENTREPRISE['tel_intl']}">{ENTREPRISE['tel']}</a>
    </div>
    <p class="mono adresse fade" style="animation-delay:1.7s">{ENTREPRISE['rue']} · {ENTREPRISE['ville']} (Québec) {ENTREPRISE['cp']}</p>
  </section>
</main>'''
    html = page('/', 'Takedown Studio | Vêtements et produits personnalisés à Bromont',
                'Takedown Studio, agence de branding à Bromont : vêtements et produits personnalisés. Notre nouveau site s’en vient, écris-nous pour ton projet.',
                corps)
    return html

def introuvable():
    corps = f'''{nav('')}
<main id="contenu">
  {phead([('/404', 'Page introuvable')], 'Page introuvable', 'Cette page existe pas ou elle a changé d’adresse.',
         '<a class="btn btn-w" href="/">Retour à l’accueil</a><a class="btn btn-g" href="/services">Nos services</a>', 'illustration-pinceau')}
</main>
{pied()}'''
    return page('/404', 'Page introuvable | Takedown Studio', 'Cette page n’existe pas.', corps).replace(
        '<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"')

# ---------------------------------------------------------------- images
def images():
    img = os.path.join(SORTIE, 'assets', 'img')
    logo = Image.open(os.path.join(img, 'logo-complet-lutteurs-blanc.png')).convert('RGBA')
    # image de partage 1200 x 630
    og = Image.new('RGBA', (1200, 630), (0, 0, 0, 255))
    l = logo.copy(); l.thumbnail((760, 520), Image.LANCZOS)
    og.alpha_composite(l, ((1200 - l.width) // 2, (630 - l.height) // 2))
    og.convert('RGB').save(os.path.join(img, 'partage.png'), optimize=True)
    # icônes : le logo sur un carré noir
    for taille in (512, 192, 180):
        ic = Image.new('RGBA', (taille, taille), (0, 0, 0, 255))
        l = logo.copy(); l.thumbnail((int(taille * .86), int(taille * .86)), Image.LANCZOS)
        ic.alpha_composite(l, ((taille - l.width) // 2, (taille - l.height) // 2))
        ic.convert('RGB').save(os.path.join(img, f'icone-{taille}.png'), optimize=True)
    Image.open(os.path.join(img, 'icone-192.png')).save(os.path.join(SORTIE, 'favicon.ico'), sizes=[(48, 48)])

# ---------------------------------------------------------------- vitesse
# Les polices sont hébergées sur le site (statique/polices/, sous-ensemble latin) et
# le CSS est mis directement dans chaque page : plus aucune ressource qui bloque l'affichage.
POLICES = """@font-face{font-family:"Archivo";src:url(/assets/polices/archivo-400-800.woff2) format("woff2");font-weight:400 800;font-stretch:100% 125%;font-display:swap}
@font-face{font-family:"IBM Plex Mono";src:url(/assets/polices/ibm-plex-mono-400.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"IBM Plex Mono";src:url(/assets/polices/ibm-plex-mono-500.woff2) format("woff2");font-weight:500;font-display:swap}
"""

def css_minifie():
    import re
    t = io.open(os.path.join(ICI, 'statique', 'site.css'), encoding='utf-8').read()
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    t = re.sub(r'\s*\n\s*', '', t)
    t = re.sub(r'\s*([{};,>])\s*', r'\1', t)
    return POLICES.replace('\n', '') + t

CSS = ''

# Chaque PNG devient du WebP en 2 largeurs ; le HTML est réécrit avec srcset et sizes.
LARGEURS = {'logo-complet-lutteurs': (520, 1000), 'logo-texte': (260, 1000), 'illustration': (400, 800), 'services/': (800,)}
TAILLES = {'logo-texte': '130px', 'logo-complet-lutteurs': '(max-width:600px) 88vw, 760px', 'illustration': '(max-width:980px) 180px, 300px',
           'services/': '(max-width:980px) 62vw, 31vw'}

def largeurs(nom):
    return next((v for k, v in LARGEURS.items() if nom.startswith(k)), (400, 800))

def optimiser_images():
    racine = os.path.join(SORTIE, 'assets', 'img')
    for dossier, _, fichiers in os.walk(racine):
        for fi in fichiers:
            chemin = os.path.join(dossier, fi)
            rel = os.path.relpath(chemin, racine).replace(os.sep, '/')
            base, ext = os.path.splitext(chemin)
            if rel.startswith('photos/') and ext == '.jpg':
                im = Image.open(chemin).convert('RGB')
                for w in (600, 1086):
                    c = im.copy(); c.thumbnail((w, w * 2), Image.LANCZOS)
                    c.save(f'{base}-{w}.webp', quality=74, method=4)
                os.remove(chemin)
            elif rel.startswith('photos/') and ext == '.webp' and '-' not in os.path.basename(base).replace('atelier-', '', 1):
                os.remove(chemin)   # ancienne version sans largeur
            elif ext == '.png' and not rel.startswith(('icone', 'partage')):
                im = Image.open(chemin).convert('RGBA')
                for w in largeurs(rel):
                    c = im.copy()
                    if c.width > w:
                        c = c.resize((w, round(c.height * w / c.width)), Image.LANCZOS)
                    c.save(f'{base}-{w}.webp', quality=82, method=4)
                os.remove(chemin)   # le PNG n'est plus servi

def images_srcset(html):
    import re
    def un(m):
        nom = m.group(1)
        ws = largeurs(nom)
        if len(ws) == 1:
            return f'src="/assets/img/{nom}-{ws[0]}.webp"'
        sizes = next((v for k, v in TAILLES.items() if nom.startswith(k)), '50vw')
        jeu = ', '.join(f'/assets/img/{nom}-{w}.webp {w}w' for w in ws)
        return f'src="/assets/img/{nom}-{ws[-1]}.webp" srcset="{jeu}" sizes="{sizes}"'
    return re.sub(r'src="/assets/img/((?:services/)?[\w-]+)\.png"', un, html)

# ---------------------------------------------------------------- construction
# Aperçu GitHub Pages : le site vit sous /takedown-studio/, donc on préfixe les adresses
# absolues et on bloque l'indexation (le vrai domaine reste l'URL canonique).
CHEMIN_BASE = os.environ.get('CHEMIN_BASE', '').rstrip('/')

def prefixer(html):
    if not CHEMIN_BASE:
        return html
    import re
    for attr in ('href="/', 'src="/', 'action="/', 'url(/'):
        html = html.replace(attr, attr[:-1] + CHEMIN_BASE + '/')
    html = re.sub(r'(srcset="|imagesrcset=")([^"]*)',
                  lambda m: m.group(1) + re.sub(r'(^|,\s*)/', lambda n: n.group(1) + CHEMIN_BASE + '/', m.group(2)), html)
    return html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">', 1)

def ecrire(rel, contenu):
    if rel.endswith('.html'):
        contenu = images_srcset(contenu)
        contenu = prefixer(contenu)
    f = os.path.join(SORTIE, rel)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    io.open(f, 'w', encoding='utf-8').write(contenu)

def construire():
    if os.path.isdir(SORTIE):
        shutil.rmtree(SORTIE)
    os.makedirs(os.path.join(SORTIE, 'assets'))
    global CSS
    CSS = css_minifie()
    shutil.copytree(os.path.join(ICI, 'statique', 'img'), os.path.join(SORTIE, 'assets', 'img'))
    shutil.copytree(os.path.join(ICI, 'statique', 'polices'), os.path.join(SORTIE, 'assets', 'polices'))
    shutil.copy(os.path.join(ICI, 'statique', 'site.js'), os.path.join(SORTIE, 'assets', 'site.js'))
    images()
    optimiser_images()

    # Fichiers « page.html » : Cloudflare les sert à /page, sans barre oblique finale,
    # comme les adresses du plan de contenu (/services/broderie).
    pages = {'index.html': accueil(), 'agence-branding.html': agence(), 'services.html': services_index(),
             'realisations.html': realisations(), 'contact.html': contact(), '404.html': introuvable()}
    for i, s in enumerate(SERVICES):
        pages[f'services/{s["slug"]}.html'] = service(s, i)
    for rel, html in pages.items():
        assert '—' not in html, f'tiret cadratin dans {rel}'
        ecrire(rel, html)

    urls = ['/', '/agence-branding', '/services'] + [f'/services/{s["slug"]}' for s in SERVICES] + ['/realisations', '/contact']
    ecrire('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
           ''.join(f'  <url><loc>{BASE}{u}</loc><lastmod>{AUJ}</lastmod></url>\n' for u in urls) + '</urlset>\n')
    ecrire('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {BASE}/sitemap.xml\n')
    print(f'✓ {len(pages)} fichiers HTML, {len(urls)} pages dans le sitemap → {SORTIE}')
    construire_construction()

def construire_construction():
    """Copie autonome de la page « en construction » dans ../site-construction/ (son propre dépôt GitHub).
    Adresses relatives pour marcher autant sur l'aperçu GitHub que sur www.takedownstudio.com."""
    import re
    dest = os.path.join(os.path.dirname(ICI), 'site-construction')
    os.makedirs(dest, exist_ok=True)
    for n in os.listdir(dest):
        if n in ('.git', 'CNAME', 'README.md'):
            continue
        p = os.path.join(dest, n)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    html = images_srcset(construction())
    for attr in ('href="/', 'src="/', 'url(/'):
        html = html.replace(attr, attr[:-1])
    html = re.sub(r'(srcset=")([^"]*)', lambda m: m.group(1) + re.sub(r'(^|,\s*)/', r'\1', m.group(2)), html)
    html = html.replace('href="">', 'href="./">')
    html = html.replace('https://takedownstudio.com', 'https://www.takedownstudio.com')   # le client utilise www
    assert '—' not in html
    io.open(os.path.join(dest, 'index.html'), 'w', encoding='utf-8').write(html)
    io.open(os.path.join(dest, '404.html'), 'w', encoding='utf-8').write(
        '<!doctype html><meta charset="utf-8"><title>Takedown Studio</title><meta http-equiv="refresh" content="0;url=/"><a href="/">Takedown Studio</a>')
    os.makedirs(os.path.join(dest, 'assets', 'img'))
    for n in os.listdir(os.path.join(SORTIE, 'assets', 'img')):
        if n.startswith(('logo-', 'illustration-', 'icone-', 'partage')):
            shutil.copy(os.path.join(SORTIE, 'assets', 'img', n), os.path.join(dest, 'assets', 'img', n))
    shutil.copytree(os.path.join(SORTIE, 'assets', 'polices'), os.path.join(dest, 'assets', 'polices'))
    shutil.copy(os.path.join(SORTIE, 'assets', 'site.js'), os.path.join(dest, 'assets', 'site.js'))
    shutil.copy(os.path.join(SORTIE, 'favicon.ico'), os.path.join(dest, 'favicon.ico'))
    io.open(os.path.join(dest, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\n')
    print(f'✓ page en construction → {dest}')

if __name__ == '__main__':
    construire()
