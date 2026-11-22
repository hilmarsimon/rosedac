# rosedac – DIY-Nachbau HiFi Rose RD160

Nachbau des HiFi Rose RD160 (DAC mit Dual-AMOLED-Front hinter Plexiglas, beleuchteter Drehknopf, Alu-Gehäuse 430 × 88 × 327 mm).
Schwerpunkt bisher: Front, Drehknopf, Gehäuse, Bedienlogik, Hardware-Architektur, Testaufbau.

## Struktur

| Ordner | Inhalt |
|---|---|
| `cad/` | Parametrische CAD-Skripte (CadQuery/Python), Zeichnungen, Ansichten, Platzpläne |
| `cad/out/` | Erzeugte Dateien: STEP, PDF, PNG, DXF, CSV (Stand im Repo = letzter Build) |
| `cad/out/testfront/` | Testfront 1:1 (einteilig CNC/Druck, zweiteilig Druck), Knopfteile, Plexiglas-DXF |
| `test/` | Testaufbau Displays/Plexiglas/Drehknopf: Pi-UI (`pi/`), RP2040-Firmware (`pico/`), Anleitung + Prüfprotokoll |
| `doc/` | Entscheidungen, offene Punkte, Bezugsquellen |

## Bauen

```bash
pip install -r requirements.txt          # + Systempakete: librsvg2-bin, imagemagick
cad/build_all.sh                          # erzeugt alles in cad/out/
```
Zentrale Parameter (Maße, Laschen, Deckel, Nut, Rippen, Knopf) stehen in `cad/frontplatte.py`; alle anderen Skripte importieren sie.

## Stand (11/2026)

- **Front:** Alu-Rahmen 430 × 88, Plexiglas 9H04 SC/7H25 GT vollflächig, 2× DFRobot DFR0524 5,5" AMOLED, 10 Taster, Einschalttaster.
- **Drehknopf:** Alu-Becher Ø50, PMMA-Lichtleiter, Lager 6805-2RS, AS5600 + Magnet, 12 weiße LEDs (PWM ≥ 25 kHz); Knopfplatine mit Schaltplan.
- **Gehäuse:** Seitenteile als C-Profil mit Rippen außen; Front ↔ Seitenteil über waagerechte Laschen + senkrechte M3-Senkschraube;
  Deckel 5 mm eben mit Feder in Nut im Band, Schaumstoff, Ziernut; hinten von unten verschraubt; Bodenblech 1 mm.
- **Architektur:** Pi 5 (Renderer + Displays), RP2040 als Master (Bedienung, I²C/SPI zum DAC, UART zum Pi), 3 Ringkerne linear.
- **DAC:** offen – Variante AK (AckoDAC AKD49S, AK4191 + AK4499EX) oder Variante Ian Canada (ES9038Q2M Dual Mono). Siehe `doc/entscheidungen.md`.
- **Nächster Schritt:** Testaufbau Front (Displays, Plexiglas, Knopf) vor der DAC-Bestellung – `test/README.md`.

## Links (privat)

- Blockschaltbild (Whiteboard): https://claude.ai/artifact/UPaNxN4nF1NFZ33DLWigmk
- Bedienlogik (Doc): https://claude.ai/artifact/NB5RAEfV8VzS8VQHGWQxaS
