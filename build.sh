#!/usr/bin/env bash
# ============================================================
#  build.sh — Construit MonExtension.oxt
#  Usage : bash build.sh
# ============================================================
set -e
EXTENSION_NAME="Elise"
OUT="${EXTENSION_NAME}.oxt"

echo "→ Nettoyage..."
rm -f "$OUT"

cd src

echo "→ Création de l'archive..."
zip -r ../"$OUT" \
  META-INF/ \
  description.xml \
  description/ \
  addons.xcu \
  WriterWindowState.xcu \
  elise/ \
  images/ \
  icons/

cd .

echo "✓ Extension créée : $OUT"
echo ""
echo "Installation :"
echo "  LibreOffice → Outils → Gestionnaire d'extensions → Ajouter"
