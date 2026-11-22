# RD160-Nachbau – Testaufbau Front (Displays, Plexiglas, Drehknopf)

Ziel: Displays, Dead-Front-Optik und Drehknopf prüfen, **bevor** DAC-Module (Acko oder Ian Canada) bestellt werden.
Alles hier wird später im Gerät weiterverwendet.

## 1. Einkaufsliste

| Teil | Menge | Hinweis |
|---|---|---|
| Raspberry Pi 5 (4 GB reicht) + offizielles 27-W-Netzteil + microSD 32 GB | 1 | Pi OS Lite 64 bit |
| DFRobot DFR0524 5,5" AMOLED 1080×1920 (HDMI) | 2 | je ein Micro-HDMI-auf-HDMI-Kabel bzw. Adapter |
| PLEXIGLAS LED Black & White 9H04 SC (matt), 3 mm | 1 Muster ≥ 210 × 160 | ergibt 2 Testhälften (DXF) |
| PLEXIGLAS LED Black & White 7H25 GT (glänzend), 3 mm | 1 Muster ≥ 210 × 160 | Vergleich |
| Raspberry Pi Pico (RP2040) | 1 | MicroPython |
| AS5600-Breakout (≈ 23 × 23 mm) + Diametralmagnet 6 × 2,5 mm | 1 | Magnet liegt meist bei |
| Rillenkugellager 6805-2RS (25 × 37 × 7) | 1 | |
| O-Ring 26 × 2 NBR | 1 | Dämpfung |
| 3-mm-LED weiß, diffus | 12 | + 12× 200 Ω |
| AO3400A (SOT-23 auf Adapter) oder 2N7000 | 1 | LED-Treiber, 100 Ω Gate, 100 kΩ Pull-down |
| Taster 6 × 6 (z. B. Omron B3F-1000) | 11 | 10 Bedientaster + Einschalttaster |
| Einschmelzmuttern M3 (Ruthex M3 × 5,7) | 16 | |
| Schrauben M3 × 8 / M3 × 12, Passstifte Ø3 × 15 | je 10 / 2 | |
| Schaumstoff 1 mm selbstklebend | Rest | zwischen Klammer und Display |
| Dämpfungsfett (Nyogel 767A oder ähnlich) | wenig | Drehgefühl |

## 2. Druckteile (Ordner `cad/out/testfront/`, STL + STEP; erzeugt von `cad/testfront.py`)

**Testfront einteilig (empfohlen):** `Testfront_einteilig_CNC.step` (430 × 88 × 12) bei JLCCNC aus **POM schwarz** fräsen lassen,
M3-Gewinde direkt in POM (Gewinde in der Bestellung angeben). Alternativ `Testfront_einteilig_Druck.stl/.step` (Ø4 für Einschmelzmuttern)
bei einem Druckdienst mit Bauraum ≥ 440 mm (SLA-Harz schwarz). Zweiteilige Druckversion nur für eigene Drucker < 440 mm.

| Datei | Material | Ausrichtung |
|---|---|---|
| Testfront_links / Testfront_rechts (je 215 × 88 × 12) | PETG schwarz, 0,2 mm, 4 Wände | Rückseite aufs Bett |
| Displayklammer (4×) | PETG | Lasche aufs Bett |
| Sensorhalter_Knopf | PETG | flache Seite aufs Bett |
| Knopf_Becher, Knopf_Konus, Knopf_Haltescheibe | PLA/PETG (Alu später CNC) | Öffnung nach oben |
| Knopf_Lichtleiter | klares Harz (SLA) oder klares PETG | stehend |
| Tasterkappe (10×), Einschaltkappe | PETG/Harz | Kopf nach oben |

Plexiglas: `Plexiglas_Testhaelfte_links/rechts.dxf` (je 210,0 × 79,4 mm, mit Tasterbohrungen bzw. Knopfausschnitt) lasern lassen.
Lagersitz Ø37 nach dem Druck mit Schleifpapier auf Presssitz bringen.

## 3. Montage

1. Einschmelzmuttern in alle Ø4-Bohrungen der Rückseite setzen.
2. Hälften mit Passstiften Ø3 und etwas Sekundenkleber verbinden; Front plan auf eine Glasplatte drücken.
3. Plexiglashälften in die Fronttasche legen (vorerst nur mit 2 Streifen Kapton-Band halten – Muster tauschbar).
4. Displays von hinten in die Displaytaschen, aktive Fläche Richtung Front; mit den 4 Displayklammern (1 mm Schaumstoff auf dem Finger) an den Bohrungen ±127/±25 halten. **Dicke des Displaymoduls messen** und ggf. `DISP_T` in `testfront.py` anpassen.
5. Knopf: O-Ring in die Nut, Lager einpressen, Becher mit Lichtleiter und Konus einsetzen, Magnet in die Nabe kleben (Klebstoff, Polung egal), Haltescheibe mit 3× M2,5 von hinten.
6. Sensorhalter: AS5600-Breakout (Chip nach vorn) in die Tasche, 12 LEDs von hinten in den Lichtkreis, Einschalttaster einsetzen; mit 4× M3 × 12 an den Träger. Abstand Chip–Magnet ≈ 2,5 mm.

## 4. Verdrahtung Pico

| Pico | an |
|---|---|
| 3V3 / GND | AS5600 VCC / GND, DIR → GND |
| GP4 / GP5 | AS5600 SDA / SCL |
| GP10 … GP19 | Taster INPUT▲, INPUT▼, SAMPLING▲, SAMPLING▼, FILTER▲, FILTER▼, DIMMING, MUTE, CLOCK INPUT, SOUND WAVE (jeweils gegen GND) |
| GP20 | Einschalttaster (gegen GND) |
| GP22 | 100 Ω → Gate MOSFET; Drain an LED-Kathoden-Sammelleitung; LEDs mit je 200 Ω an VBUS (5 V) |
| USB | an Pi 5 (Daten + Strom) |

## 5. Software

**Pico:** MicroPython-Firmware aufspielen, `test/pico/main.py` mit Thonny als `main.py` auf den Pico speichern.

**Pi 5 (Pi OS Lite 64 bit):**
```bash
sudo apt install -y python3-pygame python3-serial fonts-dejavu-core
mkdir -p ~/rd160 && cp test/pi/rd160_ui.py ~/rd160/
# Test von Hand (Konsole, kein Desktop):
SDL_VIDEODRIVER=kmsdrm python3 ~/rd160/rd160_ui.py
# Hochformat-Displays quer: falls Bild gedreht -> --rotate 90 (oder 270); Displays vertauscht -> --swap
# Autostart:
sudo cp test/pi/rd160-ui.service /etc/systemd/system/ && sudo systemctl enable --now rd160-ui
```
Entwicklung am PC ohne Hardware: `python3 test/pi/rd160_ui.py --windowed` (Tastatur statt Knopf).

Tasten: ←/→ Lautstärke · I/K Eingang · S/X Abtastrate · F/V Filter · D Dimmen · M Mute · W Wellenform · P Standby ·
**1** Schwarz · **2** Weiß · **3** Graukeil · **4** Bedienoberfläche · **5** Rahmen (aktive Fläche) · **6** Schriftproben

## 6. Prüfprotokoll

Jeweils mit 9H04 SC **und** 7H25 GT durchführen; Fotos vom Original (Pressebilder) daneben legen.

| # | Prüfung | Vorgehen | Ziel | SC | GT |
|---|---|---|---|---|---|
| 1 | Dead Front aus | Displays aus (Taste P), Deckenlicht + Lampe 45° seitlich | Displaykante und Fläche nicht erkennbar, gleichmäßig schwarz | | |
| 2 | Schwarz bei „an“ | Testbild 1 | kein sichtbares Rechteck / kein Grauschleier | | |
| 3 | Helligkeit | Testbild 4 bei Dimmstufe 100 / 60 / 30 % | Tageslicht gut lesbar, abends nicht blendend | | |
| 4 | Schärfe | Testbild 6 | 34-px-Schrift aus 1 m klar lesbar | | |
| 5 | Lage der aktiven Fläche | Testbild 5 | Außenrahmen sitzt mittig in der Tasche, Fuge zwischen den Displays ≤ 2 mm | | |
| 6 | Blickwinkel | Testbild 2/4, ±60° horizontal und vertikal | kein Farbumschlag, Weiß bleibt neutral | | |
| 7 | Graustufen | Testbild 3 | alle 16 Stufen unterscheidbar, keine Stufe abgesoffen | | |
| 8 | Spiegelung | Fenster/Lampe im Rücken | vergleichbar mit Originalfotos | | |
| 9 | Drehgefühl | Knopf drehen, mit/ohne Dämpfungsfett | gleichmäßig, kein Spiel, satter Widerstand | | |
| 10 | Auflösung | eine Umdrehung | ≈ 48 Schritte, keine Sprünge/Rücksprünge (`COUNTS_PER_STEP`) | | |
| 11 | Reaktionszeit | Handy-Zeitlupe 240 fps: Drehung → Zahl ändert sich | < 50 ms | | |
| 12 | LED-Ring | Dimmen D, im Dunkeln | gleichmäßiger Ring ohne Einzelpunkte, kein Flimmern | | |
| 13 | Taster | alle 10 + Einschalttaster | jede Betätigung genau ein Ereignis | | |
| 14 | Dauer | 4 h Laufzeit | keine Abstürze, Displays/Plexiglas nicht warm > 40 °C | | |

**Ergebnis / Entscheidung:** Plexiglas-Typ ______  Displays geeignet ja/nein ______  Änderungen an Front/Knopf: ______
