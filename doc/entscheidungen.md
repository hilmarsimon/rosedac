# Entscheidungen und offene Punkte

## Getroffen

| Thema | Entscheidung | Grund |
|---|---|---|
| Display | 2× DFRobot DFR0524 5,5" AMOLED (HDMI) am Pi 5 | Größe passend zur Front, echtes Schwarz hinter Dead-Front |
| Front-Abdeckung | Plexiglas vollflächig, Musterplatten 9H04 SC und 7H25 GT im Test vergleichen | Dead-Front-Optik wie Original |
| Rahmen-Oberfläche | Glasperlstrahlen + Eloxal schwarz | Originaloptik |
| Deckelhalterung vorn | Nut im Band (Scheibenfräser), einseitige Feder am Deckel, Schaumstoff darunter | keine sichtbaren Schrauben |
| Seitenteile | C-Profil, Wand 5 mm, Wulst innen 9 × 10, 10 Rippen außen | Original-Detailfoto |
| Deckel | ebene 5-mm-Platte über die Seitenteile, Ziernut 0,6 × 0,15 vorn am Stoß, seitlich nach hinten auslaufend | Originalfotos |
| Boden | Blech 1 mm, ISO 7380 M3 in die untere Wulst | |
| Steuerung | RP2040 als Master, Pi 5 nur Renderer + Displays (UART/JSON) | Bedienung unabhängig vom Pi-Boot |
| Eigenentwicklung | nur Steuerplatine, Tasterplatine, Knopfplatine | DAC-/Mixed-Signal-Layout zu riskant für Eigenbau |
| Testaufbau | Front vor der DAC-Bestellung testen | Displays/Optik/Knopf sind unabhängig vom DAC |
| Rückwand | Anordnung wie Original (Handbuch-Reihenfolge, 2 Reihen); nur Einbaubuchsen mit kurzen Kabeln, Neutrik D-Serie für XLR/AES/HDMI/USB/RJ45; E-T-A 1658 als Breaker + C14 mit Sicherung; Gravur nach Eloxal | unabhängig von DAC-Variante A/B, einheitliche Ausschnitte |
| Rückwand: nicht umgesetzt | SFP-USB, EXT. CLOCK 10 MHz (Schalter `REAR_EXT_CLOCK`) | im Modul-Stack keine Funktion |
| COAX 2 (BNC), AES/EBU | Relais-Umschaltung auf den Coax-Eingang der ReceiverPi DDC II, AES über Übertrager 110→75 Ω, RP2040 schaltet | DDC II hat nur einen S/PDIF-Eingang |

## Offen

| Thema | Optionen | Empfehlung / nächster Schritt |
|---|---|---|
| DAC | A: AckoDAC AKD49S (AK4191 + AK4499EX, 835 USD) · B: Ian Canada ES9038Q2M Dual Mono + I/V STD | A, wenn Acko I²C-Steuerung durch RP2040, Takt vom FifoPi, Maße und Versorgung bestätigt; sonst B |
| Eingänge/Takt | Ian Canada ReceiverPi DDC II + FifoPi Q7 III | in beiden Varianten gesetzt |
| Displaymodul-Dicke | Annahme 3 mm (`DISP_T` in `cad/testfront.py`) | am echten DFR0524 messen |
| Fronthöhe | 88 mm; Original-Front evtl. niedriger | nach Displaytest prüfen |
| Knopfposition X | 166 mm; Foto deutet 157–160 an | nach Testaufbau entscheiden |
| Wand Displaytasche/Nut | 2,7 mm | bei Fertigung prüfen |
| Innenraum hinten | Buchsenkörper ragen 20–45 mm nach innen; Platzpläne kollidieren (Ausgabe `platzplan*.py`) | Innenlayout nach DAC-Entscheidung neu: Platinen ≥ 48 mm hinter der Rückwand-Innenseite |
| Rückwand-Positionen | aus Handbuch-Reihenfolge abgeleitet, kein Maßfoto | mit Foto der Original-Rückseite abgleichen; Cinch/BNC/Klinke/Toslink/IEC-Ausschnitte gegen Datenblatt |

## Bezug Kernbauteile (Stand 11/2026, Variante AK-Eigenbau – nur falls doch eigene DAC-Platine)

AK4499EXEQ (Mouser.de ~51 €, DigiKey ~69 $), AK4191EQ (Mouser ~11,5 $), MUSES72320V (DigiKey ~21 $), FifoPi Q7 III (Audiophonics 265 €).
