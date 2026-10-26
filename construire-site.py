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
import io, os, re, json, shutil, datetime, html as H
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, 'site')
BASE = 'https://takedownstudio.com'   # À CONFIRMER : domaine final du site
AUJ = datetime.date.today().isoformat()
import hashlib
V = hashlib.sha1(open(os.path.join(ICI, 'statique', 'site.js'), 'rb').read()).hexdigest()[:8]   # change dès que le JS change

# Adresse du Worker Cloudflare qui reçoit le formulaire (fichiers dans R2 + courriel à Takedown).
API_SOUMISSION = os.environ.get('API_SOUMISSION', 'https://takedown-soumission.jack-mobile.workers.dev/api/soumission')

# Les 3 services de l'étape 15 doivent être validés par Takedown avant la mise en ligne.
AFFICHER_EXTRAS = True

ENTREPRISE = {
    'nom': 'Takedown Studio',
    'tel': '579 488-0321', 'tel_intl': '+15794880321',
    'courriel': 'info@takedownstudio.com',
    'rue': '50, chemin de Gaspé, bloc C, local 5', 'ville': 'Bromont', 'region': 'QC', 'cp': 'J2L 2N8',
    'geo': (45.31643, -72.65788),   # 50 ch. de Gaspé (OpenStreetMap)
    'reseaux': ['https://www.instagram.com/takedownstudio/'],   # sameAs
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
         desc='Sérigraphie sur t-shirts et hoodies pour ton équipe, ton événement ou ton merch. Un beau rendu à l’encre, intéressant en quantité. Takedown Studio Bromont.'),
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
    # 2026-10-24 (Takedown via Alex) : page de départ, texte à retravailler avec Takedown. Bloc rose (rose=True).
    dict(slug='casquettes-100-personnalisees', nom='Casquettes 100 % personnalisées', filtre='casquettes-tuques', ton='#f29cc0', rose=True,
         tag='Casquette sur mesure', court='Forme, couleurs, tissu, logo : on la monte de A à Z, à ton choix.',
         texte='Pas juste ton logo sur une casquette déjà faite. On part de zéro et tu choisis chaque morceau : la forme, les couleurs, le tissu et le logo. On monte la casquette avec toi, de A à Z.',
         plus='Une casquette unique, pensée pour ta marque, avec la forme, les couleurs, le tissu et le logo que tu choisis.',
         prevoir='Un projet sur mesure demande plus de préparation qu’une casquette de catalogue. Les minimums, les délais et le prix dépendent de la forme, du tissu et de la méthode choisis, et on te les confirme dans la soumission.',
         exemples=['Forme : structurée, dad cap, trucker, cinq panneaux', 'Couleurs de la couronne, de la visière et des coutures', 'Tissu : coton, sergé, maille, velours côtelé', 'Logo brodé, en patch ou imprimé', 'Détails : dessous de la visière, étiquette, fermeture'],
         bouton='Demander une soumission pour une casquette sur mesure',
         liens=['casquettes-tuques', 'patches-ecussons', 'broderie'],
         seo='Casquettes 100 % personnalisées | Takedown Studio',
         desc='Casquettes 100 % personnalisées : forme, couleurs, tissu et logo, on la monte de A à Z selon ton choix. Demande ta soumission à Takedown Studio, Bromont.'),
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

# Réalisations : realisations.csv (une ligne par photo, la photo dans statique/img/photos/<photo>.jpg).
# Pour en ajouter : déposer le JPG, ajouter la ligne, relancer. Les pages de services prennent
# automatiquement les photos de leur service ; sans photo, aucun emplacement vide n'est affiché.
def lire_realisations():
    import csv
    chemin = os.path.join(ICI, 'realisations.csv')
    if not os.path.exists(chemin):
        return []
    rows = []
    for r in csv.DictReader(io.open(chemin, encoding='utf-8')):
        jpg = os.path.join(ICI, 'statique', 'img', 'photos', r['photo'] + '.jpg')
        if not os.path.exists(jpg):
            raise SystemExit(f'photo manquante pour la réalisation : {jpg}')
        r['w'], r['h'] = Image.open(jpg).size
        rows.append(r)
    return rows
REALISATIONS = lire_realisations()
INSTAGRAM = 'https://www.instagram.com/takedownstudio/'
FILTRES = [('tous', 'Tous'), ('vetements', 'Vêtements'), ('broderie', 'Broderie'), ('serigraphie', 'Sérigraphie'),
           ('dtf', 'DTF'), ('casquettes-tuques', 'Casquettes et tuques'), ('patches', 'Patches'), ('autocollants', 'Autocollants')]

CHOIX_SERVICE = [('je-sais-pas', 'Je ne sais pas encore')] + [(s['slug'], s['nom']) for s in SERVICES] + \
                [('vetements-sport-sublimation', 'Vêtements de sport et sublimation'), ('produits-sur-mesure', 'Produits sur mesure')]

DESSINS = ['illustration-pinceau', 'illustration-encre', 'logo-complet-lutteurs']

# Dessins du client (WhatsApp, 7 oct. 2026), convertis en blanc par convertir-dessins.py
DESSIN_SERVICE = {
    'vetements-personnalises': 'dessins/vetements-chandail',
    'broderie': 'dessins/broderie-aiguille',
    'serigraphie': 'dessins/serigraphie-cadre',
    'impression-dtf': 'dessins/presse-chaleur',
    'casquettes-tuques': 'dessins/casquette-tuque',
    'patches-ecussons': 'dessins/patch-aiguille',
    'autocollants': 'dessins/autocollants-planche',
    'casquettes-100-personnalisees': 'dessins/casquettes-tuques-pile',
}

# Tuiles de services (accueil, « Services associés », page Nos services) : un dessin du client
# par service, en action quand il en existe un (la sérigraphie montre l'impression, l'en-tête montre le cadre).
DESSIN_TUILE = dict(DESSIN_SERVICE, serigraphie='dessins/serigraphie-impression')

# Trait d'encre dessiné sous un mot de titre (style des dessins du client : feutre, bout arrondi,
# deux passes qui ne se superposent pas tout à fait). Il se trace quand le titre apparaît.
TRAIT = ('<svg class="trait" viewBox="0 0 300 16" preserveAspectRatio="none" aria-hidden="true">'
         '<path pathLength="1" d="M3 9.5C46 6.2 92 11.8 140 8.6S232 5.4 297 8.8"/>'
         '<path pathLength="1" d="M18 12.6C70 10.4 128 13.8 190 11.2S256 10.2 282 12"/></svg>')

def encre(mot):
    return f'<span class="encre">{mot}{TRAIT}</span>'

def gouttes(cls='coule'):
    # deux gouttes reprises du chandail taché du client, qui « coulent » d'une ligne de section
    return (f'<span class="{cls}" aria-hidden="true">'
            '<img src="/assets/img/dessins/goutte-longue-blanc.png" alt="" width="40" height="178" loading="lazy">'
            '<img src="/assets/img/dessins/goutte-courte-blanc.png" alt="" width="42" height="111" loading="lazy"></span>')

def mots(petits=True):
    # les quotes « Du fil. De l'encre... » avec le dessin du client qui va avec chaque mot
    lignes = [('Du fil.', 'fil-aiguille', 'Broderie<br>Casquettes, polos', 'Broderie'),
              ('De l’encre.', 'serigraphie-racloir', 'Sérigraphie<br>En quantité', 'Sérigraphie'),
              ('De la chaleur.', 'presse-chaleur', 'Impression DTF<br>Petits lots', 'Impression DTF'),
              ('Ta marque.', None, 'Takedown Studio<br>Bromont', 'Takedown Studio')]
    out = ''
    for txt, dessin, long_, court in lignes:
        img = (f'<img class="mini" src="/assets/img/dessins/{dessin}-blanc.png" sizes="160px" alt="" loading="lazy">' if dessin
               else '<img class="mini" src="/assets/img/bonhomme-goutte-blanc.png" sizes="120px" alt="" loading="lazy">')
        out += f'<div class="line x"><span>{txt}</span><span class="cote">{img}<small>{long_ if petits else court}</small></span></div>'
    return f'<section class="words wrap" aria-label="Nos techniques">{out}</section>'

# ---------------------------------------------------------------- morceaux communs
MENU = [('/', 'Accueil'), ('/agence-branding', 'L’agence'), ('/services', 'Nos services'),
        ('/services/casquettes-100-personnalisees', 'Casquettes custom'), ('/catalogue', 'Catalogue'), ('/realisations', 'Réalisations'), ('/contact', 'Contact')]

def soum(slug=None):
    return '/contact' + (f'?service={slug}' if slug else '')

def nav(courant):
    liens = ''.join(
        f'<li><a href="{u}"{" aria-current=\"page\"" if u == courant else ""}{" class=\"rose\"" if "casquettes" in u else ""}>{t}</a></li>' for u, t in MENU)
    mob = ''.join(f'<a href="{u}"{" class=\"rose\"" if "casquettes" in u else ""}>{t}</a>' for u, t in MENU)
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
    tete = '' if court else f'''<p class="mono" style="color:var(--mute)">Demander une soumission</p>
        <h2 class="x rv"><span class="ind">On regarde ton</span><br>projet {encre('ensemble!')}</h2>'''
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
            <div><h4>Studio</h4><a href="/agence-branding">L’agence</a><a href="/catalogue">Catalogue</a><a href="/realisations">Réalisations</a><a href="/contact">Contact</a>
              <h4 style="margin-top:22px">Nous joindre</h4><a href="tel:{ENTREPRISE['tel_intl']}">{ENTREPRISE['tel']}</a><a href="mailto:{ENTREPRISE['courriel']}">{ENTREPRISE['courriel']}</a><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a></div>
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
    return f'''<section class="hesite">
  {gouttes('coule gauche')}
  <div class="wrap">
    <div><h2 class="x rv">Tu hésites entre plusieurs options?</h2>
    <p class="rv">Envoie-nous ton idée et les informations que tu as. On va t’aider à choisir la bonne combinaison de produits et de techniques.</p></div>
    <img class="duo rv" src="/assets/img/dessins/deux-tuques-blanc.png" alt="" loading="lazy" width="1000" height="640">
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

def photo_real(r, sizes='(max-width:600px) 100vw, (max-width:980px) 50vw, 33vw', cls='', eager=False):
    """Photo d'une réalisation, en WebP 600 et 1086 px (générés par optimiser_images)."""
    base = f'/assets/img/photos/{r["photo"]}'
    w = min(1086, r['w']); h = round(r['h'] * w / r['w'])
    fit = ' fit' if r.get('cadrage') == 'contain' else ''
    charge = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<div class="ph{fit} {cls}"><img src="{base}-1086.webp" srcset="{base}-600.webp 600w, {base}-1086.webp 1086w" '
            f'sizes="{sizes}" alt="{e(r["alt"])}" width="{w}" height="{h}" {charge} decoding="async"></div>')

def reals_de(s):
    return [r for r in REALISATIONS if r['service'] == s['slug'] or s['filtre'] in r['categories'].split()]

def ph(tag, ton, cls='', style=''):
    return f'<div class="ph {cls}" style="--t:{ton};{style}"><span class="tag">{e(tag)}</span></div>'

def tuile(s, titre_tag='h3'):
    # Dessin du client (WhatsApp, 7 oct.) qui correspond au service
    casq = ' casq' if s.get('rose') else ''
    return (f'<a class="tile dessin{casq} rv" href="/services/{s["slug"]}">'
            f'<div class="art"><img src="/assets/img/{DESSIN_TUILE[s["slug"]]}-blanc.png" alt="" loading="lazy"></div>'
            f'<div class="lab"><div><{titre_tag}>{nom_court(s)}</{titre_tag}><p>{s["court"]}</p></div>'
            f'<span class="go" aria-hidden="true">→</span></div></a>')

def tuile_aide():
    return '''<a class="tile help rv" href="/contact?service=je-sais-pas"><div><h3>Tu sais pas quelle technique choisir?</h3><p>Envoie-nous ton idée. On t’aide à trouver la bonne combinaison de produits et de techniques.</p></div><div class="bas"><span class="go" aria-hidden="true">→</span><img src="/assets/img/illustration-encre-noir.png" alt="" loading="lazy" width="300" height="230"></div></a>'''

def casquettes_custom():
    choix = [('La forme', 'Structurée, dad cap, trucker, cinq panneaux.'),
             ('Les couleurs', 'La couronne, la visière, le bouton, les coutures.'),
             ('Le tissu', 'Coton, sergé, maille, velours côtelé.'),
             ('Ton logo', 'Brodé, en patch ou imprimé, devant, sur le côté ou derrière.'),
             ('Les détails', 'Le dessous de la visière, l’étiquette, la fermeture.')]
    lis = ''.join(f'<li class="rv"><b>{t}</b><span>{d}</span></li>' for t, d in choix)
    return f'''<section class="casq-custom" id="casquettes-custom" aria-labelledby="t-casq">
    <div class="wrap cc">
      <div class="txt">
        <p class="mono rv">Casquettes custom</p>
        <h2 class="h2 rv" id="t-casq">Ta casquette.<br><span class="rose">100 % à ton choix.</span></h2>
        <p class="big rv">Pas juste ton logo sur une casquette déjà faite. On part de zéro et tu choisis chaque morceau.</p>
        <ul class="choix">{lis}</ul>
        <a class="btn btn-rose rv" href="/contact?service=casquettes-tuques">On monte ta casquette <span class="arr">→</span></a>
      </div>
      <div class="art rv"><img src="/assets/img/dessins/bonhomme-casquette-blanc.png" alt="" loading="lazy" width="908" height="1000"></div>
    </div>
  </section>'''

def crumb(chemin):
    morceaux = ['<a href="/">Accueil</a>']
    for u, t in chemin[:-1]:
        morceaux.append(f'<a href="{u}">{t}</a>')
    morceaux.append(f'<span aria-current="page">{chemin[-1][1]}</span>')
    return '<nav class="crumb mono" aria-label="Fil d’Ariane">' + '<span aria-hidden="true">/</span>'.join(morceaux) + '</nav>'

def phead(chemin, titre, intro, ctas='', dessin=None, rose=False):
    fig = f'<img class="fig" src="/assets/img/{dessin}-blanc.png" alt="" aria-hidden="true">' if dessin else ''
    # taille du titre : le plus long mot doit toujours tenir sur une ligne (environ 0,95 em par lettre en majuscules larges)
    mots_t = re.sub(r'<[^>]+>', ' ', H.unescape(titre)).split()
    marge = max(8.0, round(max([len(w) for w in mots_t] or [8]) * 0.95 + 0.5, 1))
    return f'''<section class="phead">
  <div class="wrap">
    {crumb(chemin)}
    <h1 class="x" style="--m:{marge}{";color:var(--rose)" if rose else ""}">{titre}</h1>
    <p class="intro">{intro}</p>
    {f'<div class="ctas">{ctas}</div>' if ctas else ''}
  </div>
  {fig}
  {gouttes()}
</section>'''

def plus_prevoir(plus, prevoir):
    return f'''<div class="pp rv">
      <div class="plus"><span class="lbl mono"><i>+</i>Les plus</span><p>{plus}</p></div>
      <div><span class="lbl mono"><i>!</i>À prévoir</span><p>{prevoir}</p></div>
    </div>'''

def etapes():
    return f'''<section class="how wrap">
    <div class="top">
      <div><p class="mono rv" style="color:var(--mute)">Le processus</p><h2 class="h2 rv" style="margin-top:12px">Comment ça {encre('fonctionne')}</h2>
      <p class="rv">Tu nous expliques ton projet. On choisit les produits et on prépare la soumission. Tu approuves le visuel. On lance la production selon les conditions confirmées.</p></div>
    </div>
    <ol class="steps" style="list-style:none">
      <li style="display:contents"><div class="rv"><span class="dessin"><img src="/assets/img/dessins/bonhomme-surpris-blanc.png" alt="" loading="lazy" width="548" height="1000"></span><b>01</b><p>Tu nous expliques ton projet.</p></div></li>
      <li style="display:contents"><div class="rv"><span class="dessin"><img src="/assets/img/dessins/casquettes-tuques-pile-blanc.png" alt="" loading="lazy" width="1000" height="769"></span><b>02</b><p>On choisit les produits et la technique.</p></div></li>
      <li style="display:contents"><div class="rv"><span class="dessin"><img src="/assets/img/dessins/chandail-loupe-blanc.png" alt="" loading="lazy" width="1000" height="670"></span><b>03</b><p>Tu approuves le visuel et la soumission.</p></div></li>
      <li style="display:contents"><div class="rv"><span class="dessin"><img src="/assets/img/dessins/bonhomme-casquette-blanc.png" alt="" loading="lazy" width="908" height="1000"></span><b>04</b><p>On lance la production.</p></div></li>
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
        'geo': {'@type': 'GeoCoordinates', 'latitude': ENTREPRISE['geo'][0], 'longitude': ENTREPRISE['geo'][1]},
        'hasMap': 'https://www.google.com/maps/search/?api=1&query=' + 'Takedown+Studio+50+chemin+de+Gasp%C3%A9+Bromont',
        'areaServed': [{'@type': 'City', 'name': 'Bromont'}, {'@type': 'AdministrativeArea', 'name': 'Estrie'}],   # régions à confirmer (étape 20)
        **({'sameAs': ENTREPRISE['reseaux']} if ENTREPRISE['reseaux'] else {}),
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
<meta property="og:image:alt" content="Logo de Takedown Studio, agence de branding à Bromont">
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
    tuiles = ''.join(tuile(s) for s in SERVICES)
    corps = f'''{nav('/')}
<main id="contenu">
  <section class="hero hero-dessins" data-intro="/assets/img/logo-complet-lutteurs-blanc-1000.webp">
    <div class="defile" aria-hidden="true"><div class="piste"><div class="groupe"><span class="p p1" style="--n:6;--ar:0.7287;--t:0.72s"><img src="/assets/img/marche/bonhomme-casquette-blanc.png" alt="" width="1311" height="300" loading="lazy"></span><span class="p p2" style="--n:4;--ar:1.2559;--t:0.62s"><img src="/assets/img/marche/deux-tuques-blanc.png" alt="" width="1507" height="300" loading="lazy"></span><span class="p p3" style="--n:6;--ar:0.5248;--t:0.66s"><img src="/assets/img/marche/bonhomme-surpris-blanc.png" alt="" width="944" height="300" loading="lazy"></span><span class="p p4" style="--n:4;--ar:2.1714;--t:0.9s"><img src="/assets/img/marche/bonhomme-couche-blanc.png" alt="" width="2605" height="300" loading="lazy"></span><span class="p p1" style="--n:6;--ar:0.7287;--t:0.72s"><img src="/assets/img/marche/bonhomme-casquette-blanc.png" alt="" width="1311" height="300" loading="lazy"></span><span class="p p2" style="--n:4;--ar:1.2559;--t:0.62s"><img src="/assets/img/marche/deux-tuques-blanc.png" alt="" width="1507" height="300" loading="lazy"></span><span class="p p3" style="--n:6;--ar:0.5248;--t:0.66s"><img src="/assets/img/marche/bonhomme-surpris-blanc.png" alt="" width="944" height="300" loading="lazy"></span><span class="p p4" style="--n:4;--ar:2.1714;--t:0.9s"><img src="/assets/img/marche/bonhomme-couche-blanc.png" alt="" width="2605" height="300" loading="lazy"></span></div><div class="groupe"><span class="p p1" style="--n:6;--ar:0.7287;--t:0.72s"><img src="/assets/img/marche/bonhomme-casquette-blanc.png" alt="" width="1311" height="300" loading="lazy"></span><span class="p p2" style="--n:4;--ar:1.2559;--t:0.62s"><img src="/assets/img/marche/deux-tuques-blanc.png" alt="" width="1507" height="300" loading="lazy"></span><span class="p p3" style="--n:6;--ar:0.5248;--t:0.66s"><img src="/assets/img/marche/bonhomme-surpris-blanc.png" alt="" width="944" height="300" loading="lazy"></span><span class="p p4" style="--n:4;--ar:2.1714;--t:0.9s"><img src="/assets/img/marche/bonhomme-couche-blanc.png" alt="" width="2605" height="300" loading="lazy"></span><span class="p p1" style="--n:6;--ar:0.7287;--t:0.72s"><img src="/assets/img/marche/bonhomme-casquette-blanc.png" alt="" width="1311" height="300" loading="lazy"></span><span class="p p2" style="--n:4;--ar:1.2559;--t:0.62s"><img src="/assets/img/marche/deux-tuques-blanc.png" alt="" width="1507" height="300" loading="lazy"></span><span class="p p3" style="--n:6;--ar:0.5248;--t:0.66s"><img src="/assets/img/marche/bonhomme-surpris-blanc.png" alt="" width="944" height="300" loading="lazy"></span><span class="p p4" style="--n:4;--ar:2.1714;--t:0.9s"><img src="/assets/img/marche/bonhomme-couche-blanc.png" alt="" width="2605" height="300" loading="lazy"></span></div></div></div>
    <h1 class="titre-h1 fade"><span class="l1 x">Agence de branding</span> <span class="l2 mono">Bromont</span></h1>
    <div class="difficiles fade">
      <h2 class="t">On est {encre('difficiles')}.<br><span class="t2">Pour que vous n’ayez pas à l’être.</span></h2>
    </div>
    <p class="sr">Vêtements et produits personnalisés à Bromont. Agence de branding spécialisée en vêtements et produits personnalisés.</p>
  </section>

  <section class="sec wrap" id="services" aria-labelledby="t-services">
    <div class="head">
      <h2 class="h2 rv" id="t-services">Nos {encre('services')}</h2>
      <div class="links rv"><a href="/services">Tous les services <span class="arr">→</span></a></div>
    </div>
    <div class="grid">{tuiles}</div>
  </section>

  {casquettes_custom()}

  {etapes()}

  {mots()}

  <section class="mission" aria-labelledby="t-presentation">
    {photo(4, 'L’atelier de Takedown Studio à Bromont, avec les presses à chaleur et le séchoir de sérigraphie', pos='50% 62%')}
    <div class="wrap in">
      <h2 class="sr" id="t-presentation">L’agence</h2>
      <p class="big rv">On t’aide à mettre ta marque sur des vêtements et des produits que les gens vont aimer utiliser.</p>
      <p class="small rv">Du choix du modèle au placement de ton logo, on te conseille selon ton idée, ton budget et la quantité dont tu as besoin. Broderie, sérigraphie ou impression numérique : on trouve la bonne option pour ton projet.</p>
      <a class="lien rv" href="/agence-branding">Découvrir l’agence <span class="arr">→</span></a>
    </div>
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
    {plus_prevoir('Un même contact pour ton projet, des conseils concrets et des produits qui vont bien ensemble.',
                  'Un projet qui regroupe plusieurs produits demande plus de préparation. Le budget et les délais dépendent des articles choisis.')}
  </section>
  {mots(False)}
  {etapes()}
</main>
{hesite()}
{pied()}'''
    return page('/agence-branding', 'Agence de branding à Bromont | Takedown Studio',
                'Takedown Studio t’aide à donner une image cohérente à tes vêtements et à tes produits : choix des produits, des couleurs, des placements, de la technique.',
                corps, fil=[('/agence-branding', 'L’agence')])

def services_index():
    blocs = ''
    for s in SERVICES:
        phrase = s['texte'].split('. ')[0].rstrip('.') + '.'
        blocs += f'''<article class="svc{' rose' if s.get('rose') else ''} rv">
      <a class="ph art" href="/services/{s['slug']}" tabindex="-1" aria-hidden="true"><img src="/assets/img/{DESSIN_TUILE[s['slug']]}-blanc.png" alt="" loading="lazy"></a>
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

# Types de patches (demande de Takedown, 2026-10-07) : brodé, caoutchouc (rubber / PVC).
# L'étiquette tissée (woven label) est présentée À PART : « pas patch, c'est une étiquette mince » (Takedown, WhatsApp).
# Photos d'exemple envoyées par le client (marque/client-2026-10-07/).
TYPES_PATCHES = [
    dict(nom='Brodé', en='Embroidered', photos=['patch-brode-rose', 'patch-brode-bleu'],
         texte='Ton logo cousu en fil sur une base de tissu. Du relief, des couleurs vives et un contour net. Le classique pour les casquettes et les vestes.'),
    dict(nom='Caoutchouc', en='Rubber / PVC', photos=['patch-caoutchouc'],
         texte='Un patch moulé en caoutchouc souple, avec du relief et une finition durable. Parfait pour un look moderne sur une casquette ou un sac.'),
]
ETIQUETTE = dict(nom='Étiquette tissée', en='Woven label', photo='patch-tisse',
                 texte='Pas un patch : une étiquette mince et souple, tissée avec des fils très fins. Elle est plus plate que la broderie et les petits textes ressortent bien. On la coud au collet, sur une couture ou au bas d’un vêtement, pour signer ta marque comme une marque de vêtements.')

def photo_patch(nom, alt):
    base = f'/assets/img/photos/{nom}'
    return (f'<div class="ph patch"><img src="{base}-1086.webp" srcset="{base}-600.webp 600w, {base}-1086.webp 1086w" '
            f'sizes="(max-width:980px) 100vw, 33vw" alt="{e(alt)}" width="1086" height="607" loading="lazy" decoding="async"></div>')

def types_patches():
    cartes = ''
    for t in TYPES_PATCHES:
        visuel = (photo_patch(t['photos'][0], f'Exemple de patch {t["nom"].lower()}') if t['photos']
                  else ph('Photo à venir', '#2a2420'))
        cartes += f'''<article class="type-patch rv">{visuel}
        <div class="txt"><h3>{t['nom']} <span class="mono">{t['en']}</span></h3><p>{t['texte']}</p></div></article>'''
    x = ETIQUETTE
    etiq = f'''<article class="etiquette rv">{photo_patch(x['photo'], 'Exemple d’étiquette tissée Takedown Studio, une étiquette mince')}
      <div class="txt"><span class="mono">Aussi possible</span><h3>{x['nom']} <span class="mono">{x['en']}</span></h3><p>{x['texte']}</p>
      <p><a class="lien" href="{soum('patches-ecussons')}">Demander une soumission <span class="arr">→</span></a></p></div></article>'''
    return f'''<section class="sec wrap"><div class="head"><h2 class="h2 rv">Les types de patches</h2>
    <p class="note rv">On t’aide à choisir selon ton logo, ton produit et le look que tu veux.</p></div>
    <div class="types-patches">{cartes}</div>{etiq}</section>'''

# 2026-10-24 (Takedown via Alex) : guide de la page Casquettes 100 % personnalisées, un bloc par info
# (même disposition que la page Nos services). Dessins provisoires, texte à retravailler avec Takedown.
GUIDE_CASQUETTES = [
    ('Les formes', 'On part de la forme qui te ressemble.', [
        ('dessins/casquettes-tuques-pile', 'Forme', 'Dad cap', 'Couronne basse et visière courbée, souple et décontractée. Un classique facile à porter, très bien pour la broderie.', None),
        ('dessins/bonhomme-casquette', 'Forme', 'Casquette structurée', 'Couronne haute et rigide qui garde sa forme. Un look net et affirmé, idéal pour un logo bien visible à l’avant.', None),
        ('dessins/casquette-tuque', 'Forme', 'Trucker', 'Panneau avant en mousse et arrière en filet. Légère et aérée, avec un look streetwear. Le logo se place sur le panneau avant.', None),
        ('dessins/casquette-tuque-trait', 'Forme', 'Cinq panneaux', 'Couronne basse faite de cinq panneaux, souvent avec une visière plate. Un style plus moderne, avec beaucoup de place pour jouer avec les couleurs.', None)]),
    ('Les tissus', 'Chaque tissu change le look et le toucher.', [
        ('dessins/casquettes-tuques-pile', 'Tissu', 'Coton', 'Doux, léger et confortable. Un tissu simple qui convient à la plupart des styles.', None),
        ('dessins/bonhomme-casquette', 'Tissu', 'Sergé', 'Du coton tissé en diagonale, plus solide et plus structuré. Se prête bien à la broderie.', None),
        ('dessins/casquette-tuque', 'Tissu', 'Maille', 'Un tissu ajouré et respirant, pour les journées chaudes. On le voit surtout à l’arrière des casquettes trucker.', None),
        ('dessins/casquette-tuque-trait', 'Tissu', 'Velours côtelé', 'Des lignes verticales en relief et un look rétro. Une texture qui se démarque.', None)]),
    ('Ton logo', 'Trois façons de mettre ta marque sur la casquette.', [
        ('dessins/casquettes-tuques-pile', 'Logo', 'Brodé', 'Ton logo cousu directement avec du fil. Du relief, une belle finition et une bonne tenue dans le temps.', None),
        ('dessins/bonhomme-casquette', 'Logo', 'Patch', 'Un écusson fabriqué à part, puis installé sur la casquette. Un look distinctif, devant ou ailleurs.', ('patches-ecussons', 'Voir les patches')),
        ('dessins/casquette-tuque', 'Logo', 'Imprimé', 'Ton visuel imprimé directement sur la casquette, quand le modèle le permet. Bien pour les couleurs et les détails.', None)]),
    ('Les couleurs et les détails', 'Les petites choses qui rendent la casquette vraiment à toi.', [
        ('dessins/casquette-tuque-trait', 'Couleurs', 'Les couleurs', 'La couronne, la visière, le bouton et les coutures peuvent chacun avoir leur couleur. On t’aide à choisir une palette qui va bien avec ton logo.', None),
        ('dessins/casquettes-tuques-pile', 'Détails', 'Les détails', 'La fermeture (snapback, boucle en métal, velcro), le dessous de la visière, l’étiquette tissée : on règle tout ça avec toi.', None)]),
]

def guide_casquettes():
    # Chaque section est un carrousel : un bloc à la fois, qui change aux 3 s (menu défilant, léger sur cell).
    out = ''
    for titre, note, blocs in GUIDE_CASQUETTES:
        arts = ''
        puces = ''
        for n, (dessin, tag, nom, texte, lien) in enumerate(blocs):
            btn = f'<div><a class="btn btn-g" href="/services/{lien[0]}">{lien[1]} <span class="arr">→</span></a></div>' if lien else ''
            arts += f'''<article class="carte-casq">
        <div class="art"><img src="/assets/img/{dessin}-blanc.png" alt="" loading="lazy"></div>
        <div class="lab"><span class="mono">{tag}</span><h3>{nom}</h3><p>{texte}</p>{btn}</div>
      </article>'''
            puces += f'<button type="button" class="chip" aria-pressed="{"true" if n == 0 else "false"}">{nom}</button>'
        out += f'''<section class="sec guide"><div class="wrap"><div class="head"><h2 class="h2 rv">{titre}</h2><p class="note rv">{note}</p></div>
      <div class="chips-g" role="group" aria-label="{titre}">{puces}</div></div>
      <div class="rail-g" style="--n:{len(blocs)}" data-auto="3000" tabindex="0" aria-label="{titre}">{arts}</div></section>'''
    return out

def service(s, i):
    photos = reals_de(s)
    exemples = ''.join(f'<figure class="rv">{photo_real(r)}<figcaption>{r["titre"]}</figcaption></figure>' for r in photos[1:7])
    exemples = (f'<div class="ex">{exemples}</div>' if exemples else '') + \
        '<ul class="ex-liste rv">' + ''.join(f'<li>{x}</li>' for x in s['exemples']) + '</ul>'
    grande = (f'<section class="sec wrap"><figure class="grande rv">{photo_real(photos[0], "(max-width:1200px) 100vw, 1200px")}'
              f'<figcaption class="mono">{photos[0]["titre"]} · {photos[0]["tech"]}</figcaption></figure></section>') if photos else ''
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
    pp = f'<section class="sec wrap">{plus_prevoir(s["plus"], s["prevoir"])}</section>'
    pp_haut = '' if s.get('rose') else pp   # pour les casquettes 100 % : « Les plus / À prévoir » passent sous le guide
    if s.get('rose'):
        bloc_exemples = guide_casquettes() + pp + f'''<section class="sec wrap"><p class="rv"><a class="btn btn-w" href="{soum(s['slug'])}">{s['bouton']} <span class="arr">→</span></a></p></section>'''
    else:
        bloc_exemples = f'''<section class="sec wrap"><div class="head"><h2 class="h2 rv">Exemples</h2>
    <div class="links rv"><a href="/realisations?f={s['filtre']}">Voir les réalisations <span class="arr">→</span></a></div></div>
    {exemples}
    <p class="rv" style="margin-top:40px"><a class="btn btn-w" href="{soum(s['slug'])}">{s['bouton']} <span class="arr">→</span></a></p>
  </section>'''
    ctas = (f'<a class="btn btn-w" href="{soum(s["slug"])}">{s["bouton"]}</a>'
            f'<a class="btn btn-g" href="/realisations?f={s["filtre"]}">Voir les réalisations</a>')
    corps = f'''{nav('/services')}
<main id="contenu">
  {phead([('/services', 'Nos services'), ('/services/' + s['slug'], s['nom'])], s['nom'], s['texte'], ctas, DESSIN_SERVICE.get(s['slug'], DESSINS[i % 3]), rose=bool(s.get('rose')))}
  {grande}
  {pp_haut}
  {types_patches() if s['slug'] == 'patches-ecussons' else ''}
  {bloc_exemples}
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

# 2026-10-26 (Takedown via Alex Moite) : page Catalogue, les produits favoris (promo / basic et premium)
CATALOGUE = json.load(io.open(os.path.join(ICI, 'contenu', 'catalogue.json'), encoding='utf-8'))
CAT_FILTRES = [('tous', 'Tous'), ('tshirt', 'T-shirts'), ('manches-longues', 'Manches longues'), ('crewneck', 'Crewnecks'),
               ('hoodie', 'Hoodies'), ('casquette', 'Casquettes'), ('tuque', 'Tuques'), ('accessoire', 'Accessoires')]
CAT_SLUG = {'T-shirt': 'tshirt', 'Manches longues': 'manches-longues', 'Crewneck': 'crewneck', 'Hoodie': 'hoodie',
            'Casquette': 'casquette', 'Tuque': 'tuque', 'Accessoire': 'accessoire'}

def carte_produit(x):
    ligne_ref = e(x['marque']) + (' · ' + e(x['ref']) if x['ref'] else '')
    lignes = f'<div><dt>Catégorie</dt><dd>{e(x["categorie"])}</dd></div>'
    if x['poids']:
        lignes += f'<div><dt>Poids</dt><dd>{e(x["poids"])}</dd></div>'
    if x['tailles']:
        lignes += f'<div><dt>Tailles</dt><dd>{e(x["tailles"])}</dd></div>'
    plus = f' <em>{e(x["couleurs_plus"])}.</em>' if x['couleurs_plus'] else ''
    return (f'<article class="pcat rv" data-cat="{CAT_SLUG.get(x["categorie"], "autre")}">'
            f'<div class="pimg"><img src="/assets/img/{x["image"]}" alt="{e(x["nom"])}, {e(x["marque"])}" width="720" height="900" loading="lazy"></div>'
            f'<div class="ptxt"><p class="mono">{ligne_ref}</p><h3>{e(x["nom"])}</h3><dl>{lignes}</dl>'
            f'<details><summary>Couleurs ({e(x["couleurs_nb"])})</summary><p>{e(x["couleurs"])}.{plus}</p></details></div></article>')

def catalogue():
    puces = ''.join(f'<button type="button" class="chip" data-cat="{k}" aria-pressed="{"true" if k == "tous" else "false"}">{t}</button>' for k, t in CAT_FILTRES)
    promo = [x for x in CATALOGUE if x['section'] == 'promo']
    prem = [x for x in CATALOGUE if x['section'] == 'premium']
    def bloc(titre, note, liste):
        cartes = ''.join(carte_produit(x) for x in liste)
        return (f'<section class="sec wrap cat-section"><div class="head"><h2 class="h2 rv">{titre}</h2><p class="note rv">{note}</p></div>'
                f'<div class="cat-grid">{cartes}</div></section>')
    corps = f'''{nav('/catalogue')}
<main id="contenu">
  {phead([('/catalogue', 'Catalogue')], 'Notre catalogue',
         'Nos produits favoris, du promo au premium. On en a beaucoup plus : dis-nous ce que tu cherches.',
         '', 'illustration-pinceau')}
  <section class="wrap cat-barre"><p class="rv">Livraison gratuite partout au Canada.</p>
    <div class="chips-cat" role="group" aria-label="Filtrer par catégorie">{puces}</div></section>
  {bloc('Promo / Basic', '21 produits favoris. Les essentiels, sans compromis sur le service.', promo)}
  {bloc('Premium', '12 produits favoris. Des vêtements qui méritent ton logo.', prem)}
  <section class="sec wrap"><div class="cat-fin rv"><h2 class="h2">Tu cherches autre chose?</h2>
    <p>Ces produits sont nos favoris, mais on en a beaucoup plus. Parle-nous de ton projet et on te trouve le bon produit.</p>
    <div class="ctas"><a class="btn btn-w" href="/contact">Demander une soumission <span class="arr">→</span></a><a class="btn btn-g" href="/services">Nos services</a></div></div></section>
</main>
{hesite()}
{pied()}'''
    return page('/catalogue', 'Catalogue de vêtements et de produits personnalisés | Takedown Studio',
                'Les produits favoris de Takedown Studio : t-shirts, crewnecks, hoodies, casquettes, tuques, du promo au premium. On en a beaucoup plus. Demande ta soumission.',
                corps, fil=[('/catalogue', 'Catalogue')])

def realisations():
    presents = {'tous'} | {c for r in REALISATIONS for c in r['categories'].split()}
    chips = ''.join(f'<button class="chip" type="button" data-f="{k}" aria-pressed="{str(k == "tous").lower()}">{t}</button>'
                    for k, t in FILTRES if k in presents)
    items = ''.join(f'''<article class="real rv" data-c="{r['categories']}">
      {photo_real(r)}
      <h3>{r['titre']}</h3>
      <div class="meta mono"><span>{r['produit']}</span><span>{r['tech']}</span></div>
      <a class="lien" href="/services/{r['service']}">{nom_court(PAR_SLUG[r['service']])} <span class="arr">→</span></a>
    </article>''' for r in REALISATIONS)
    insta = f'''<a class="real insta rv" href="{INSTAGRAM}" target="_blank" rel="noopener" data-c="tous">
      <div class="ph"><span class="ig">@takedownstudio</span></div>
      <h3>Nos derniers projets sur Instagram <span class="arr">→</span></h3>
      <div class="meta mono"><span>Broderie</span><span>Sérigraphie</span><span>DTF</span></div>
    </a>'''
    corps = f'''{nav('/realisations')}
<main id="contenu">
  {phead([('/realisations', 'Réalisations')], 'Nos réalisations',
         'Découvre quelques projets réalisés par Takedown Studio. Chaque projet est différent, et la technique utilisée dépend du produit, du visuel, de la quantité et du résultat recherché.',
         '', 'dessins/bonhomme-aiguille')}
  <section class="sec wrap">
    <div class="chips" role="group" aria-label="Filtrer par technique">{chips}</div>
    <div class="reals">{items}{insta}</div>
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
         'Envoie-nous ton idée, ton logo et la quantité que tu as en tête. On va regarder les possibilités avec toi et te guider vers les bons produits et la bonne technique.',
         dessin='dessins/chandail-tache')}
  <section class="wrap formgrid">
    <div>
      <form id="soumission" class="form" action="{API_SOUMISSION}" data-merci="/merci" method="post" enctype="multipart/form-data" novalidate>
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
    <div class="flotte"><img class="mark" src="/assets/img/logo-complet-lutteurs-blanc.png" alt="Takedown Studio" width="1000" height="799" fetchpriority="high"></div>
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

def merci():
    corps = f'''{nav('')}
<main id="contenu">
  {phead([('/merci', 'Demande envoyée')], 'Merci, on a reçu ta demande!',
         'On regarde les informations et les fichiers que tu nous as envoyés, puis on te revient par courriel ou par téléphone pour discuter de ton projet.',
         '<a class="btn btn-w" href="/realisations">Voir nos réalisations</a><a class="btn btn-g" href="/">Retour à l’accueil</a>', 'dessins/bonhomme-casquette')}
</main>
{pied(court=True)}'''
    return page('/merci', 'Demande envoyée | Takedown Studio', 'Ta demande de soumission a bien été envoyée à Takedown Studio.', corps).replace(
        '<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"')

def introuvable():
    corps = f'''{nav('')}
<main id="contenu">
  {phead([('/404', 'Page introuvable')], 'Page introuvable', 'Cette page existe pas ou elle a changé d’adresse.',
         '<a class="btn btn-w" href="/">Retour à l’accueil</a><a class="btn btn-g" href="/services">Nos services</a>', 'dessins/bonhomme-couche')}
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
LARGEURS = {'marche/': (2700,), 'bonhomme': (400, 642), 'logo-complet-lutteurs': (520, 1000), 'logo-texte': (260, 1000), 'illustration': (400, 800), 'services/': (800,), 'dessins/': (360, 720)}
TAILLES = {'bonhomme': '(max-width:600px) 60vw, 380px', 'logo-texte': '130px', 'logo-complet-lutteurs': '(max-width:600px) 88vw, 760px', 'illustration': '(max-width:980px) 180px, 300px',
           'services/': '(max-width:980px) 62vw, 31vw', 'dessins/': '(max-width:600px) 60vw, 320px'}

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
        sizes = m.group(2) or next((v for k, v in TAILLES.items() if nom.startswith(k)), '50vw')
        jeu = ', '.join(f'/assets/img/{nom}-{w}.webp {w}w' for w in ws)
        return f'src="/assets/img/{nom}-{ws[-1]}.webp" srcset="{jeu}" sizes="{sizes}"'
    return re.sub(r'src="/assets/img/((?:services/|dessins/|marche/)?[\w-]+)\.png"(?: sizes="([^"]*)")?', un, html)

# ---------------------------------------------------------------- construction
# Aperçu GitHub Pages : le site vit sous /takedown-studio/, donc on préfixe les adresses
# absolues et on bloque l'indexation (le vrai domaine reste l'URL canonique).
CHEMIN_BASE = os.environ.get('CHEMIN_BASE', '').rstrip('/')

def prefixer(html):
    if not CHEMIN_BASE:
        return html
    import re
    for attr in ('href="/', 'src="/', 'action="/', 'url(/', 'data-intro="/', 'data-merci="/'):
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
             'catalogue.html': catalogue(), 'realisations.html': realisations(), 'contact.html': contact(), 'merci.html': merci(), '404.html': introuvable()}
    for i, s in enumerate(SERVICES):
        pages[f'services/{s["slug"]}.html'] = service(s, i)
    for rel, html in pages.items():
        assert '—' not in html, f'tiret cadratin dans {rel}'
        ecrire(rel, html)

    urls = ['/', '/agence-branding', '/services'] + [f'/services/{s["slug"]}' for s in SERVICES] + ['/catalogue', '/realisations', '/contact']
    ecrire('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
           ''.join(f'  <url><loc>{BASE}{u}</loc><lastmod>{AUJ}</lastmod></url>\n' for u in urls) + '</urlset>\n')
    ecrire('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {BASE}/sitemap.xml\n')
    print(f'✓ {len(pages)} fichiers HTML, {len(urls)} pages dans le sitemap → {SORTIE}')
    if os.environ.get('SANS_CONSTRUCTION'):
        print('· page en construction laissée telle quelle (SANS_CONSTRUCTION)')
    else:
        construire_construction()

def construire_construction():
    """Copie autonome de la page « en construction » dans ../site-construction/ (son propre dépôt GitHub).
    Adresses relatives pour marcher autant sur l'aperçu GitHub que sur www.takedownstudio.com."""
    import re
    dest = os.path.join(os.path.dirname(ICI), 'site-construction')
    os.makedirs(dest, exist_ok=True)
    for n in os.listdir(dest):
        if n in ('.git', '.github', 'CNAME', 'README.md'):
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
