#!/usr/bin/env bash
# Erzeugt alle CAD-Ausgaben in cad/out/ und sortiert sie nach Typ: out/cad (STEP/STL), out/dxf, out/pdf, out/bilder, out/daten. Reihenfolge wichtig: frontplatte.py leert zuerst cad/out/ (nur Dateien).
# Voraussetzungen: pip install -r ../requirements.txt; rsvg-convert (librsvg2-bin) und ImageMagick (convert).
set -e
cd "$(dirname "$0")"
rm -rf out/cad out/dxf out/pdf out/bilder out/daten out/testfront   # alte, sortierte Ausgaben entfernen
for s in frontplatte zeichnung knopf_schnitt knopf_baugruppe knopfplatine_schaltplan seitenansicht ecke_ansicht \
         draufsicht kante_schnitt display_schnitt seitenteil_schnitt deckel rueckwand seitenrippen platzplan gehaeuse_baugruppe testfront testfront_vorschau; do
  echo "== $s"; python3 "$s.py"
done
echo "== Ausgaben sortieren"; python3 sortiere_ausgaben.py
