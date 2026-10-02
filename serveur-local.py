# -*- coding: utf-8 -*-
"""Sert site/ en local comme Cloudflare le fera : /services/broderie → services/broderie.html.
Usage : python3 serveur-local.py [port]"""
import os, sys, http.server, functools
from urllib.parse import urlsplit

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')

class Gestion(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        chemin = urlsplit(self.path).path
        fichier = os.path.join(RACINE, chemin.lstrip('/'))
        sans_index = os.path.isdir(fichier) and not os.path.exists(os.path.join(fichier, 'index.html'))
        if chemin != '/' and (not os.path.exists(fichier) or sans_index) and os.path.exists(fichier.rstrip('/') + '.html'):
            self.path = chemin.rstrip('/') + '.html' + ('?' + urlsplit(self.path).query if urlsplit(self.path).query else '')
        elif chemin != '/' and not os.path.exists(fichier):
            self.path = '/404.html'
        return super().send_head()
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
http.server.ThreadingHTTPServer(('', port), functools.partial(Gestion, directory=RACINE)).serve_forever()
