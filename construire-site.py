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
API_SOUMISSION = os.environ.get('API_SOUMISSION', 'https://formsubmit.co/ajax/info@takedownstudio.com')

# Les 3 services de l'étape 15 doivent être validés par Takedown avant la mise en ligne.
AFFICHER_EXTRAS = True

ENTREPRISE = {
    'nom': 'Takedown Studio',
    'tel': '579 488-0321', 'tel_intl': '+15794880321',
    'courriel': 'info@takedownstudio.com',
    'rue': '50, chemin de Gaspé, bloc C, local 5', 'ville': 'Bromont', 'region': 'QC', 'cp': 'J2L 2N8',
    'geo': (45.31643, -72.65788),   # 50 ch. de Gaspé (OpenStreetMap)
    'reseaux': ['https://www.instagram.com/takedownstudio/', 'https://www.facebook.com/profile.php?id=61551481097411'],   # sameAs
}

# ---------------------------------------------------------------- langues
# 2026-10-27 : version anglaise sous /en/. Les pages sont construites deux fois : L = 'fr' puis L = 'en'.
# tr(fr, en) choisit le texte ; le français reste identique à avant.
L = 'fr'          # langue de la page en construction
PAGE_CLE = None   # clé de la page en construction (sélecteur FR / EN et hreflang)

def tr(fr, en):
    return en if L == 'en' else fr

SLUG_EN = {'vetements-personnalises': 'custom-apparel', 'broderie': 'embroidery', 'serigraphie': 'screen-printing',
           'impression-dtf': 'dtf-printing', 'casquettes-tuques': 'custom-caps-beanies', 'patches-ecussons': 'patches',
           'autocollants': 'stickers', 'casquettes-100-personnalisees': '100-custom-caps'}
ROUTES = {'accueil': ('/', '/en/'), 'agence': ('/agence-branding', '/en/agency'), 'services': ('/services', '/en/services'),
          'catalogue': ('/catalogue', '/en/catalogue'), 'realisations': ('/realisations', '/en/our-work'),
          'contact': ('/contact', '/en/contact'), 'merci': ('/merci', '/en/thank-you'),
          'confidentialite': ('/politique-de-confidentialite', '/en/privacy-policy'), 'conditions': ('/conditions-dutilisation', '/en/terms'),
          'ecrire': ('/nous-ecrire', '/en/write-to-us')}

def route_de(cle, langue=None):
    langue = langue or L
    if cle.startswith('svc:'):
        slug = cle[4:]
        return '/en/services/' + SLUG_EN[slug] if langue == 'en' else '/services/' + slug
    return ROUTES[cle][1 if langue == 'en' else 0]

def url_p(cle):
    return route_de(cle)

def url_s(slug):
    return route_de('svc:' + slug)

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
         desc='T-shirts, hoodies, polos et manteaux personnalisés avec ton logo. On t’aide à choisir les vêtements et la technique selon ton budget. Bromont, Estrie, Granby, Sherbrooke, Magog, Montréal.'),
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
def loc(s):
    return dict(s, **SERVICES_EN[s['slug']]) if L == 'en' else s

def svcs():
    return [loc(s) for s in SERVICES]

def nom_court(s):
    s = loc(s)
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

def extras_l():
    return [dict(x, **EXTRAS_EN[x['id']]) if L == 'en' else x for x in EXTRAS]

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
FACEBOOK = 'https://www.facebook.com/profile.php?id=61551481097411'
FILTRES = [('tous', 'Tous'), ('vetements', 'Vêtements'), ('broderie', 'Broderie'), ('serigraphie', 'Sérigraphie'),
           ('dtf', 'DTF'), ('casquettes-tuques', 'Casquettes et tuques'), ('patches', 'Patches'), ('autocollants', 'Autocollants'),
           ('accessoires', 'Accessoires et sacs')]

def choix_service():
    return [('je-sais-pas', tr('Je ne sais pas encore', 'I don’t know yet'))] + [(s['slug'], s['nom']) for s in svcs()] + \
           [('vetements-sport-sublimation', tr('Vêtements de sport et sublimation', 'Sportswear and sublimation')),
            ('produits-sur-mesure', tr('Produits sur mesure', 'Made-to-order products'))]

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
    if L == 'en':
        lignes = [('Thread.', 'fil-aiguille', 'Embroidery<br>Caps, polos', 'Embroidery'),
                  ('Ink.', 'serigraphie-racloir', 'Screen printing<br>In volume', 'Screen printing'),
                  ('Heat.', 'presse-chaleur', 'DTF printing<br>Small batches', 'DTF printing'),
                  ('Your brand.', None, 'Takedown Studio<br>Bromont', 'Takedown Studio')]
    out = ''
    for txt, dessin, long_, court in lignes:
        img = (f'<img class="mini" src="/assets/img/dessins/{dessin}-blanc.png" sizes="160px" alt="" loading="lazy">' if dessin
               else '<img class="mini" src="/assets/img/bonhomme-goutte-blanc.png" sizes="120px" alt="" loading="lazy">')
        out += f'<div class="line x"><span>{txt}</span><span class="cote">{img}<small>{long_ if petits else court}</small></span></div>'
    return f'<section class="words wrap" aria-label="{tr("Nos techniques", "Our techniques")}">{out}</section>'

# ---------------------------------------------------------------- textes anglais (marché canadien, tutoiement devenu « you »)
SERVICES_EN = {
    'vetements-personnalises': dict(nom='Custom apparel', tag='T-shirts, hoodies, polos',
        court='The right garments for your project, with your logo.',
        texte='T-shirts, hoodies, crewnecks, polos or jackets: we help you pick the right garments for your project. We look at fit, comfort and budget, then add your logo with the technique that suits it best. Whether you are outfitting your team or creating merch, we guide you from start to finish.',
        plus='Lots of choice, several price ranges and garments suited to how you plan to use them.',
        prevoir='Sizes, colours and stock vary by style. A small order usually costs more per piece.',
        exemples=['Company T-shirts', 'Branded hoodies', 'Embroidered polos', 'Workwear'],
        bouton='Request a quote for custom apparel',
        seo='Custom apparel with your logo in Bromont | Takedown Studio',
        desc='Custom T-shirts, hoodies, polos and jackets with your logo. We help you choose the garments and the technique to fit your budget. Bromont, Eastern Townships, Granby, Sherbrooke, Magog, Montréal.'),
    'broderie': dict(nom='Embroidery', tag='Close-up · thread and texture',
        court='Your logo stitched into the garment, with texture.',
        texte='Embroidery is your logo stitched straight into the garment with thread. It gives texture and a clean finish. It is a great fit for caps, beanies, polos, crewnecks and jackets.',
        plus='A polished look, a raised texture and good durability when the garment is cared for properly.',
        prevoir='Small text and very fine details may need to be simplified. A large, filled-in logo takes more stitches and costs more. Some very thin fabrics are not a good match.',
        exemples=['Logo on the chest', 'Embroidered cap', 'Beanie with embroidery', 'Embroidered polo', 'Custom jacket'],
        bouton='Request a quote for embroidery',
        seo='Custom embroidery in Bromont | Takedown Studio',
        desc='Logo embroidery on caps, beanies, polos, crewnecks and jackets. A polished look with texture. Request your quote from Takedown Studio, Bromont.'),
    'serigraphie': dict(nom='Screen printing', tag='Screen and ink',
        court='A great finish that gets more affordable in volume.',
        texte='Screen printing is ink printed straight onto the garment using screens. Each colour needs its own setup. It is a great option when you want several pieces with the same design, especially if your design has few colours.',
        plus='A great finish, solid durability with proper care and a price per piece that gets attractive in volume.',
        prevoir='Setup costs more on small orders. The number of colours and the print locations change the price.',
        exemples=['Team T-shirts', 'Event merch', 'Printed hoodies', 'One-colour print', 'Multicolour print'],
        bouton='Request a quote for screen printing',
        seo='Screen printing on apparel in Bromont | Takedown Studio',
        desc='Screen printing on T-shirts and hoodies for your team, your event or your merch. A great ink finish that gets attractive in volume. Takedown Studio, Bromont.'),
    'impression-dtf': dict(nom='DTF digital printing', tag='Multicolour artwork',
        court='Lots of colour and detail, even in small quantities.',
        texte='DTF is your artwork printed on a film, then transferred onto the garment with a heat press. It works well for small quantities and for images with several colours and gradients.',
        plus='Lots of colours in the same design, good reproduction of detail and a practical option for small projects.',
        prevoir='You can feel the print on the fabric. A large solid design can be thicker and less breathable. File quality and following the washing instructions matter a lot.',
        exemples=['Multicolour T-shirt', 'Small batch of garments', 'Sample before a bigger order', 'Design with a gradient', 'Detailed logo'],
        bouton='Request a quote for DTF printing',
        seo='DTF printing on apparel | Takedown Studio',
        desc='DTF digital printing on apparel: lots of colour, gradients and detail, even for a small batch. Request your quote from Takedown Studio.'),
    'casquettes-tuques': dict(nom='Custom caps and beanies', court_nom='Caps and beanies', tag='Embroidered dad cap',
        court='Embroidered, with a patch or printed, depending on the style.',
        texte='We help you pick the right cap or beanie for the style you want. Then we look at how to add your logo: embroidery, patch or printing when the style allows it.',
        plus='An easy-to-wear accessory, a logo that stands out and plenty of styles to represent your brand.',
        prevoir='Space for the logo is limited. Seams, the shape of the cap and the knit of a beanie may mean adapting the design. Minimums vary by method.',
        exemples=['Dad caps', 'Structured caps', 'Custom beanies', 'Embroidered caps', 'Caps with a patch'],
        bouton='Request a quote for caps or beanies',
        seo='Custom caps and beanies | Takedown Studio',
        desc='Caps and beanies with your logo: embroidery, patch or printing depending on the style. Dad caps, structured caps, beanies. Takedown Studio, Bromont.'),
    'patches-ecussons': dict(nom='Custom patches', tag='Patch on a jacket',
        court='Your logo or a name, as a badge.',
        texte='A patch is a custom badge we add to a cap, a shirt, a jacket or another compatible product. It is a great way to give your logo a different look or to add a name to a garment.',
        plus='A distinctive look, several finishing options and a good fit for names or logos in badge format.',
        prevoir='Small details sometimes need to be adapted to the type of patch. Making and applying the patch are two steps to plan for in price and timeline.',
        exemples=['Logo patch', 'Name badge', 'Cap with a patch', 'Iron-on patch', 'Sewn-on patch'],
        bouton='Request a quote for patches',
        seo='Custom patches | Takedown Studio',
        desc='Custom patches for caps, shirts and jackets. Your logo or a name in badge format. Request your quote from Takedown Studio.'),
    'autocollants': dict(nom='Custom stickers', tag='Stickers on packaging',
        court='For your packaging, your orders and your events.',
        texte='We have your stickers made with your logo or artwork. For packaging, orders or events, we help you pick the size and finish for how you will use them.',
        plus='Easy to hand out, handy for personalizing your packaging and available in different sizes.',
        prevoir='Size, material and finish affect the price. For outdoor use, water or a specific surface, you need a suitable material and adhesive.',
        exemples=['Logo stickers', 'Packaging seals', 'Stickers included with an order', 'Event stickers', 'Outdoor-resistant stickers'],
        bouton='Request a quote for stickers',
        seo='Custom stickers with your logo | Takedown Studio',
        desc='Custom stickers with your logo for your packaging, orders and events. We help you pick the size and finish. Bromont.'),
    'casquettes-100-personnalisees': dict(nom='100% custom caps', tag='Made-to-order cap',
        court='Shape, colours, fabric, logo: we build it from A to Z, your way.',
        texte='Not just your logo on a ready-made cap. We start from scratch and you choose every piece: the shape, the colours, the fabric and the logo. We build the cap with you, from A to Z.',
        plus='A one-of-a-kind cap designed for your brand, with the shape, colours, fabric and logo you choose.',
        prevoir='A made-to-order project takes more preparation than a catalogue cap. Minimums, timelines and price depend on the shape, fabric and method you choose, and we confirm them in your quote.',
        exemples=['Shape: structured, dad cap, trucker, five-panel', 'Colours of the crown, the visor and the stitching', 'Fabric: cotton, twill, mesh, corduroy', 'Logo embroidered, as a patch or printed', 'Details: under the visor, label, closure'],
        bouton='Request a quote for a made-to-order cap',
        seo='100% custom caps | Takedown Studio',
        desc='100% custom caps: shape, colours, fabric and logo, we build it from A to Z your way. Request your quote from Takedown Studio, Bromont.'),
}

EXTRAS_EN = {
    'sublimation': dict(titre='Sportswear and sublimation',
        texte='For your sports team, we can help you order custom jerseys and sets from our partners. Sublimation works the colours and artwork into a compatible fabric, often polyester.',
        plus='Lots of freedom in the design and a pattern that does not leave a thick layer on the fabric.',
        prevoir='Fabrics, styles, minimums and timelines depend on the manufacturing program. This process is not suited to every garment.'),
    'sur-mesure': dict(titre='Made-to-order products',
        texte='Looking for something outside the usual catalogue? We can explore the options with our partners to develop a product that reflects you, like socks, sandals or custom accessories.',
        plus='A product that stands out and more room for customization, depending on the manufacturer.',
        prevoir='Often higher minimums, longer timelines and sometimes sample or development fees.'),
    'fiches-techniques': dict(titre='Tech packs and production prep',
        texte='We gather the information needed to explain your project to the manufacturer: dimensions, colours, placements and customization details. The goal is for everything to be clear before production.',
        plus='Fewer grey areas and a reference document to follow the project.',
        prevoir='Product details need to be confirmed. A tech pack does not replace a sample when one is needed.'),
}

TYPES_PATCHES_EN = [
    dict(nom='Embroidered', en='', texte='Your logo stitched in thread on a fabric base. Texture, vivid colours and a crisp edge. The classic for caps and jackets.'),
    dict(nom='Rubber / PVC', en='', texte='A moulded patch in soft rubber, with texture and a durable finish. Great for a modern look on a cap or a bag.'),
]
ETIQUETTE_EN = dict(nom='Woven label', en='',
    texte='Not a patch: a thin, soft label woven with very fine threads. It is flatter than embroidery and small text stands out well. We sew it on at the collar, on a seam or at the bottom of a garment, to sign your brand like a clothing brand.')

GUIDE_CASQUETTES_EN = [
    ('Shapes', 'We start from the shape that suits you.', [
        ('Shape', 'Dad cap', 'Low crown and curved visor, soft and relaxed. An easy-to-wear classic, great for embroidery.', None),
        ('Shape', 'Structured cap', 'High, rigid crown that holds its shape. A sharp, confident look, ideal for a logo that stands out on the front.', None),
        ('Shape', 'Trucker', 'Foam front panel and mesh back. Light and airy, with a streetwear look. The logo goes on the front panel.', None),
        ('Shape', 'Five-panel', 'Low crown made of five panels, often with a flat visor. A more modern style, with lots of room to play with colour.', None)]),
    ('Fabrics', 'Each fabric changes the look and the feel.', [
        ('Fabric', 'Cotton', 'Soft, light and comfortable. A simple fabric that suits most styles.', None),
        ('Fabric', 'Twill', 'Cotton woven on a diagonal, sturdier and more structured. Works well for embroidery.', None),
        ('Fabric', 'Mesh', 'An open, breathable fabric for hot days. Mostly seen at the back of trucker caps.', None),
        ('Fabric', 'Corduroy', 'Raised vertical lines and a retro look. A texture that stands out.', None)]),
    ('Your logo', 'Three ways to put your brand on the cap.', [
        ('Logo', 'Embroidered', 'Your logo stitched straight on with thread. Texture, a polished finish and good staying power.', None),
        ('Logo', 'Patch', 'A badge made separately, then attached to the cap. A distinctive look, on the front or elsewhere.', 'See patches'),
        ('Logo', 'Printed', 'Your artwork printed straight onto the cap, when the style allows it. Good for colour and detail.', None)]),
    ('Colours and details', 'The little things that make the cap truly yours.', [
        ('Colours', 'The colours', 'The crown, the visor, the button and the stitching can each have their own colour. We help you pick a palette that goes well with your logo.', None),
        ('Details', 'The details', 'The closure (snapback, metal buckle, velcro), the underside of the visor, the woven label: we sort all that out with you.', None)]),
]

CAT_EN = {'T-shirt': 'T-shirt', 'Manches longues': 'Long sleeve', 'Crewneck': 'Crewneck', 'Hoodie': 'Hoodie', 'Veste': 'Jacket',
          'Pantalon': 'Pants', 'Casquette': 'Cap', 'Tuque': 'Beanie', 'Accessoire': 'Accessory'}
CAT_TITRES_EN = {'T-shirt': 'T-shirts', 'Manches longues': 'Long sleeves', 'Crewneck': 'Crewnecks', 'Hoodie': 'Hoodies', 'Veste': 'Jackets',
                 'Pantalon': 'Pants', 'Casquette': 'Caps', 'Tuque': 'Beanies', 'Accessoire': 'Accessories'}
CAT_FILTRES_EN = {'tous': 'All', 'tshirt': 'T-shirts', 'manches-longues': 'Long sleeves', 'crewneck': 'Crewnecks', 'hoodie': 'Hoodies',
                  'veste': 'Jackets', 'pantalon': 'Pants', 'casquette': 'Caps', 'tuque': 'Beanies', 'accessoire': 'Accessories'}

def t_tailles(t):
    if L != 'en':
        return t
    return (t.replace(' à ', ' to ').replace('Taille unique', 'One size').replace('ajustable', 'adjustable')
             .replace('dans certaines couleurs seulement', 'in some colours only'))

def t_poids(p):
    if L != 'en':
        return p
    p = re.sub(r'(\d),(\d)', r'\1.\2', p)
    return (p.replace(' à ', ' to ').replace('g/m²', 'gsm').replace('oz/vg²', 'oz/yd²')
             .replace('poids de l’article', 'item weight'))

def t_nb(n):
    return n.replace('Sélection de', 'Selection of').replace('Sélection', 'Selection') if L == 'en' else n

def t_plus(p):
    if L != 'en':
        return p
    m = re.match(r'(Plus de |Environ )?(\d+) couleurs offertes', p)
    if not m:
        return p
    pre = {'Plus de ': '', 'Environ ': 'About '}.get(m.group(1) or '', '')
    suf = '+' if m.group(1) == 'Plus de ' else ''
    return f'{pre}{m.group(2)}{suf} colours available'

# ---------------------------------------------------------------- morceaux communs
MENU = [('accueil', 'Accueil', 'Home'), ('agence', 'L’agence', 'About'), ('services', 'Nos services', 'Services'),
        ('svc:casquettes-100-personnalisees', 'Casquettes custom', 'Custom caps'), ('catalogue', 'Catalogue', 'Catalogue'),
        ('realisations', 'Réalisations', 'Our work'), ('contact', 'Contact', 'Contact')]

def soum(slug=None):
    return url_p('contact') + (f'?service={slug}' if slug else '')

def lien_langue():
    # adresse de la même page dans l'autre langue (sélecteur FR / EN)
    autre = 'fr' if L == 'en' else 'en'
    cible = route_de(PAGE_CLE, autre) if PAGE_CLE else route_de('accueil', autre)
    return cible, autre

def nav(courant):
    liens = ''
    mob = ''
    for cle, t_fr, t_en in MENU:
        href = route_de(cle)
        actif = ' aria-current="page"' if route_de(cle, 'fr') == courant else ''
        rose = ' class="rose"' if 'casquettes' in cle else ''
        titre = tr(t_fr, t_en)
        liens += f'<li><a href="{href}"{actif}{rose}>{titre}</a></li>'
        mob += f'<a href="{href}"{rose}>{titre}</a>'
    cible, autre = lien_langue()
    sel_h = f'<a class="lang" href="{cible}" hreflang="{autre}" lang="{autre}" aria-label="{tr("English version", "Version française")}">{autre.upper()}</a>'
    sel_m = f'<a class="lang-m" href="{cible}" hreflang="{autre}" lang="{autre}">{tr("English", "Français")}</a>'
    return f'''<a class="skip" href="#contenu">{tr('Aller au contenu', 'Skip to content')}</a>
<header class="nav">
  <div class="wrap">
    <a class="logo" href="{url_p('accueil')}" aria-label="{tr('Takedown Studio, accueil', 'Takedown Studio, home')}"><img src="/assets/img/logo-texte-blanc.png" alt="Takedown Studio" width="130" height="17"></a>
    <nav aria-label="{tr('Menu principal', 'Main menu')}"><ul>{liens}</ul></nav>
    <div class="right">{sel_h}<a class="btn btn-w" href="{url_p('contact')}"><span class="lg">{tr('Demander une&nbsp;', 'Request a&nbsp;')}</span>{tr('soumission', 'quote')}</a><button class="burger" aria-label="{tr('Ouvrir le menu', 'Open the menu')}" aria-expanded="false" aria-controls="menu-m"><span></span><span></span></button></div>
  </div>
</header>
<nav class="menu-m" id="menu-m" aria-label="{tr('Menu cellulaire', 'Mobile menu')}">{mob}{sel_m}<a class="btn btn-w" href="{url_p('contact')}">{tr('Demander une soumission', 'Request a quote')}</a></nav>'''

def ville_cp():
    return tr(f"{ENTREPRISE['ville']} (Québec) {ENTREPRISE['cp']}", f"{ENTREPRISE['ville']}, Quebec {ENTREPRISE['cp']}")

def pied(court=False, lien_courriel=None):
    services = ''.join(f'<a href="{url_s(s["slug"])}">{nom_court(s)}</a>' for s in svcs())
    cible, autre = lien_langue()
    tete = '' if court else f'''<p class="mono" style="color:var(--mute)">{tr('Demander une soumission', 'Request a quote')}</p>
        <h2 class="x rv"><span class="ind">{tr('On regarde ton', 'Let’s look at your')}</span><br>{tr('projet', 'project')} {encre(tr('ensemble!', 'together!'))}</h2>'''
    appel = '' if court else f'''<div>
            <p>{tr('Envoie-nous ton idée, ton logo et la quantité que tu as en tête. On va te guider pour la suite.', 'Send us your idea, your logo and the quantity you have in mind. We will guide you from there.')}</p>
            <a class="btn btn-w" href="{url_p('contact')}">{tr('Demander une soumission', 'Request a quote')} <span class="arr">→</span></a>
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
            <div><h4>Studio</h4><a href="{url_p('agence')}">{tr('L’agence', 'About')}</a><a href="{url_p('catalogue')}">Catalogue</a><a href="{url_p('realisations')}">{tr('Réalisations', 'Our work')}</a><a href="{url_p('contact')}">Contact</a><a href="{cible}" hreflang="{autre}" lang="{autre}">{tr('English version', 'Version française')}</a>
              <h4 style="margin-top:22px">{tr('Nous joindre', 'Get in touch')}</h4><a href="tel:{ENTREPRISE['tel_intl']}">{ENTREPRISE['tel']}</a><a href="{lien_courriel or 'mailto:' + ENTREPRISE['courriel']}">{ENTREPRISE['courriel']}</a><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a><a href="{FACEBOOK}" target="_blank" rel="noopener">Facebook</a></div>
          </div>
        </div>
      </div>
    </div>
    <div class="legal">
      <img src="/assets/img/logo-texte-blanc.png" alt="Takedown Studio" width="122" height="16" loading="lazy">
      <span>{ENTREPRISE['rue']}, {ville_cp()}</span>
      <span class="liens-legaux"><a href="{url_p('confidentialite')}">{tr('Politique de confidentialité', 'Privacy policy')}</a> · <a href="{url_p('conditions')}">{tr('Conditions d’utilisation', 'Terms of use')}</a></span>
      <span>© {AUJ[:4]} Takedown Studio{tr(' · Site par Scalera', ' · Website by Scalera')}</span>
    </div>
  </div>
</footer>'''

def hesite():
    return f'''<section class="hesite">
  {gouttes('coule gauche')}
  <div class="wrap">
    <div><h2 class="x rv">{tr('Tu hésites entre plusieurs options?', 'Not sure which option to pick?')}</h2>
    <p class="rv">{tr('Envoie-nous ton idée et les informations que tu as. On va t’aider à choisir la bonne combinaison de produits et de techniques.', 'Send us your idea and whatever information you have. We will help you choose the right mix of products and techniques.')}</p></div>
    <img class="duo rv" src="/assets/img/dessins/deux-tuques-blanc.png" alt="" loading="lazy" width="1000" height="640">
    <a class="btn btn-w rv" href="{url_p('contact')}">{tr('Demander une soumission', 'Request a quote')} <span class="arr">→</span></a>
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
    s = loc(s)
    casq = ' casq' if s.get('rose') else ''
    return (f'<a class="tile dessin{casq} rv" href="{url_s(s["slug"])}">'
            f'<div class="art"><img src="/assets/img/{DESSIN_TUILE[s["slug"]]}-blanc.png" alt="" loading="lazy"></div>'
            f'<div class="lab"><div><{titre_tag}>{nom_court(s)}</{titre_tag}><p>{s["court"]}</p></div>'
            f'<span class="go" aria-hidden="true">→</span></div></a>')

def tuile_aide():
    return '''<a class="tile help rv" href="/contact?service=je-sais-pas"><div><h3>Tu sais pas quelle technique choisir?</h3><p>Envoie-nous ton idée. On t’aide à trouver la bonne combinaison de produits et de techniques.</p></div><div class="bas"><span class="go" aria-hidden="true">→</span><img src="/assets/img/illustration-encre-noir.png" alt="" loading="lazy" width="300" height="230"></div></a>'''

def casquettes_custom():
    choix = [(tr('La forme', 'The shape'), tr('Structurée, dad cap, trucker, cinq panneaux.', 'Structured, dad cap, trucker, five-panel.')),
             (tr('Les couleurs', 'The colours'), tr('La couronne, la visière, le bouton, les coutures.', 'The crown, the visor, the button, the stitching.')),
             (tr('Le tissu', 'The fabric'), tr('Coton, sergé, maille, velours côtelé.', 'Cotton, twill, mesh, corduroy.')),
             (tr('Ton logo', 'Your logo'), tr('Brodé, en patch ou imprimé, devant, sur le côté ou derrière.', 'Embroidered, as a patch or printed, on the front, the side or the back.')),
             (tr('Les détails', 'The details'), tr('Le dessous de la visière, l’étiquette, la fermeture.', 'Under the visor, the label, the closure.'))]
    lis = ''.join(f'<li class="rv"><b>{t}</b><span>{d}</span></li>' for t, d in choix)
    return f'''<section class="casq-custom" id="casquettes-custom" aria-labelledby="t-casq">
    <div class="wrap cc">
      <div class="txt">
        <p class="mono rv">{tr('Casquettes custom', 'Custom caps')}</p>
        <h2 class="h2 rv" id="t-casq">{tr('Ta casquette.', 'Your cap.')}<br><span class="rose">{tr('100 % à ton choix.', '100% your choice.')}</span></h2>
        <p class="big rv">{tr('Pas juste ton logo sur une casquette déjà faite. On part de zéro et tu choisis chaque morceau.', 'Not just your logo on a ready-made cap. We start from scratch and you choose every piece.')}</p>
        <ul class="choix">{lis}</ul>
        <a class="btn btn-rose rv" href="{url_p('contact')}?service=casquettes-tuques">{tr('On monte ta casquette', 'We build your cap')} <span class="arr">→</span></a>
      </div>
      <div class="art rv"><img src="/assets/img/dessins/bonhomme-casquette-blanc.png" alt="" loading="lazy" width="908" height="1000"></div>
    </div>
  </section>'''

def crumb(chemin):
    morceaux = [f'<a href="{url_p("accueil")}">{tr("Accueil", "Home")}</a>']
    for u, t in chemin[:-1]:
        morceaux.append(f'<a href="{u}">{t}</a>')
    morceaux.append(f'<span aria-current="page">{chemin[-1][1]}</span>')
    return f'<nav class="crumb mono" aria-label="{tr("Fil d’Ariane", "Breadcrumb")}">' + '<span aria-hidden="true">/</span>'.join(morceaux) + '</nav>'

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
      <div class="plus"><span class="lbl mono"><i>+</i>{tr('Les plus', 'The upsides')}</span><p>{plus}</p></div>
      <div><span class="lbl mono"><i>!</i>{tr('À prévoir', 'Keep in mind')}</span><p>{prevoir}</p></div>
    </div>'''

def etapes():
    return f'''<section class="how wrap">
    <div class="top">
      <div><p class="mono rv" style="color:var(--mute)">{tr('Le processus', 'The process')}</p><h2 class="h2 rv" style="margin-top:12px">{tr('Comment ça', 'How it')} {encre(tr('fonctionne', 'works'))}</h2>
      <p class="rv">{tr('Tu nous expliques ton projet. On choisit les produits et on prépare la soumission. Tu approuves le visuel. On lance la production selon les conditions confirmées.', 'You tell us about your project. We pick the products and prepare the quote. You approve the visual. We start production under the confirmed terms.')}</p></div>
    </div>
    <ol class="steps" style="list-style:none">
      <li style="display:contents"><div class="rv"><span class="dessin"><img src="/assets/img/dessins/bonhomme-surpris-blanc.png" alt="" loading="lazy" width="548" height="1000"></span><b>01</b><p>{tr('Tu nous expliques ton projet.', 'You tell us about your project.')}</p></div></li>
      <li style="display:contents"><div class="rv"><span class="dessin"><img src="/assets/img/dessins/casquettes-tuques-pile-blanc.png" alt="" loading="lazy" width="1000" height="769"></span><b>02</b><p>{tr('On choisit les produits et la technique.', 'We pick the products and the technique.')}</p></div></li>
      <li style="display:contents"><div class="rv"><span class="dessin"><img src="/assets/img/dessins/chandail-loupe-blanc.png" alt="" loading="lazy" width="1000" height="670"></span><b>03</b><p>{tr('Tu approuves le visuel et la soumission.', 'You approve the visual and the quote.')}</p></div></li>
      <li style="display:contents"><div class="rv"><span class="dessin"><img src="/assets/img/dessins/bonhomme-casquette-blanc.png" alt="" loading="lazy" width="908" height="1000"></span><b>04</b><p>{tr('On lance la production.', 'We start production.')}</p></div></li>
    </ol>
  </section>'''

# ---------------------------------------------------------------- SEO
def entreprise_ld():
    return {
        '@type': 'ProfessionalService', '@id': BASE + '/#entreprise', 'name': ENTREPRISE['nom'],
        'description': tr('Agence de branding spécialisée en vêtements et produits personnalisés à Bromont.', 'Branding agency specializing in custom apparel and products in Bromont.'),
        'url': BASE + '/', 'logo': BASE + '/assets/img/icone-512.png', 'image': BASE + '/assets/img/partage.png',
        'telephone': ENTREPRISE['tel_intl'], 'email': ENTREPRISE['courriel'],
        'address': {'@type': 'PostalAddress', 'streetAddress': ENTREPRISE['rue'], 'addressLocality': ENTREPRISE['ville'],
                    'addressRegion': ENTREPRISE['region'], 'postalCode': ENTREPRISE['cp'], 'addressCountry': 'CA'},
        'geo': {'@type': 'GeoCoordinates', 'latitude': ENTREPRISE['geo'][0], 'longitude': ENTREPRISE['geo'][1]},
        'hasMap': 'https://www.google.com/maps/search/?api=1&query=' + 'Takedown+Studio+50+chemin+de+Gasp%C3%A9+Bromont',
        'areaServed': [{'@type': 'City', 'name': 'Bromont'}, {'@type': 'AdministrativeArea', 'name': 'Estrie'}, {'@type': 'City', 'name': 'Granby'}, {'@type': 'City', 'name': 'Sherbrooke'}, {'@type': 'City', 'name': 'Magog'}, {'@type': 'City', 'name': 'Montréal'}],   # régions à confirmer (étape 20)
        **({'sameAs': ENTREPRISE['reseaux']} if ENTREPRISE['reseaux'] else {}),
        'knowsAbout': [s['nom'] for s in svcs()],
    }

DETECTION_LANGUE = """<script>(function(){try{
if(/bot|crawl|spider|slurp|facebookexternalhit|lighthouse|preview/i.test(navigator.userAgent))return;
if(location.search)return;
if(localStorage.getItem('langue'))return;
var l=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||''];
for(var i=0;i<l.length;i++){var c=String(l[i]).toLowerCase().slice(0,2);
if(c==='fr')return;
if(c==='en'){var a=document.querySelector('link[hreflang="en-CA"]');if(a)location.replace(a.href);return}}
}catch(x){}})()</script>"""

def page(chemin_url, titre_seo, desc, corps, fil=None, extra_ld=None, js=True):
    url = BASE + (chemin_url if chemin_url != '/' else '/')
    graph = [entreprise_ld(), {'@type': 'WebPage', '@id': url + '#page', 'url': url, 'name': titre_seo,
                                'description': desc, 'inLanguage': tr('fr-CA', 'en-CA'), 'isPartOf': {'@id': BASE + '/#site'},
                                'about': {'@id': BASE + '/#entreprise'}},
             {'@type': 'WebSite', '@id': BASE + '/#site', 'url': BASE + '/', 'name': 'Takedown Studio', 'inLanguage': tr('fr-CA', 'en-CA')}]
    if fil:
        items = [{'@type': 'ListItem', 'position': 1, 'name': tr('Accueil', 'Home'), 'item': BASE + url_p('accueil')}]
        for i, (u, t) in enumerate(fil, start=2):
            items.append({'@type': 'ListItem', 'position': i, 'name': H.unescape(t), 'item': BASE + u})
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': items})
    if extra_ld:
        graph += extra_ld
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False)
    detection = DETECTION_LANGUE if (PAGE_CLE == 'accueil' and L == 'fr') else ''
    alternates = ''
    if PAGE_CLE:
        alternates = (f'<link rel="alternate" hreflang="fr-CA" href="{BASE}{route_de(PAGE_CLE, "fr")}">'
                      f'<link rel="alternate" hreflang="en-CA" href="{BASE}{route_de(PAGE_CLE, "en")}">'
                      f'<link rel="alternate" hreflang="x-default" href="{BASE}{route_de(PAGE_CLE, "fr")}">')
    return f'''<!doctype html>
<html lang="{tr('fr-CA', 'en-CA')}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre_seo)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">{alternates}
<meta name="theme-color" content="#000000">
<meta property="og:type" content="website">
<meta property="og:locale" content="{tr('fr_CA', 'en_CA')}">
<meta property="og:locale:alternate" content="{tr('en_CA', 'fr_CA')}">
<meta property="og:site_name" content="Takedown Studio">
<meta property="og:title" content="{e(titre_seo)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/img/partage.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{tr('Logo de Takedown Studio, agence de branding à Bromont', 'Takedown Studio logo, a branding agency in Bromont')}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/img/icone-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/assets/img/icone-180.png">
<link rel="preload" href="/assets/polices/archivo-400-800.woff2" as="font" type="font/woff2" crossorigin>
<style>{CSS}</style>
<script>if(!location.search.includes('apercu'))document.documentElement.classList.add('js')</script>
{detection}
<script type="application/ld+json">{ld}</script>
</head>
<body>
{corps}
{'<script src="/assets/site.js?v=' + V + '" defer></script>' if js else ''}
</body>
</html>
'''

# ---------------------------------------------------------------- pages
def zones():
    """SEO local : zones desservies (texte visible, sans changer la mise en page)."""
    return f'''<section class="sec wrap" aria-labelledby="t-zones">
    <div class="head"><h2 class="h2 rv" id="t-zones">{tr('Zones desservies', 'Areas we serve')}</h2></div>
    <p class="note rv">{tr('Takedown Studio est à Bromont. On sert l’Estrie, dont Granby, Sherbrooke et Magog, ainsi que Montréal et partout au Québec. Dis-nous où tu es, on s’occupe du reste.', 'Takedown Studio is based in Bromont. We serve the Eastern Townships, including Granby, Sherbrooke and Magog, as well as Montréal and clients all across Québec. Tell us where you are and we will take care of the rest.')}</p>
  </section>'''

def accueil():
    tuiles = ''.join(tuile(s) for s in SERVICES)
    corps = f'''{nav('/')}
<main id="contenu">
  <section class="hero hero-dessins" data-intro="/assets/img/logo-complet-lutteurs-blanc-1000.webp">
    <div class="defile" aria-hidden="true"><div class="piste"><div class="groupe"><span class="p p1" style="--n:6;--ar:0.7287;--t:0.72s"><img src="/assets/img/marche/bonhomme-casquette-blanc.png" alt="" width="1311" height="300" loading="lazy"></span><span class="p p2" style="--n:4;--ar:1.2559;--t:0.62s"><img src="/assets/img/marche/deux-tuques-blanc.png" alt="" width="1507" height="300" loading="lazy"></span><span class="p p3" style="--n:6;--ar:0.5248;--t:0.66s"><img src="/assets/img/marche/bonhomme-surpris-blanc.png" alt="" width="944" height="300" loading="lazy"></span><span class="p p4" style="--n:4;--ar:2.1714;--t:0.9s"><img src="/assets/img/marche/bonhomme-couche-blanc.png" alt="" width="2605" height="300" loading="lazy"></span><span class="p p1" style="--n:6;--ar:0.7287;--t:0.72s"><img src="/assets/img/marche/bonhomme-casquette-blanc.png" alt="" width="1311" height="300" loading="lazy"></span><span class="p p2" style="--n:4;--ar:1.2559;--t:0.62s"><img src="/assets/img/marche/deux-tuques-blanc.png" alt="" width="1507" height="300" loading="lazy"></span><span class="p p3" style="--n:6;--ar:0.5248;--t:0.66s"><img src="/assets/img/marche/bonhomme-surpris-blanc.png" alt="" width="944" height="300" loading="lazy"></span><span class="p p4" style="--n:4;--ar:2.1714;--t:0.9s"><img src="/assets/img/marche/bonhomme-couche-blanc.png" alt="" width="2605" height="300" loading="lazy"></span></div><div class="groupe"><span class="p p1" style="--n:6;--ar:0.7287;--t:0.72s"><img src="/assets/img/marche/bonhomme-casquette-blanc.png" alt="" width="1311" height="300" loading="lazy"></span><span class="p p2" style="--n:4;--ar:1.2559;--t:0.62s"><img src="/assets/img/marche/deux-tuques-blanc.png" alt="" width="1507" height="300" loading="lazy"></span><span class="p p3" style="--n:6;--ar:0.5248;--t:0.66s"><img src="/assets/img/marche/bonhomme-surpris-blanc.png" alt="" width="944" height="300" loading="lazy"></span><span class="p p4" style="--n:4;--ar:2.1714;--t:0.9s"><img src="/assets/img/marche/bonhomme-couche-blanc.png" alt="" width="2605" height="300" loading="lazy"></span><span class="p p1" style="--n:6;--ar:0.7287;--t:0.72s"><img src="/assets/img/marche/bonhomme-casquette-blanc.png" alt="" width="1311" height="300" loading="lazy"></span><span class="p p2" style="--n:4;--ar:1.2559;--t:0.62s"><img src="/assets/img/marche/deux-tuques-blanc.png" alt="" width="1507" height="300" loading="lazy"></span><span class="p p3" style="--n:6;--ar:0.5248;--t:0.66s"><img src="/assets/img/marche/bonhomme-surpris-blanc.png" alt="" width="944" height="300" loading="lazy"></span><span class="p p4" style="--n:4;--ar:2.1714;--t:0.9s"><img src="/assets/img/marche/bonhomme-couche-blanc.png" alt="" width="2605" height="300" loading="lazy"></span></div></div></div>
    <h1 class="titre-h1 fade"><span class="l1 x">{tr('Agence de branding', 'Branding agency')}</span> <span class="l2 mono">Bromont</span></h1>
    <div class="difficiles fade">
      <h2 class="t">{tr('On est', 'We are')} {encre(tr('difficiles', 'picky'))}.<br><span class="t2">{tr('Pour que vous n’ayez pas à l’être.', 'So you don’t have to be.')}</span></h2>
    </div>
    <p class="sr">{tr('Vêtements et produits personnalisés à Bromont. Agence de branding spécialisée en vêtements et produits personnalisés.', 'Custom apparel and products in Bromont. A branding agency specializing in custom apparel and products.')}</p>
  </section>

  <section class="sec wrap" id="services" aria-labelledby="t-services">
    <div class="head">
      <h2 class="h2 rv" id="t-services">{tr('Nos', 'Our')} {encre('services')}</h2>
      <div class="links rv"><a href="{url_p('services')}">{tr('Tous les services', 'All services')} <span class="arr">→</span></a></div>
    </div>
    <div class="grid">{tuiles}</div>
  </section>

  {casquettes_custom()}

  {etapes()}

  {mots()}

  <section class="mission" aria-labelledby="t-presentation">
    {photo(4, tr('L’atelier de Takedown Studio à Bromont, avec les presses à chaleur et le séchoir de sérigraphie', 'The Takedown Studio workshop in Bromont, with the heat presses and the screen printing dryer'), pos='50% 62%')}
    <div class="wrap in">
      <h2 class="sr" id="t-presentation">{tr('L’agence', 'About')}</h2>
      <p class="big rv">{tr('On t’aide à mettre ta marque sur des vêtements et des produits que les gens vont aimer utiliser.', 'We help you put your brand on apparel and products people will love to use.')}</p>
      <p class="small rv">{tr('Du choix du modèle au placement de ton logo, on te conseille selon ton idée, ton budget et la quantité dont tu as besoin. Broderie, sérigraphie ou impression numérique : on trouve la bonne option pour ton projet.', 'From choosing the style to placing your logo, we advise you based on your idea, your budget and the quantity you need. Embroidery, screen printing or digital printing: we find the right option for your project.')}</p>
      <a class="lien rv" href="{url_p('agence')}">{tr('Découvrir l’agence', 'Discover the agency')} <span class="arr">→</span></a>
    </div>
  </section>
  {zones()}
</main>
{pied()}'''
    return page(url_p('accueil'), tr('Takedown Studio | Vêtements et produits personnalisés à Bromont', 'Takedown Studio | Custom apparel and products in Bromont'),
                tr('Agence de branding à Bromont, pour l’Estrie, Granby, Sherbrooke, Magog et Montréal. On met ta marque sur des vêtements et des produits : broderie, sérigraphie, DTF, casquettes, patches et autocollants.',
                   'Branding agency in Bromont, serving the Eastern Townships, Granby, Sherbrooke, Magog and Montréal. We put your brand on apparel and products: embroidery, screen printing, DTF, caps, patches and stickers.'),
                corps)

def agence():
    corps = f'''{nav('/agence-branding')}
<main id="contenu">
  {phead([(url_p('agence'), tr('L’agence', 'About'))], tr('Agence de branding à Bromont', 'Branding agency in Bromont'),
         tr('Chez Takedown Studio, on t’aide à donner une image cohérente à tes vêtements et à tes produits. Que ce soit pour ton entreprise, ton équipe, un événement ou ta propre marque, on prend le temps de comprendre ce que tu cherches. On t’accompagne dans le choix des produits, des couleurs, des placements et de la bonne méthode de personnalisation.',
            'At Takedown Studio, we help you give your apparel and products a consistent image. Whether it is for your business, your team, an event or your own brand, we take the time to understand what you are after. We guide you through the choice of products, colours, placements and the right customization method.'),
         f'<a class="btn btn-w" href="{url_p("contact")}">{tr("Parle-nous de ton projet", "Tell us about your project")}</a><a class="btn btn-g" href="{url_p("services")}">{tr("Nos services", "Our services")}</a>',
         'logo-complet-lutteurs')}
  <section class="sec wrap">
    {plus_prevoir(tr('Un même contact pour ton projet, des conseils concrets et des produits qui vont bien ensemble.', 'One point of contact for your project, practical advice and products that work well together.'),
                  tr('Un projet qui regroupe plusieurs produits demande plus de préparation. Le budget et les délais dépendent des articles choisis.', 'A project that combines several products takes more preparation. Budget and timelines depend on the items you choose.'))}
  </section>
  {mots(False)}
  {etapes()}
</main>
{hesite()}
{pied()}'''
    return page(url_p('agence'), tr('Agence de branding à Bromont | Takedown Studio', 'Branding agency in Bromont | Takedown Studio'),
                tr('Takedown Studio t’aide à donner une image cohérente à tes vêtements et à tes produits : choix des produits, des couleurs, des placements, de la technique.',
                   'Takedown Studio helps you give your apparel and products a consistent image: choosing products, colours, placements and the technique.'),
                corps, fil=[(url_p('agence'), tr('L’agence', 'About'))])

# logo Instagram dessiné en SVG (trait blanc, taille remplacée au besoin)
LOGO_INSTA = ('<svg class="ig-ico" viewBox="0 0 24 24" width="__T__" height="__T__" aria-hidden="true" focusable="false">'
              '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.7"/>'
              '<circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.7"/>'
              '<circle cx="17.3" cy="6.7" r="1.15" fill="currentColor"/></svg>')

def services_index():
    blocs = ''
    for s in svcs():
        phrase = s['texte'].split('. ')[0].rstrip('.') + '.'
        blocs += f'''<article class="svc{' rose' if s.get('rose') else ''} rv">
      <a class="ph art" href="{url_s(s['slug'])}" tabindex="-1" aria-hidden="true"><img src="/assets/img/{DESSIN_TUILE[s['slug']]}-blanc.png" alt="" loading="lazy"></a>
      <div class="txt"><span class="mono" style="color:var(--mute)">{e(s['court'])}</span><h2>{s['nom']}</h2><p>{phrase}</p>
      <div><a class="btn btn-g" href="{url_s(s['slug'])}">{tr('Découvrir le service', 'See the service')} <span class="arr">→</span></a></div></div>
    </article>'''
    extras = ''
    if AFFICHER_EXTRAS:
        liens = ''.join(f'<a class="lien" href="{url_s("vetements-personnalises")}#{x["id"]}">{x["titre"]} <span class="arr">→</span></a>' for x in extras_l())
        extras = f'''<section class="sec wrap"><div class="head"><h2 class="h2 rv">{tr('Aussi possible', 'Also possible')}</h2></div>
      <div class="rv" style="display:flex;gap:28px;flex-wrap:wrap">{liens}</div></section>'''
    corps = f'''{nav('/services')}
<main id="contenu">
  {phead([(url_p('services'), tr('Nos services', 'Services'))], tr('Nos services', 'Our services'),
         tr('On t’aide à choisir les bons produits et la bonne technique pour représenter ta marque. Explore nos services pour voir les possibilités, les avantages et les éléments à prévoir.',
            'We help you choose the right products and the right technique to represent your brand. Explore our services to see the possibilities, the upsides and what to keep in mind.'),
         f'<a class="btn btn-w" href="{url_p("contact")}?service=je-sais-pas">{tr("Je sais pas quelle technique choisir", "I don’t know which technique to pick")}</a>', 'illustration-pinceau')}
  <section class="sec">{blocs}</section>
  {extras}
  <section class="wrap ig-section"><hr class="ig-sep">
    <div class="ig-bloc"><div class="ig-txt">
      <div class="ig-ligne rv">{LOGO_INSTA.replace('__T__', '44')}<p>{tr('Nos derniers projets, tu les trouves sur Instagram.', 'You can find our latest projects on Instagram.')}</p></div>
      <p class="rv"><a class="btn btn-g" href="{INSTAGRAM}" target="_blank" rel="noopener">{LOGO_INSTA.replace('__T__', '18')} {tr('Voir nos réalisations sur Instagram', 'See our work on Instagram')} <span class="arr">→</span></a></p></div>
      <img class="ig-dessin rv" src="/assets/img/dessins/chandail-loupe-blanc.png" sizes="(max-width:820px) 62vw, 380px" alt="" width="1000" height="670" loading="lazy"></div></section>
</main>
{hesite()}
{pied()}'''
    ld = [{'@type': 'ItemList', 'name': tr('Nos services', 'Our services'), 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': s['nom'], 'url': BASE + url_s(s['slug'])} for i, s in enumerate(svcs())]}]
    return page(url_p('services'), tr('Vêtements et produits personnalisés | Takedown Studio', 'Custom apparel and products | Takedown Studio'),
                tr('Vêtements personnalisés, broderie, sérigraphie, impression DTF, casquettes et tuques, patches et autocollants. Découvre nos services à Bromont.',
                   'Custom apparel, embroidery, screen printing, DTF printing, caps and beanies, patches and stickers. Explore our services in Bromont.'),
                corps, fil=[(url_p('services'), tr('Nos services', 'Services'))], extra_ld=ld)

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
    for i, t0 in enumerate(TYPES_PATCHES):
        t = dict(t0, **TYPES_PATCHES_EN[i]) if L == 'en' else t0
        visuel = (photo_patch(t['photos'][0], tr(f'Exemple de patch {t["nom"].lower()}', f'Example of a {t["nom"].lower()} patch')) if t['photos']
                  else ph(tr('Photo à venir', 'Photo coming soon'), '#2a2420'))
        sous = f' <span class="mono">{t["en"]}</span>' if t['en'] else ''
        cartes += f'''<article class="type-patch rv">{visuel}
        <div class="txt"><h3>{t['nom']}{sous}</h3><p>{t['texte']}</p></div></article>'''
    x = dict(ETIQUETTE, **ETIQUETTE_EN) if L == 'en' else ETIQUETTE
    sous_x = f' <span class="mono">{x["en"]}</span>' if x['en'] else ''
    etiq = f'''<article class="etiquette rv">{photo_patch(x['photo'], tr('Exemple d’étiquette tissée Takedown Studio, une étiquette mince', 'Example of a Takedown Studio woven label, a thin label'))}
      <div class="txt"><span class="mono">{tr('Aussi possible', 'Also possible')}</span><h3>{x['nom']}{sous_x}</h3><p>{x['texte']}</p>
      <p><a class="lien" href="{soum('patches-ecussons')}">{tr('Demander une soumission', 'Request a quote')} <span class="arr">→</span></a></p></div></article>'''
    return f'''<section class="sec wrap"><div class="head"><h2 class="h2 rv">{tr('Les types de patches', 'Patch types')}</h2>
    <p class="note rv">{tr('On t’aide à choisir selon ton logo, ton produit et le look que tu veux.', 'We help you choose based on your logo, your product and the look you want.')}</p></div>
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
    for gi, (titre, note, blocs) in enumerate(GUIDE_CASQUETTES):
        if L == 'en':
            titre, note, blocs_e = GUIDE_CASQUETTES_EN[gi]
        arts = ''
        puces = ''
        for n, (dessin, tag, nom, texte, lien) in enumerate(blocs):
            if L == 'en':
                tag, nom, texte, lien_e = blocs_e[n]
                lien = (lien[0], lien_e) if lien else None
            btn = f'<div><a class="btn btn-g" href="{url_s(lien[0])}">{lien[1]} <span class="arr">→</span></a></div>' if lien else ''
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
    s = loc(s)
    photos = []   # 2026-10-26 (Alex Moite) : plus de photos d'exemple sur les pages de services, seulement la liste d'exemples
    exemples = ''.join(f'<figure class="rv">{photo_real(r)}<figcaption>{r["titre"]}</figcaption></figure>' for r in photos[1:7])
    exemples = (f'<div class="ex">{exemples}</div>' if exemples else '') + \
        '<ul class="ex-liste rv">' + ''.join(f'<li>{x}</li>' for x in s['exemples']) + '</ul>'
    grande = (f'<section class="sec wrap"><figure class="grande rv">{photo_real(photos[0], "(max-width:1200px) 100vw, 1200px")}'
              f'<figcaption class="mono">{photos[0]["titre"]} · {photos[0]["tech"]}</figcaption></figure></section>') if photos else ''
    extras = ''
    if s['slug'] == 'vetements-personnalises' and AFFICHER_EXTRAS:
        extras = f'<section class="sec wrap"><div class="head"><h2 class="h2 rv">{tr("Aussi possible", "Also possible")}</h2><p class="note rv">{tr("Avec nos partenaires, pour les projets qui sortent de l’ordinaire.", "With our partners, for projects that go beyond the ordinary.")}</p></div>' + ''.join(f'''
      <article class="extra rv" id="{x['id']}">
        <div><span class="mono">{tr('Sur demande', 'On request')}</span><h3>{x['titre']}</h3></div>
        <div><p>{x['texte']}</p>
          <dl><div><dt>{tr('Les plus', 'The upsides')}</dt><dd>{x['plus']}</dd></div><div><dt>{tr('À prévoir', 'Keep in mind')}</dt><dd>{x['prevoir']}</dd></div></dl>
          <p style="margin-top:22px"><a class="lien" href="{soum(x['val'])}">{tr('Demander une soumission', 'Request a quote')} <span class="arr">→</span></a></p></div>
      </article>''' for x in extras_l()) + '</section>'
    assoc = ''
    if s['liens']:
        assoc = f'''<section class="sec wrap"><div class="head"><h2 class="h2 rv">{tr('Services associés', 'Related services')}</h2>
      <div class="links rv"><a href="{url_p('services')}">{tr('Tous les services', 'All services')} <span class="arr">→</span></a></div></div>
      <div class="grid g3">{''.join(tuile(PAR_SLUG[l]) for l in s['liens'][:3])}</div>
      {('<div class="rv" style="display:flex;gap:28px;flex-wrap:wrap;margin-top:24px">' + ''.join(f'<a class="lien" href="{url_s(l)}">{nom_court(PAR_SLUG[l])} <span class="arr">→</span></a>' for l in s['liens'][3:]) + '</div>') if len(s['liens']) > 3 else ''}
    </section>'''
    pp = f'<section class="sec wrap">{plus_prevoir(s["plus"], s["prevoir"])}</section>'
    pp_haut = '' if s.get('rose') else pp   # pour les casquettes 100 % : « Les plus / À prévoir » passent sous le guide
    if s.get('rose'):
        bloc_exemples = guide_casquettes() + pp + f'''<section class="sec wrap"><p class="rv"><a class="btn btn-w" href="{soum(s['slug'])}">{s['bouton']} <span class="arr">→</span></a></p></section>'''
    else:
        bloc_exemples = f'''<section class="sec wrap"><div class="head"><h2 class="h2 rv">{tr('Exemples', 'Examples')}</h2>
    <div class="links rv"><a href="{url_p('realisations')}?f={s['filtre']}">{tr('Voir les réalisations', 'See our work')} <span class="arr">→</span></a></div></div>
    {exemples}
    <p class="rv" style="margin-top:40px"><a class="btn btn-w" href="{soum(s['slug'])}">{s['bouton']} <span class="arr">→</span></a></p>
  </section>'''
    ctas = (f'<a class="btn btn-w" href="{soum(s["slug"])}">{s["bouton"]}</a>'
            f'<a class="btn btn-g" href="{url_p("realisations")}?f={s["filtre"]}">{tr("Voir les réalisations", "See our work")}</a>')
    corps = f'''{nav('/services')}
<main id="contenu">
  {phead([(url_p('services'), tr('Nos services', 'Services')), (url_s(s['slug']), s['nom'])], s['nom'], s['texte'], ctas, DESSIN_SERVICE.get(s['slug'], DESSINS[i % 3]), rose=bool(s.get('rose')))}
  {grande}
  {pp_haut}
  {types_patches() if s['slug'] == 'patches-ecussons' else ''}
  {bloc_exemples}
  {extras}
  {assoc}
  {zones()}
</main>
{hesite()}
{pied()}'''
    ld = [{'@type': 'Service', 'name': s['nom'], 'serviceType': s['nom'], 'description': s['texte'],
           'provider': {'@id': BASE + '/#entreprise'}, 'areaServed': {'@type': 'City', 'name': 'Bromont'},
           'url': BASE + url_s(s['slug'])}]
    return page(url_s(s['slug']), s['seo'], s['desc'], corps,
                fil=[(url_p('services'), tr('Nos services', 'Services')), (url_s(s['slug']), s['nom'])], extra_ld=ld)

# 2026-10-26 (Takedown via Alex Moite) : page Catalogue, les produits favoris (promo / basic et premium)
CATALOGUE = json.load(io.open(os.path.join(ICI, 'contenu', 'catalogue.json'), encoding='utf-8'))
CAT_FILTRES = [('tous', 'Tous'), ('tshirt', 'T-shirts'), ('manches-longues', 'Manches longues'), ('crewneck', 'Crewnecks'),
               ('hoodie', 'Hoodies'), ('veste', 'Vestes'), ('pantalon', 'Pantalons'), ('casquette', 'Casquettes'), ('tuque', 'Tuques'), ('accessoire', 'Accessoires')]
CAT_SLUG = {'T-shirt': 'tshirt', 'Manches longues': 'manches-longues', 'Crewneck': 'crewneck', 'Hoodie': 'hoodie',
            'Casquette': 'casquette', 'Tuque': 'tuque', 'Accessoire': 'accessoire', 'Veste': 'veste', 'Pantalon': 'pantalon'}
CAT_TITRES = {'T-shirt': 'T-shirts', 'Manches longues': 'Manches longues', 'Crewneck': 'Crewnecks', 'Hoodie': 'Hoodies', 'Veste': 'Vestes',
              'Pantalon': 'Pantalons', 'Casquette': 'Casquettes', 'Tuque': 'Tuques', 'Accessoire': 'Accessoires'}

# 2026-10-28 : noms de produits en anglais (page /en/ et PDF anglais), par id du catalogue
NOMS_EN = {
    1: 'Heavyweight Cotton T-shirt',
    2: 'Parkour T-shirt',
    3: 'Everyday Cotton T-shirt',
    4: 'Fine Jersey T-shirt',
    5: 'Cotton T-shirt',
    6: 'Heavy Cotton T-shirt',
    7: 'Heavyweight Cotton Long Sleeve',
    8: 'Breeze Long Sleeve',
    9: 'Heavy Blend Crewneck',
    10: 'Midweight Crewneck',
    11: 'Crew Sweatshirt',
    12: 'Everyday Fleece Hoodie',
    13: 'Midweight Hoodie',
    14: 'Element CFF Hoodie',
    15: 'Heavy Blend Hoodie',
    16: 'Vault Hoodie',
    17: 'Classic Dad Cap',
    18: 'Trucker Cap',
    19: 'Ribbed Cuffed Beanie',
    20: 'Polar Beanie',
    21: 'Core Tote Bag',
    22: 'Garment-Dyed Heavyweight T-shirt',
    23: 'The 1801, Garment Dyed',
    24: 'Max Heavyweight Oversized Tee',
    25: 'Super Heavy Oversized Tee',
    26: 'Urban 280 T-shirt',
    27: 'Garment-Dyed Heavyweight Long Sleeve',
    28: 'Premium Crewneck',
    29: 'Boulevard Heavyweight Hoodie',
    30: 'Pigment-Dyed Cap',
    31: 'Washed Dad Cap',
    32: 'Accent Beanie',
    33: 'Fisherman Beanie',
    34: 'Cozy Beanie',
    35: 'Tofino Beanie',
    36: 'Mountain Beanie',
    37: 'OG Beanie',
    38: 'Fundy Beanie',
    39: 'Trail Beanie (Recycled Cotton)',
    40: 'Mesh Trucker Cap',
    41: 'Cotton Trucker Cap',
    42: 'Foam Trucker Cap',
    43: 'Nylon Rope Cap',
    44: 'Dad Cap Classic',
    45: 'Grid Tote Bag',
    46: 'Cargo Tote Bag',
    47: 'Windbreaker Anorak Jacket',
    48: 'Hooded Windbreaker Coach Jacket',
    49: 'Windbreaker Coach Jacket',
    50: 'Avenue Midweight Hoodie',
    51: 'Heavyweight Original Hoodie',
    52: 'Heavyweight Zip Hoodie',
    53: 'Mainstreet Hoodie',
    54: 'Mainstreet Zip Hoodie',
    55: 'Premium 180 Long Sleeve',
    56: 'Premium 180 Pigment-Dyed T-shirt',
    57: 'Max Heavyweight Garment-Dyed T-shirt',
    58: 'Garment-Dyed Cropped T-shirt',
    59: 'Thermal Long Sleeve',
    60: 'Garment-Dyed Long Sleeve',
    61: 'Premium Core Hoodie',
    62: 'Premium Zip Hoodie',
    63: 'Straight-Leg Jogger Pants',
    64: 'Urban Hoodie',
    65: 'Urban Crewneck',
    66: 'Heavy Core Hoodie',
    67: 'Heavyweight Pullover Hoodie',
    68: 'Heavy Crewneck',
    69: 'Thermal Crewneck',
    70: 'Thermal Hoodie',
    71: 'Urban Heavy T-shirt',
    72: 'Women’s Cropped T-shirt',
    73: 'Women’s Relaxed T-shirt',
    74: 'Women’s Ribbed Tank',
    75: 'Women’s Garment-Dyed Cropped T-shirt',
    76: 'Heavy Core T-shirt',
}

def nom_produit(x):
    return NOMS_EN.get(x['id'], x['nom']) if L == 'en' else x['nom']

def carte_produit(x):
    cat = tr(x['categorie'], CAT_EN.get(x['categorie'], x['categorie']))
    tailles, poids, couleurs_plus = t_tailles(x['tailles']), t_poids(x['poids']), t_plus(x['couleurs_plus'])
    ligne_ref = e(x['marque']) + (' · ' + e(x['ref']) if x['ref'] else '')
    lignes = f'<div><dt>{tr("Catégorie", "Category")}</dt><dd>{e(cat)}</dd></div>'
    if poids:
        lignes += f'<div><dt>{tr("Poids", "Weight")}</dt><dd>{e(poids)}</dd></div>'
    if tailles:
        lignes += f'<div><dt>{tr("Tailles", "Sizes")}</dt><dd>{e(tailles)}</dd></div>'
    plus = f' <em>{e(couleurs_plus)}.</em>' if couleurs_plus else ''
    court_t = tailles.split(' (')[0] if tailles else ''
    court_p = poids.split(' (')[0] if poids else ''
    pres = f'<p class="pres">{e(cat)}{" · " + e(court_t) if court_t else ""}{" · " + e(court_p) if court_p else ""}</p>'
    return (f'<article class="pcat rv" data-cat="{CAT_SLUG.get(x["categorie"], "autre")}">'
            f'<div class="pimg" style="background:{x.get("fond", "#fff")}"><img src="/assets/img/{x["image"]}" alt="{e(nom_produit(x))}, {e(x["marque"])}" width="720" height="900" loading="lazy"></div>'
            f'<div class="ptxt"><p class="mono">{ligne_ref}</p><h3>{e(nom_produit(x))}</h3>{pres}<dl>{lignes}</dl>'
            f'<details><summary>{tr("Couleurs", "Colours")} ({e(t_nb(x["couleurs_nb"]))})</summary><p>{e(x["couleurs"])}.{plus}</p></details></div></article>')

def catalogue():
    puces = ''.join(f'<button type="button" class="chip" data-cat="{k}" aria-pressed="{"true" if k == "tous" else "false"}">{tr(t, CAT_FILTRES_EN[k])}</button>' for k, t in CAT_FILTRES)
    def bloc(titre, liste):
        cartes = ''.join(carte_produit(x) for x in liste)
        n = len(liste)
        return (f'<section class="sec wrap cat-section"><div class="head"><h2 class="h2 rv">{titre}</h2><p class="note rv">{n} {tr("produit", "product")}{"s" if n > 1 else ""}.</p></div>'
                f'<div class="cat-grid">{cartes}</div></section>')
    blocs = ''.join(bloc(tr(CAT_TITRES[t], CAT_TITRES_EN[t]), [x for x in CATALOGUE if x['categorie'] == t]) for t in CAT_TITRES if any(x['categorie'] == t for x in CATALOGUE))
    # un PDF par langue : le français et l'anglais ont chacun leur lien de téléchargement
    pdf_lien = tr(' <a class="lien" href="/assets/documents/catalogue-takedown-studio.pdf" download>Télécharger le catalogue (PDF) <span class="arr">↓</span></a>',
                  ' <a class="lien" href="/assets/documents/takedown-studio-catalog.pdf" download>Download the catalogue (PDF) <span class="arr">↓</span></a>')
    corps = f'''{nav('/catalogue')}
<main id="contenu">
  {phead([(url_p('catalogue'), 'Catalogue')], tr('Notre catalogue', 'Our catalogue'),
         tr('Nos produits favoris, du promo au premium.<span class="cat-plus">On en a ' + encre('beaucoup plus') + '.</span>Dis-nous ce que tu cherches.',
            'Our favourite products, from budget to premium.<span class="cat-plus">We have ' + encre('a lot more') + '.</span>Tell us what you are looking for.'),
         '', 'illustration-pinceau')}
  <section class="wrap cat-barre"><p class="rv">{tr('Livraison gratuite partout au Canada.', 'Free shipping anywhere in Canada.')}{pdf_lien}</p>
    <div class="chips-cat" role="group" aria-label="{tr('Filtrer par catégorie', 'Filter by category')}">{puces}</div></section>
  {blocs}
  <section class="sec wrap"><div class="cat-fin rv"><h2 class="h2">{tr('Tu cherches autre chose?', 'Looking for something else?')}</h2>
    <p>{tr('Ces produits sont nos favoris, mais on en a beaucoup plus. Parle-nous de ton projet et on te trouve le bon produit.', 'These products are our favourites, but we have a lot more. Tell us about your project and we will find you the right product.')}</p>
    <div class="ctas"><a class="btn btn-w" href="{url_p('contact')}">{tr('Demander une soumission', 'Request a quote')} <span class="arr">→</span></a><a class="btn btn-g" href="{url_p('services')}">{tr('Nos services', 'Our services')}</a></div></div></section>
</main>
{hesite()}
{pied()}'''
    return page(url_p('catalogue'), tr('Catalogue de vêtements et de produits personnalisés | Takedown Studio', 'Catalogue of custom apparel and products | Takedown Studio'),
                tr('Les produits favoris de Takedown Studio : t-shirts, crewnecks, hoodies, casquettes, tuques, du promo au premium. On en a beaucoup plus. Demande ta soumission.',
                   'Takedown Studio favourites: T-shirts, crewnecks, hoodies, caps, beanies, from budget to premium. We have a lot more. Request your quote.'),
                corps, fil=[(url_p('catalogue'), 'Catalogue')])

def realisations():
    presents = {'tous'} | {c for r in REALISATIONS for c in r['categories'].split()}
    AFFICHER_PHOTOS = False   # 2026-10-26 (Alex Moite) : la page Réalisations montre seulement la carte Instagram pour l'instant
    chips = ''.join(f'<button class="chip" type="button" data-f="{k}" aria-pressed="{str(k == "tous").lower()}">{t}</button>'
                    for k, t in FILTRES if k in presents and AFFICHER_PHOTOS)
    items = ''.join(f'''<article class="real rv" data-c="{r['categories']}">
      {photo_real(r)}
      <h3>{r['titre']}</h3>
      <div class="meta mono"><span>{r['produit']}</span><span>{r['tech']}</span></div>
      <a class="lien" href="{url_s(r['service'])}">{nom_court(PAR_SLUG[r['service']])} <span class="arr">→</span></a>
    </article>''' for r in REALISATIONS if AFFICHER_PHOTOS)
    insta = f'''<a class="real insta rv" href="{INSTAGRAM}" target="_blank" rel="noopener" data-c="tous">
      <div class="ph"><span class="ig">@takedownstudio</span></div>
      <h3>{tr('Nos derniers projets sur Instagram', 'Our latest projects on Instagram')} <span class="arr">→</span></h3>
      <div class="meta mono"><span>{tr('Broderie', 'Embroidery')}</span><span>{tr('Sérigraphie', 'Screen printing')}</span><span>DTF</span></div>
    </a>'''
    corps = f'''{nav('/realisations')}
<main id="contenu">
  {phead([(url_p('realisations'), tr('Réalisations', 'Our work'))], tr('Nos réalisations', 'Our work'),
         tr('Découvre quelques projets réalisés par Takedown Studio. Chaque projet est différent, et la technique utilisée dépend du produit, du visuel, de la quantité et du résultat recherché.',
            'Discover a few projects completed by Takedown Studio. Every project is different, and the technique used depends on the product, the artwork, the quantity and the result you want.'),
         '', 'dessins/bonhomme-aiguille')}
  <section class="sec wrap">
    {f'<div class="chips" role="group" aria-label="Filtrer par technique">{chips}</div>' if chips else ''}
    <div class="reals">{items}{insta}</div>
    <p style="margin-top:56px"><a class="btn btn-w" href="{url_p('contact')}">{tr('Parle-nous de ton projet', 'Tell us about your project')} <span class="arr">→</span></a></p>
  </section>
</main>
{hesite()}
{pied()}'''
    return page(url_p('realisations'), tr('Nos réalisations | Takedown Studio', 'Our work | Takedown Studio'),
                tr('Des projets de Takedown Studio : vêtements brodés, t-shirts en sérigraphie, impression DTF, casquettes, patches et autocollants personnalisés.',
                   'Takedown Studio projects: embroidered apparel, screen-printed T-shirts, DTF printing, caps, patches and custom stickers.'),
                corps, fil=[(url_p('realisations'), tr('Réalisations', 'Our work'))])

def contact():
    options = ''.join(f'<option value="{v}">{t}</option>' for v, t in choix_service())
    def champ(id_, lab, typ='text', req=True, full=False, extra='', ph_=''):
        opt = '' if req else ' <em>' + tr('(facultatif)', '(optional)') + '</em>'
        r = ' required aria-required="true"' if req else ''
        return (f'<div class="champ{" full" if full else ""}"><label for="{id_}">{lab}{opt}</label>'
                f'<input id="{id_}" name="{id_}" type="{typ}"{r}{extra}{f" placeholder=\"{ph_}\"" if ph_ else ""}>'
                f'<span class="msg">{tr("Ce champ est obligatoire.", "This field is required.")}</span></div>')
    corps = f'''{nav('/contact')}
<main id="contenu">
  {phead([(url_p('contact'), 'Contact')], tr('Demander une soumission', 'Request a quote'),
         tr('Envoie-nous ton idée, ton logo et la quantité que tu as en tête. On va regarder les possibilités avec toi et te guider vers les bons produits et la bonne technique.',
            'Send us your idea, your logo and the quantity you have in mind. We will look at the options with you and guide you to the right products and technique.'),
         dessin='dessins/chandail-tache')}
  <section class="wrap formgrid">
    <div>
      <form id="soumission" class="form" action="{API_SOUMISSION}" data-merci="{url_p('merci')}" method="post" enctype="multipart/form-data" novalidate>
        {champ('nom', tr('Nom', 'Name'), extra=' autocomplete="name"')}
        {champ('entreprise', tr('Entreprise', 'Company'), req=False, extra=' autocomplete="organization"')}
        {champ('courriel', tr('Courriel', 'Email'), 'email', extra=' autocomplete="email" inputmode="email"')}
        {champ('telephone', tr('Téléphone', 'Phone'), 'tel', req=False, extra=' autocomplete="tel" inputmode="tel"')}
        <div class="champ full"><label for="service">{tr('Service recherché', 'Service needed')}</label>
          <select id="service" name="service" required aria-required="true"><option value="">{tr('Choisis un service', 'Choose a service')}</option>{options}</select>
          <span class="msg">{tr('Choisis un service, ou coche la case en dessous.', 'Choose a service, or tick the box below.')}</span>
          <label class="coche" style="margin-top:12px;text-transform:none;letter-spacing:0;font-family:inherit;font-size:15px;color:#d6d6d9"><input type="checkbox" id="sais-pas"> {tr('Je ne sais pas quelle technique choisir', 'I don’t know which technique to pick')}</label>
        </div>
        {champ('produit', tr('Produit recherché', 'Product you want'), ph_=tr('Ex. hoodies, casquettes, autocollants', 'e.g. hoodies, caps, stickers'))}
        {champ('quantite', tr('Quantité approximative', 'Approximate quantity'), ph_=tr('Ex. 50 morceaux', 'e.g. 50 pieces'), extra=' inputmode="numeric"')}
        {champ('date', tr('Date souhaitée', 'Date needed'), 'date')}
        {champ('budget', tr('Budget approximatif', 'Approximate budget'), req=False)}
        <div class="champ full"><label for="description">{tr('Description du projet', 'Project description')}</label>
          <textarea id="description" name="description" required aria-required="true" placeholder="{tr('Ton idée, les couleurs, les placements, l’utilisation prévue…', 'Your idea, the colours, the placements, how it will be used…')}"></textarea>
          <span class="msg">{tr('Décris-nous ton projet en quelques mots.', 'Tell us about your project in a few words.')}</span></div>
        <div class="champ full"><span class="lab">{tr('Tes fichiers', 'Your files')} <em style="color:var(--mute);text-transform:none;letter-spacing:0">{tr('(logo, visuel, croquis)', '(logo, artwork, sketch)')}</em></span>
          <label class="depot" tabindex="0" for="fichiers"><input id="fichiers" name="fichiers" type="file" multiple accept=".ai,.eps,.pdf,.svg,.png,.jpg,.jpeg,.webp,.heic,.psd,image/*,application/pdf">
            <b>{tr('Glisse tes fichiers ici', 'Drag your files here')}</b> {tr('ou clique pour les choisir', 'or click to choose them')}</label>
          <ul class="fichiers" aria-live="polite"></ul></div>
        <div class="champ full"><label for="source">{tr('Comment tu nous as connus', 'How did you hear about us')} <em>{tr('(facultatif)', '(optional)')}</em></label>
          <select id="source" name="source"><option value="">{tr('Choisis une option', 'Choose an option')}</option><option>Instagram</option><option>Facebook</option><option>Google</option><option value="Bouche-à-oreille">{tr('Bouche-à-oreille', 'Word of mouth')}</option><option value="Un client de Takedown">{tr('Un client de Takedown', 'A Takedown client')}</option><option value="Autre">{tr('Autre', 'Other')}</option></select></div>
        <div class="miel" aria-hidden="true"><label for="site_web">{tr('Ne pas remplir', 'Do not fill in')}</label><input id="site_web" name="_honey" type="text" tabindex="-1" autocomplete="off"></div>
        <input type="hidden" name="_subject" value="{tr('Nouvelle demande de soumission (site Takedown Studio)', 'New quote request (Takedown Studio website, EN)')}"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false">
        <div class="envoi full"><button class="btn btn-w" type="submit">{tr('Envoyer ma demande', 'Send my request')}</button><small>{tr('On te répond par courriel ou par téléphone.', 'We will reply by email or by phone.')}</small>
          <small class="consent">{tr('En envoyant ce formulaire, tu acceptes notre', 'By sending this form, you agree to our')} <a href="{url_p('confidentialite')}">{tr('politique de confidentialité', 'privacy policy')}</a>.</small></div>
      </form>
      <div id="etat" class="etat" role="status" aria-live="polite"></div>
    </div>
    <aside class="aside">
      <div class="bloc"><h3>{tr('Pour aller plus vite', 'To go faster')}</h3><ol><li>{tr('Ton logo ou ton visuel', 'Your logo or artwork')}</li><li>{tr('La quantité que tu as en tête', 'The quantity you have in mind')}</li><li>{tr('La date où tu en as besoin', 'The date you need it by')}</li></ol></div>
      <div class="bloc"><h3>{tr('Nous joindre', 'Get in touch')}</h3><a href="mailto:{ENTREPRISE['courriel']}">{ENTREPRISE['courriel']}</a><a href="tel:{ENTREPRISE['tel_intl']}">{ENTREPRISE['tel']}</a></div>
      <div class="bloc"><h3>{tr('Le studio', 'The studio')}</h3><p>{ENTREPRISE['rue']}<br>{ville_cp()}</p></div>
    </aside>
  </section>
</main>
{pied(court=True)}'''
    return page(url_p('contact'), tr('Demander une soumission | Takedown Studio', 'Request a quote | Takedown Studio'),
                tr('Envoie ton idée, ton logo et la quantité que tu as en tête. Takedown Studio te guide vers les bons produits et la bonne technique. Bromont.',
                   'Send your idea, your logo and the quantity you have in mind. Takedown Studio guides you to the right products and technique. Bromont.'),
                corps, fil=[(url_p('contact'), 'Contact')])

def page_texte(cle, titre, intro, sections, desc):
    """Page de texte légal : en-tête sobre + sections numérotées. sections = [(titre, html)]."""
    corps_s = ''.join(f'<section class="pol-s">{"<h2>" + t + "</h2>" if t else ""}{h}</section>' for t, h in sections)
    corps = f'''{nav('')}
<main id="contenu">
  {phead([(url_p(cle), titre)], titre, intro)}
  <section class="sec wrap pol">
    {corps_s}
  </section>
</main>
{pied(court=True, lien_courriel=url_p('ecrire'))}'''
    return page(url_p(cle), f'{titre} | Takedown Studio', desc, corps, fil=[(url_p(cle), titre)])

def mini_form():
    """Mini formulaire (nom, courriel, message) des pages légales : remplace les liens mailto."""
    return (f'<div><form id="form-legal" class="form form-legal" action="{API_SOUMISSION}" method="post" novalidate>'
        f'<div class="champ full"><label for="lg-nom">{tr("Nom", "Name")}</label><input id="lg-nom" name="nom" type="text" required aria-required="true" autocomplete="name"><span class="msg">{tr("Ce champ est obligatoire.", "This field is required.")}</span></div>'
        f'<div class="champ full"><label for="lg-courriel">{tr("Courriel", "Email")}</label><input id="lg-courriel" name="courriel" type="email" required aria-required="true" autocomplete="email" inputmode="email"><span class="msg">{tr("Ce champ est obligatoire.", "This field is required.")}</span></div>'
        f'<div class="champ full"><label for="lg-message">{tr("Ton problème ou ta question", "Your issue or question")}</label><textarea id="lg-message" name="message" required aria-required="true"></textarea><span class="msg">{tr("Ce champ est obligatoire.", "This field is required.")}</span></div>'
        f'<div class="miel" aria-hidden="true"><label for="lg-site">{tr("Ne pas remplir", "Do not fill in")}</label><input id="lg-site" name="_honey" type="text" tabindex="-1" autocomplete="off"></div>'
        f'<input type="hidden" name="_subject" value="{tr("Demande de confidentialité / conditions (site Takedown Studio)", "Privacy / terms request (Takedown Studio website, EN)")}"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false">'
        f'<div class="envoi full"><button class="btn btn-w" type="submit">{tr("Envoyer", "Send")}</button></div></form>'
        f'<div id="etat-legal" class="etat" role="status" aria-live="polite"></div></div>')

def lien_ecrire():
    return f'<p><a class="btn btn-w" href="{url_p("ecrire")}">{tr("Nous joindre", "Contact us")}</a></p>'

def ecrire_page():
    """Page dédiée au mini formulaire (nom, courriel, message), liée depuis les pages légales."""
    titre = tr('Nous joindre', 'Contact us')
    corps = f'''{nav('')}
<main id="contenu">
  {phead([(url_p('ecrire'), titre)], titre, tr('Une question sur tes renseignements personnels ou sur nos conditions? Dis-nous ce qui se passe, on te répond par courriel.', 'A question about your personal information or our terms? Tell us what is going on and we will reply by email.'))}
  <section class="sec wrap pol">
    <section class="pol-s">{mini_form()}</section>
  </section>
</main>
{pied(court=True)}'''
    return page(url_p('ecrire'), f'{titre} | Takedown Studio',
                tr('Écris à Takedown Studio : une question sur tes renseignements personnels ou sur les conditions du site.', 'Write to Takedown Studio: a question about your personal information or the site terms.'),
                corps, fil=[(url_p('ecrire'), titre)])

def confidentialite():
    c = ENTREPRISE['courriel']
    adr = f"{ENTREPRISE['rue']}, {ville_cp()}"
    maj = tr('Dernière mise à jour : ', 'Last updated: ') + AUJ
    secs = [
      (tr('Qui on est', 'Who we are'),
       tr(f'<p>Le site takedownstudio.com est exploité par Takedown Studio, {adr}. Cette politique explique quels renseignements personnels on recueille quand tu utilises le site ou que tu nous envoies une demande, pourquoi, et comment tu peux exercer tes droits (notamment en vertu de la Loi 25 du Québec).</p>',
          f'<p>The takedownstudio.com website is operated by Takedown Studio, {adr}. This policy explains what personal information we collect when you use the site or send us a request, why we collect it, and how you can exercise your rights (including under Quebec’s Law 25).</p>')),
      (tr('Les renseignements qu’on recueille', 'What we collect'),
       tr('<p>On recueille seulement ce que tu nous donnes toi-même dans le formulaire de soumission :</p><ul><li>ton nom, et le nom de ton entreprise si tu le donnes</li><li>ton adresse courriel et, si tu veux, ton numéro de téléphone</li><li>les détails de ton projet : service, produit, quantité, date souhaitée, budget, description</li><li>les fichiers que tu joins (logo, visuel, croquis)</li><li>la façon dont tu nous as connus, si tu choisis de le dire</li></ul><p>Tu peux aussi nous écrire directement par courriel ou par téléphone : on garde alors les renseignements que tu nous donnes dans ces échanges.</p>',
          '<p>We only collect what you give us yourself in the quote form:</p><ul><li>your name, and your company name if you give it</li><li>your email address and, if you wish, your phone number</li><li>your project details: service, product, quantity, date needed, budget, description</li><li>the files you attach (logo, artwork, sketch)</li><li>how you heard about us, if you choose to say</li></ul><p>You can also write to us directly by email or phone, in which case we keep the information you give us in those exchanges.</p>')),
      (tr('Pourquoi on les utilise', 'Why we use it'),
       tr('<p>On utilise ces renseignements uniquement pour répondre à ta demande, préparer une soumission, discuter de ton projet et assurer le suivi avec toi. On ne les vend pas et on ne s’en sert pas pour de l’envoi de masse sans ton accord.</p>',
          '<p>We use this information only to answer your request, prepare a quote, discuss your project and follow up with you. We do not sell it and we do not use it for mass mailing without your agreement.</p>')),
      (tr('Ton consentement', 'Your consent'),
       tr('<p>En envoyant le formulaire, tu acceptes que Takedown Studio utilise les renseignements fournis pour les fins décrites ci-dessus. Tu peux retirer ton consentement en tout temps en nous écrivant à l’adresse indiquée plus bas.</p>',
          '<p>By sending the form, you agree that Takedown Studio may use the information you provide for the purposes described above. You can withdraw your consent at any time by writing to the address given below.</p>')),
      (tr('Avec qui on les partage', 'Who we share it with'),
       tr('<p>Pour que le site fonctionne, certains fournisseurs techniques traitent des renseignements en notre nom :</p><ul><li>le service d’envoi de formulaires FormSubmit, qui transmet le contenu du formulaire et tes fichiers à notre boîte courriel</li><li>GitHub Pages, qui héberge le site (comme tout hébergeur, il peut enregistrer des données techniques de visite, par exemple l’adresse IP)</li><li>notre fournisseur de courriel, qui reçoit ta demande</li></ul><p>Ces fournisseurs peuvent être situés à l’extérieur du Québec ou du Canada, ce qui veut dire que tes renseignements peuvent être traités ailleurs. On ne les communique à personne d’autre, sauf si la loi l’exige.</p>',
          '<p>To make the site work, some technical providers process information on our behalf:</p><ul><li>the FormSubmit form service, which forwards the form content and your files to our email inbox</li><li>GitHub Pages, which hosts the site (like any host, it may log technical visit data such as the IP address)</li><li>our email provider, which receives your request</li></ul><p>These providers may be located outside Quebec or Canada, which means your information may be processed elsewhere. We do not share it with anyone else, unless the law requires it.</p>')),
      (tr('Témoins et suivi', 'Cookies and tracking'),
       tr('<p>Le site ne dépose pas de témoins (cookies) et n’utilise pas, pour l’instant, d’outil de mesure d’audience ni de pixel publicitaire. Ton navigateur garde seulement, sur ton appareil, ta préférence de langue (FR ou EN) et un indicateur pour ne pas rejouer l’introduction de l’accueil. Ces données ne nous sont pas transmises. Si on ajoute un outil de mesure, cette politique sera mise à jour avant.</p>',
          '<p>The site does not set cookies and does not currently use an analytics tool or an advertising pixel. Your browser only keeps, on your device, your language preference (FR or EN) and a flag so the home page intro is not replayed. This data is not sent to us. If we add an analytics tool, this policy will be updated first.</p>')),
      (tr('Combien de temps on les garde', 'How long we keep it'),
       tr('<p>On garde tes renseignements le temps nécessaire pour répondre à ta demande et assurer le suivi de ton projet, puis le temps requis par nos obligations légales et comptables si un contrat est conclu. Après, ils sont supprimés ou rendus anonymes.</p>',
          '<p>We keep your information as long as needed to answer your request and follow up on your project, then for as long as our legal and accounting obligations require if a contract is signed. After that, it is deleted or anonymized.</p>')),
      (tr('Tes droits', 'Your rights'),
       tr(f'<p>Tu peux demander en tout temps :</p><ul><li>de savoir quels renseignements on détient sur toi et d’en recevoir une copie</li><li>de faire corriger un renseignement inexact</li><li>de faire supprimer tes renseignements ou de retirer ton consentement</li></ul><p>Utilise le formulaire : <a href="{url_p('ecrire')}">nous écrire</a>. Si tu estimes que tes droits ne sont pas respectés, tu peux aussi t’adresser à la Commission d’accès à l’information du Québec.</p>',
          f'<p>You can ask at any time to:</p><ul><li>know what information we hold about you and receive a copy</li><li>have inaccurate information corrected</li><li>have your information deleted or withdraw your consent</li></ul><p>Use the form: <a href="{url_p('ecrire')}">write to us</a>. If you believe your rights are not being respected, you can also contact the Commission d’accès à l’information du Québec.</p>')),
      (tr('Personne responsable', 'Person in charge'),
       tr(f'<!-- À CONFIRMER PAR TAKEDOWN : nom de la personne responsable de la protection des renseignements personnels (Loi 25). En attendant, la boîte générale sert de point de contact. --><p>Pour toute question sur la protection de tes renseignements, écris à la personne responsable de la protection des renseignements personnels de Takedown Studio : <a href="{url_p('ecrire')}">utilise le formulaire « Nous écrire »</a>.</p>',
          f'<!-- TO BE CONFIRMED BY TAKEDOWN: name of the person responsible for the protection of personal information (Law 25). Until then, the general inbox is the contact point. --><p>For any question about the protection of your information, write to Takedown Studio’s person responsible for the protection of personal information: <a href="{url_p('ecrire')}">use the “Write to us” form</a>.</p>')),
      (tr('Nous joindre', 'Contact us'), lien_ecrire()),
      (tr('Changements à cette politique', 'Changes to this policy'),
       tr('<p>On peut mettre cette politique à jour. La date de la dernière version est indiquée en haut de la page.</p>',
          '<p>We may update this policy. The date of the latest version is shown at the top of the page.</p>')),
    ]
    secs.insert(0, ('', f'<p class="maj">{maj}</p>'))
    return page_texte('confidentialite', tr('Politique de confidentialité', 'Privacy policy'),
                      tr('Voici comment Takedown Studio traite les renseignements personnels que tu nous donnes.', 'Here is how Takedown Studio handles the personal information you give us.'),
                      secs,
                      tr('Politique de confidentialité de Takedown Studio : renseignements recueillis, utilisation, partage, conservation et droits (Loi 25).',
                         'Takedown Studio privacy policy: information collected, use, sharing, retention and your rights (Quebec Law 25).'))

def conditions():
    c = ENTREPRISE['courriel']
    maj = tr('Dernière mise à jour : ', 'Last updated: ') + AUJ
    secs = [
      ('', f'<p class="maj">{maj}</p>'),
      (tr('Utilisation du site', 'Using the site'),
       tr('<p>Le site takedownstudio.com présente les services et les produits de Takedown Studio. En l’utilisant, tu acceptes ces conditions. Tu t’engages à l’utiliser de façon légale et à ne pas tenter de nuire à son fonctionnement.</p>',
          '<p>The takedownstudio.com website presents Takedown Studio’s services and products. By using it, you accept these terms. You agree to use it lawfully and not to try to disrupt its operation.</p>')),
      (tr('Propriété intellectuelle', 'Intellectual property'),
       tr('<p>Les textes, images, illustrations, logos et le design du site appartiennent à Takedown Studio ou sont utilisés avec permission. Tu ne peux pas les copier ni les réutiliser sans notre accord écrit. Les marques et les modèles de produits du catalogue appartiennent à leurs propriétaires respectifs.</p>',
          '<p>The text, images, illustrations, logos and design of the site belong to Takedown Studio or are used with permission. You may not copy or reuse them without our written consent. The brands and product models in the catalogue belong to their respective owners.</p>')),
      (tr('Fichiers que tu nous envoies', 'Files you send us'),
       tr('<p>Si tu nous envoies un logo, un visuel ou une idée, tu confirmes avoir le droit de les utiliser et de nous demander de les reproduire sur des produits. Takedown Studio peut refuser un projet qui contrevient aux droits d’autrui.</p>',
          '<p>If you send us a logo, artwork or an idea, you confirm that you have the right to use it and to ask us to reproduce it on products. Takedown Studio may decline a project that infringes the rights of others.</p>')),
      (tr('Soumissions et information du site', 'Quotes and site information'),
       tr('<p>Une demande envoyée par le formulaire n’est pas un contrat. Les prix, délais, produits et disponibilités présentés sur le site sont donnés à titre indicatif et peuvent changer. Un projet est confirmé seulement par une soumission ou une entente écrite avec Takedown Studio.</p>',
          '<p>A request sent through the form is not a contract. The prices, timelines, products and availability shown on the site are indicative and may change. A project is confirmed only by a written quote or agreement with Takedown Studio.</p>')),
      (tr('Limitation de responsabilité', 'Limitation of liability'),
       tr('<p>On fait de notre mieux pour que l’information du site soit exacte et à jour, mais on ne garantit pas qu’elle soit exempte d’erreurs ni que le site soit toujours disponible. Dans la mesure permise par la loi, Takedown Studio n’est pas responsable des dommages liés à l’utilisation du site ou de sites tiers vers lesquels il renvoie.</p>',
          '<p>We do our best to keep the site information accurate and up to date, but we do not guarantee it is free of errors or that the site is always available. To the extent permitted by law, Takedown Studio is not liable for damages related to the use of the site or of third-party sites it links to.</p>')),
      (tr('Droit applicable', 'Governing law'),
       tr('<p>Ces conditions sont régies par les lois du Québec et les lois du Canada qui s’y appliquent. Les tribunaux du district judiciaire de Bedford sont compétents, sous réserve de tes droits de consommateur.</p>',
          '<p>These terms are governed by the laws of Quebec and the federal laws of Canada applicable therein. The courts of the judicial district of Bedford have jurisdiction, subject to your consumer rights.</p>')),
      (tr('Nous joindre', 'Contact us'),
       tr('<p>Une question sur ces conditions? Écris-nous avec notre petit formulaire.</p>', '<p>Questions about these terms? Write to us using our short form.</p>') + lien_ecrire()),
    ]
    return page_texte('conditions', tr('Conditions d’utilisation', 'Terms of use'),
                      tr('Les règles simples qui encadrent l’utilisation du site de Takedown Studio.', 'The simple rules that apply to using the Takedown Studio website.'),
                      secs,
                      tr('Conditions d’utilisation du site de Takedown Studio : usage du site, propriété intellectuelle, soumissions, responsabilité et droit applicable.',
                         'Terms of use for the Takedown Studio website: site use, intellectual property, quotes, liability and governing law.'))

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
  {phead([(url_p('merci'), tr('Demande envoyée', 'Request sent'))], tr('Merci, on a reçu ta demande!', 'Thank you, we got your request!'),
         tr('On regarde les informations et les fichiers que tu nous as envoyés, puis on te revient par courriel ou par téléphone pour discuter de ton projet.',
            'We will review the information and files you sent, then get back to you by email or phone to talk about your project.'),
         f'<a class="btn btn-w" href="{url_p("realisations")}">{tr("Voir nos réalisations", "See our work")}</a><a class="btn btn-g" href="{url_p("accueil")}">{tr("Retour à l’accueil", "Back to home")}</a>', 'dessins/bonhomme-casquette')}
</main>
{pied(court=True)}'''
    return page(url_p('merci'), tr('Demande envoyée | Takedown Studio', 'Request sent | Takedown Studio'),
                tr('Ta demande de soumission a bien été envoyée à Takedown Studio.', 'Your quote request has been sent to Takedown Studio.'), corps).replace(
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

ANCIENNES_ADRESSES = {'/pages/contact': 'contact', '/pages/custom-apparel-services': 'services',
                      '/policies/privacy-policy': 'confidentialite'}

def redirection(cible):
    """Page de redirection : canonical + refresh + JS + lien visible, hors sitemap."""
    return f'''<!doctype html>
<html lang="fr-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Takedown Studio</title>
<link rel="canonical" href="{cible}">
<meta http-equiv="refresh" content="0;url={cible}">
<script>location.replace({json.dumps(cible)});</script>
</head><body style="font-family:sans-serif;padding:2rem"><p>Cette page a déménagé : <a href="{cible}">clique ici pour continuer</a>.</p></body></html>
'''

def construire():
    if os.path.isdir(SORTIE):
        shutil.rmtree(SORTIE)
    os.makedirs(os.path.join(SORTIE, 'assets'))
    global CSS
    CSS = css_minifie()
    shutil.copytree(os.path.join(ICI, 'statique', 'img'), os.path.join(SORTIE, 'assets', 'img'))
    shutil.copytree(os.path.join(ICI, 'statique', 'documents'), os.path.join(SORTIE, 'assets', 'documents'))
    shutil.copytree(os.path.join(ICI, 'statique', 'polices'), os.path.join(SORTIE, 'assets', 'polices'))
    shutil.copy(os.path.join(ICI, 'statique', 'site.js'), os.path.join(SORTIE, 'assets', 'site.js'))
    images()
    optimiser_images()

    # Fichiers « page.html » : Cloudflare les sert à /page, sans barre oblique finale,
    # comme les adresses du plan de contenu (/services/broderie).
    gabarit = [('accueil', accueil, ()), ('agence', agence, ()), ('services', services_index, ()), ('catalogue', catalogue, ()),
               ('realisations', realisations, ()), ('contact', contact, ()), ('merci', merci, ()),
               ('confidentialite', confidentialite, ()), ('conditions', conditions, ()), ('ecrire', ecrire_page, ())]
    for i, sv in enumerate(SERVICES):
        gabarit.append(('svc:' + sv['slug'], service, (sv, i)))
    global L, PAGE_CLE
    pages = {}
    for langue in ('fr', 'en'):
        L = langue
        for cle, fonction, args in gabarit:
            PAGE_CLE = cle
            r = route_de(cle, langue)
            rel = 'index.html' if r == '/' else 'en/index.html' if r == '/en/' else r.lstrip('/') + '.html'
            pages[rel] = fonction(*args)
    L, PAGE_CLE = 'fr', None
    pages['404.html'] = introuvable()
    # anciennes adresses Shopify encore indexées : pages de redirection (GitHub Pages n'a pas de redirection serveur)
    for ancien, cible in ANCIENNES_ADRESSES.items():
        pages[ancien.strip('/') + '/index.html'] = redirection(BASE + route_de(cible, 'fr'))
    for rel, html in pages.items():
        assert '—' not in html, f'tiret cadratin dans {rel}'
        ecrire(rel, html)

    cles = ['accueil', 'agence', 'services'] + ['svc:' + sv['slug'] for sv in SERVICES] + ['catalogue', 'realisations', 'contact', 'confidentialite', 'conditions', 'ecrire']
    def entree(cle, langue):
        alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{h}" href="{BASE}{route_de(cle, l)}"/>' for h, l in (('fr-CA', 'fr'), ('en-CA', 'en'), ('x-default', 'fr')))
        return f'  <url><loc>{BASE}{route_de(cle, langue)}</loc><lastmod>{AUJ}</lastmod>{alt}</url>\n'
    urls = [entree(cle, langue) for langue in ('fr', 'en') for cle in cles]
    ecrire('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' +
           ''.join(urls) + '</urlset>\n')
    ecrire('robots.txt', f'User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: {BASE}/sitemap.xml\n')
    print(f'✓ {len(pages)} fichiers HTML, {len(urls)} URL dans le sitemap → {SORTIE}')
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
