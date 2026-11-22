# CLAUDE.md – rosedac

DIY-Nachbau HiFi Rose RD160. Sprache in Code-Kommentaren, Doku und Antworten: Deutsch, knapp.

## Arbeitsweise
- CAD nur über die Skripte in `cad/` (CadQuery). Maße/Parameter zentral in `cad/frontplatte.py`; nichts in anderen Skripten doppelt definieren.
- Nach jeder Geometrieänderung: `cad/build_all.sh` laufen lassen (frontplatte.py zuerst – sie leert `cad/out/`), dann
  Gültigkeit (`isValid()`) und Kollisionen (`intersect().Volume()`) prüfen. Die Kollisionsprüfung steht am Ende von `frontplatte.py`.
- Erzeugte Dateien in `cad/out/` werden mit eingecheckt (Bestellung bei JLCCNC/JLCPCB direkt aus dem Repo).
- SVG-Ansichten: Ausrichtung per PNG-Drehung korrigieren (Rückansicht −90°, Vorderansicht +90°, Rx(90) auf dem Compound).
- Test-Software: `test/pi/rd160_ui.py` (pygame, zwei Fenster, kmsdrm), `test/pico/main.py` (MicroPython). Protokoll RP2040 ↔ Pi:
  JSON-Zeilen `{"ev":"enc","d":n}`, `{"ev":"btn","id":"..."}`, `{"cmd":"led","v":0..255}` – bleibt für die spätere C-Firmware gleich.
- Entscheidungen und offene Punkte in `doc/entscheidungen.md` nachführen.
- Bei Anweisungsblöcken für Claude Code jeweils das Modell angeben (opus für Urteilsaufgaben, sonnet für Routine).
