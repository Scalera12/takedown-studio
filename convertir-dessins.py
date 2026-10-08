#!/usr/bin/env python3
"""Dessins du client (encre noire sur papier blanc, 7 oct. 2026) → PNG blanc sur transparent.

Originaux intacts dans marque/client-2026-10-07-dessins/. Sortie : statique/img/dessins/<nom>-blanc.png
Méthode : on normalise sur le blanc du papier, le trait devient
l'opacité (courbe douce pour garder l'antialiasing), on jette les petites taches isolées et le cadre
de numérisation, puis on recadre serré avec une marge. Couleur : blanc pur, l'encre = l'alpha.

    python3 convertir-dessins.py
"""
import os
import cv2
import numpy as np
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, 'marque', 'client-2026-10-07-dessins')
DEST = os.path.join(ICI, 'statique', 'img', 'dessins')

# nom web → fichier du client (WhatsApp). Les 2 photos de pages complètes sont écartées.
DESSINS = {
    'autocollants-planche':   '14779dde-d67c-48f2-a406-72ff6ce93903.jpg',
    'fil-aiguille':           '25da03a6-1bd7-4143-babd-3f16202fba27.jpg',
    'casquette-tuque-trait':  '2d363e82-ccdd-4ebf-b515-3b59239b4510.jpg',
    'serigraphie-cadre':      '3b81e605-b8d4-4584-88d3-df8c9d7ebfbf.jpg',
    'broderie-aiguille':      '3f92e22b-cc58-4ee8-a2f3-2b399aa3d482.jpg',
    'bonhomme-casquette':     '43cd998f-c588-4687-9b1c-5a8ca875c3c3.jpg',
    'bonhomme-couche':        '768b3afa-7ff3-4ffa-94da-e8c8d7d501eb.jpg',
    'chandail-loupe':         '8222bb41-179d-4b26-a23e-31fff4b12c9b.jpg',
    'serigraphie-racloir':    '9cc8ee3f-9cf2-4ba2-ab1a-ce8c752a0193.jpg',
    'deux-tuques':            'bcbec7b5-c133-4548-b75a-769a94b1603f.jpg',
    'vetements-chandail':     'bffa1c1c-2af8-4567-a118-33cee656e432.jpg',
    'bonhomme-aiguille':      'e374684d-a816-482c-a6bb-9df0924588bd.jpg',   # version plus grande envoyée le soir même (remplace c5735708)
    'chandail-tache':         'd1858f9b-d1f9-4183-a625-cad63c9743d7.jpg',
    'serigraphie-impression': 'd658e2ea-7d0d-4d9d-8437-b9311599dd04.jpg',
    'patch-aiguille':         'e5bcad99-db8c-46cb-a5f8-98d2e3fda4f7.jpg',
    'bonhomme-surpris':       'e6ac4ba7-6ea1-4a17-a2ae-3fc9c27e5a5d.jpg',
    'presse-chaleur':         'f08331ab-7514-4eff-bb05-d61136a85add.jpg',
    'casquettes-tuques-pile': 'f5fcb278-f4f9-425c-b0b5-be0611e42738.jpg',
    'casquette-tuque':        'f813de46-c78f-41ee-a2b7-3c415474f5ff.jpg',
}
# Recadrage manuel (fractions x0, y0, x1, y1) quand il faut retirer quelque chose de l'original.
COUPE = {
    'autocollants-planche': (0, 0, 1, .84),   # retire le mot « stickers. » écrit à la main
}
MAX = 1000      # plus grand côté du PNG de sortie
MARGE = .04     # marge autour du dessin, en fraction du plus grand côté


def convertir(nom, fichier):
    g = cv2.imread(os.path.join(SRC, fichier), cv2.IMREAD_GRAYSCALE).astype(np.float32)
    h, w = g.shape
    if nom in COUPE:
        x0, y0, x1, y1 = COUPE[nom]
        g = g[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
        h, w = g.shape
    # fond du papier : les découpes sont déjà blanches et uniformes, donc un blanc global suffit
    # (un fond estimé localement mangeait les grands aplats d'encre)
    papier = np.percentile(g, 90)
    norm = np.clip(g / max(papier, 1), 0, 1)                # 1 = papier, 0 = encre
    encre = 1 - norm
    # courbe : en dessous de 18 % c'est du papier (grain, ombre), au-dessus de 55 % c'est de l'encre pleine
    a = np.clip((encre - .18) / (.55 - .18), 0, 1)
    a = a * a * (3 - 2 * a)
    # nettoyage : on garde les composantes assez grosses (les gouttes d'encre restent), on jette la poussière
    masque = (a > .5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(masque, 8)
    garde = np.zeros(n, bool)
    seuil = (h * w) * 0.00004
    for i in range(1, n):
        x, y, ww, hh, aire = stats[i]
        touche_bord = x <= 2 or y <= 2 or x + ww >= w - 2 or y + hh >= h - 2
        mince_long = (ww > w * .5 and hh < h * .02) or (hh > h * .5 and ww < w * .02)
        if aire >= seuil and not (touche_bord and mince_long):
            garde[i] = True
    zone = cv2.dilate(garde[lab].astype(np.uint8), np.ones((5, 5), np.uint8))
    a = a * zone
    # recadrage serré + marge
    ys, xs = np.where(a > .2)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    m = int(max(x1 - x0, y1 - y0) * MARGE)
    a = a[max(0, y0 - m):y1 + m, max(0, x0 - m):x1 + m]
    alpha = Image.fromarray((a * 255).round().astype(np.uint8), 'L')
    if max(alpha.size) > MAX:
        r = MAX / max(alpha.size)
        alpha = alpha.resize((round(alpha.width * r), round(alpha.height * r)), Image.LANCZOS)
    im = Image.new('RGBA', alpha.size, (255, 255, 255, 0))
    im.putalpha(alpha)
    im.save(os.path.join(DEST, f'{nom}-blanc.png'), optimize=True)
    return im.size


if __name__ == '__main__':
    os.makedirs(DEST, exist_ok=True)
    for nom, f in DESSINS.items():
        print(f'{nom:24s}', convertir(nom, f))
