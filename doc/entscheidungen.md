# Entscheidungen und offene Punkte

## Getroffen

| Thema | Entscheidung | Grund |
|---|---|---|
| Display | 2× Waveshare 5,5" HDMI AMOLED 1080×1920 am Pi 5, quer, Stoß bei x 0,5, HDMI-/USB-Buchse unten; Deckglas 140,4 × 74,76 R4 liegt an der Platte; je 3 Bolzen mit ISO 10642 M2,5×8 von hinten durch die Flansche (Silikonscheibe 0,5 im Spalt 0,3); unterer Flansch je Display für Winkelstecker ausgespart | DFR0524 (Deckglas 138,2 × 81) bräuchte H = 88; echtes Schwarz hinter Dead-Front; Zeichnung/STEP in `doc/datenblaetter/` |
| Gehäusehöhe | H = 82 mm ohne Füße (Original laut Fotos ca. 74 + ca. 9 mm Füße; Datenblatt 88) | Deckglas Waveshare 74,76 + Tasche/Wände; Flansch 11 hoch, Innenkante y ±30 wie zuvor. H = 78 verworfen (DFR0524-Maß war die Platine, nicht das Glas) |
| Front | zweiteilig: Blende (Alu, Lippe 1,5 + Fase 0,4, Rand 4, Wände 2,5, Ecken hinter dem Band) + Träger (Alu, Displaytasche, Taster, Knopflager, Flansche, Laschen); Plexiglas 424,4 × 76,4 × 3 von hinten eingelegt, 1,2 unter der Lippe, 0,3 Dehnspalt, über Poron geklemmt, nicht geklebt | keine sichtbare Fuge Platte/Rahmen; Frontdicke T = 13,5 (Plattenfront 1,5 zurückgesetzt) |
| Blende ↔ Träger | 6× M2,5 Senkkopf von unten (Unterseite); oben hält der Ring über die Seitenwände, Deckelfeder drückt von unten an den Nutsteg der Blende | oben keine sichtbaren Schrauben möglich (Platte muss von hinten durch) |
| Bodenblech | Rechteck 424,6 × 310,6 × 1, von unten in einen umlaufenden Absatz gelegt (Front 5, Seitenwände 2,5, Rückwand 2 breit, 1 tief), Unterseite bündig; 10× ISO 7380 M3×6 (3 Frontflansch, 4 Wulst, 3 Querleiste) | Front, Seiten und Rückwand bis zur Unterkante; Blech von vorn/seitlich/hinten unsichtbar |
| Ziernut / Ecke Deckel–Front | Ziernut 0,6 × 0,15 vorn entlang dem Stoß, seitlich 0,9 breit bis hinten offen, Innenecke R0,2; Fuge 0,3; Blende-Innenecke R0,5 (Fräser Ø1) | nach Bildvergleich (je Variante 2) |
| Testfront | bleibt einteilig, Platte von vorn in Fenstergröße 1,5 zurückgesetzt (Fuge dort sichtbar) | nur Optik-/Funktionstest |
| Deckelnut/Feder | nur links und rechts der Displaytasche (zwei Abschnitte mit Fräserauslauf) | Displaytasche reicht bis y 37,7, Nut läge darin |
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
| Display-Anschluss | HDMI und USB (Versorgung, ca. 0,65 A bei Weiß) zeigen nach unten; im Gerät nur Winkelstecker (90°, nach hinten) möglich, Freiraum ca. 9 mm unter der Buchse | passende Winkelstecker/FPC-Kabel auswählen und gegen den Freischnitt prüfen; Helligkeit nur per Taster am Modul (5 Stufen) – Dimmen in der UI per Software |
| Displaymodul-Dicke | aus STEP: Glas–Bolzenende 8,7, Buchse 11,0 | am Modul nachmessen (Spalt Bolzen/Flansch 0,3) |
| Knopfposition X | 166 mm; Foto deutet 157–160 an | nach Testaufbau entscheiden |
| Wand Displaytasche/Nut | 2,7 mm | bei Fertigung prüfen |
| Innenraum | Platzplan `cad/platzplan.py`: Netz/Trafos rechts, AKD49S mittig hinten zwischen den Ausgängen L/R, IC-Stapel rechts hinten, Pi 5 + Steuerung vorn links; Platinen ≥ 49 mm vor der Rückwand-Innenseite | keine Kollisionen (Gehäuse, Buchsen, Platzhalter untereinander) |
| Rückwand-Ausschnitte | Cinch/BNC/Klinke/Toslink/HDMI/USB/RJ45/IEC nach typischen Maßen | gegen Datenblatt der bestellten Teile prüfen |

## Bezug Kernbauteile (Stand 11/2026, Variante AK-Eigenbau – nur falls doch eigene DAC-Platine)

AK4499EXEQ (Mouser.de ~51 €, DigiKey ~69 $), AK4191EQ (Mouser ~11,5 $), MUSES72320V (DigiKey ~21 $), FifoPi Q7 III (Audiophonics 265 €).
