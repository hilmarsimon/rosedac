# Entscheidungen und offene Punkte

## Getroffen

| Thema | Entscheidung | Grund |
|---|---|---|
| Display | 2× DFRobot DFR0524 5,5" AMOLED (HDMI) am Pi 5 | Größe passend zur Front, echtes Schwarz hinter Dead-Front |
| Gehäusehöhe | H = 78 mm ohne Füße (Original laut Front-/Rückseitenfoto ca. 74 + ca. 9 mm Füße; Datenblatt 88 inkl. Füße) | +4 mm, damit die DFR0524 (71 mm) passen; Alternative 6,52" AMOLED PO652F2K bei H = 74 verworfen (Kosten, Board offen) |
| Deckelnut/Feder | nur links und rechts der Displaytasche (zwei Abschnitte mit Fräserauslauf) | bei H = 78 reicht die Displaytasche bis y 36, Nut läge darin |
| Front-Abdeckung | Plexiglas vollflächig, Musterplatten 9H04 SC und 7H25 GT im Test vergleichen | Dead-Front-Optik wie Original |
| Rahmen-Oberfläche | Glasperlstrahlen + Eloxal schwarz | Originaloptik |
| Deckelhalterung vorn | Nut im Band (Scheibenfräser), einseitige Feder am Deckel, Schaumstoff darunter | keine sichtbaren Schrauben |
| Seitenteile | C-Profil, Wand 5 mm, Wulst innen 9 × 10, 10 Rippen außen | Original-Detailfoto |
| Deckel | ebene 5-mm-Platte über die Seitenteile, Ziernut 0,6 × 0,15 vorn am Stoß, seitlich nach hinten auslaufend | Originalfotos |
| Boden | Blech 1 mm, ISO 7380 M3 in die untere Wulst | |
| Steuerung | RP2040 als Master, Pi 5 nur Renderer + Displays (UART/JSON) | Bedienung unabhängig vom Pi-Boot |
| Eigenentwicklung | nur Steuerplatine, Tasterplatine, Knopfplatine | DAC-/Mixed-Signal-Layout zu riskant für Eigenbau |
| Testaufbau | Front vor der DAC-Bestellung testen | Displays/Optik/Knopf sind unabhängig vom DAC |
| Rückwand | Anordnung nach Originalfoto (Kanal R links, Digital Mitte, Kanal L rechts, Gravurrahmen wie Druck); Einbaubuchsen mit Kabeln, XLR/AES Neutrik D, E-T-A 1658 + C14 mit Sicherung | Optik Original, unabhängig von DAC-Variante |
| Rückwandbefestigung | 10× M3 Senkkopf wie Original: 4 oben/4 unten in Querleisten Alu 10×10 (oben am Deckel, unten am Boden verschraubt), 2 seitlich mittig in Block im Seitenteil | Foto; Querleisten versteifen das Gehäuse hinten |
| Abweichungen Rückwand | SFP-Platz → LAN (Pi 5), SVC → USB-C RP2040, EXT. CLOCK entfällt (`EXT_CLOCK`), eigenes Typenschild statt Logo/Zulassungszeichen | Modul-Stack; keine fremden Marken/Prüfzeichen |
| COAX 2 (BNC), AES/EBU | Relais-Umschaltung auf den Coax-Eingang der ReceiverPi DDC II, AES über Übertrager 110→75 Ω, RP2040 schaltet | DDC II hat nur einen S/PDIF-Eingang |

## Offen

| Thema | Optionen | Empfehlung / nächster Schritt |
|---|---|---|
| DAC | **Entschieden 11/2026:** AckoDAC AKD49S (AK4191 + AK4499EX, I-V onboard, ±15 V) + Ian Canada ReceiverPi DDC II + FifoPi Q7 III (Reclocking, MCLK) + PurePi II; Eigenbau: Steuer-, Taster-, Knopfplatine, kleine Eingangsplatine (Relais-Mux Coax 1/2 + AES-Übertrager) | wenig Eigenentwicklung, AK4499EX-Klang; Variante IC-DAC (ES9038Q2M) verworfen |
| Acko-Klärung | Platinenmaße/Bohrbild, Ströme ±15 V, I²S-Direkteingang + ext. MCLK (Pegel, Frequenz vom FifoPi), Ausgänge als Stiftleiste statt XLR/Cinch, I²C-API für RP2040 | Anfrage an Acko, Platzhalter 175 × 102 im Platzplan |
| Eingänge/Takt | Ian Canada ReceiverPi DDC II + FifoPi Q7 III | in beiden Varianten gesetzt |
| Displaymodul-Dicke | Annahme 3 mm (`DISP_T` in `cad/testfront.py`) | am gewählten Display messen |
| Knopfposition X | 166 mm; Foto deutet 157–160 an | nach Testaufbau entscheiden |
| Wand Displaytasche/Nut | 2,7 mm | bei Fertigung prüfen |
| Innenraum | Platzplan `cad/platzplan.py`: Netz/Trafos rechts, AKD49S mittig hinten zwischen den Ausgängen L/R, IC-Stapel rechts hinten, Pi 5 + Steuerung vorn links; Platinen ≥ 49 mm vor der Rückwand-Innenseite | keine Kollisionen (Gehäuse, Buchsen, Platzhalter untereinander) |
| Rückwand-Ausschnitte | Cinch/BNC/Klinke/Toslink/HDMI/USB/RJ45/IEC nach typischen Maßen | gegen Datenblatt der bestellten Teile prüfen |

## Bezug Kernbauteile (Stand 11/2026, Variante AK-Eigenbau – nur falls doch eigene DAC-Platine)

AK4499EXEQ (Mouser.de ~51 €, DigiKey ~69 $), AK4191EQ (Mouser ~11,5 $), MUSES72320V (DigiKey ~21 $), FifoPi Q7 III (Audiophonics 265 €).
