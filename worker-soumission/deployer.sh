#!/bin/bash
# Déploie le Worker du formulaire Takedown sur le compte Cloudflare de Scalera.
# Garde : refuse de partir si le compte n'est pas info@scalera.ca.
# Passe par le helper `cf` (jeton du trousseau) quand le jeton « scalera » existe,
# sinon par la session wrangler SEULEMENT si elle répond info@scalera.ca.
# account_id est aussi épinglé dans wrangler.jsonc (double sécurité).
#
# Usage : ./deployer.sh
set -e
cd "$(dirname "$0")"

COMPTE=$(tr -d ' \n' < .cloudflare-compte)
ATTENDU="info@scalera.ca"
ID_ATTENDU="66af920c9f23ce05fd9c829f3191788e"
CF="$HOME/.local/bin/cf"

if [ -x "$CF" ] && security find-generic-password -s cloudflare-wrangler -a "$COMPTE" >/dev/null 2>&1; then
  W() { "$CF" "$COMPTE" "$@"; }
  echo "→ Jeton « $COMPTE » du trousseau"
else
  W() { npx --yes wrangler@4 "$@"; }
  echo "→ Pas de jeton « $COMPTE » dans le trousseau (cf ajouter $COMPTE) : session wrangler, vérifiée ci-dessous"
fi

SORTIE=$(W whoami 2>&1) || { echo "$SORTIE"; exit 1; }
COURRIEL=$(echo "$SORTIE" | grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | head -1)
if ! echo "$SORTIE" | grep -q "$ID_ATTENDU"; then
  echo "✗ DÉPLOIEMENT BLOQUÉ : le compte $ID_ATTENDU (Scalera) n'est pas accessible avec cette session (${COURRIEL:-inconnu})."
  exit 1
fi
if [ -n "$COURRIEL" ] && [ "$COURRIEL" != "$ATTENDU" ]; then
  echo "✗ DÉPLOIEMENT BLOQUÉ : session $COURRIEL, attendu $ATTENDU."
  exit 1
fi
echo "✓ Compte ${COURRIEL:-$COMPTE} ($ID_ATTENDU)"
grep -q '"DESTINATAIRE": "info@scalera.ca"' wrangler.jsonc && echo "  (mode ESSAI : courriels vers info@scalera.ca)"
W deploy "$@"
