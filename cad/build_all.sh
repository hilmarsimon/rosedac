#!/usr/bin/env bash
# Erzeugt alle CAD-Ausgaben in cad/out/. Reihenfolge wichtig: frontplatte.py leert zuerst cad/out/ (nur Dateien).
# Voraussetzungen: pip install -r ../requirements.txt; rsvg-convert (librsvg2-bin) und ImageMagick (convert).
set -e
cd "$(dirname "$0")"
for s in frontplatte zeichnung knopf_schnitt knopf_baugruppe knopfplatine_schaltplan seitenansicht ecke_ansicht \
         draufsicht kante_schnitt seitenteil_schnitt deckel seitenrippen platzplan platzplan_ic testfront testfront_vorschau; do
  echo "== $s"; python3 "$s.py"
done
