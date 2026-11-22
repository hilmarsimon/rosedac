"""Stromlaufplan Knopfplatine RD160-Nachbau (AS5600 + 12 LEDs + Einschalttaster).
Blöcke über Netznamen verbunden. Ausgabe: PDF, SVG, PNG + Stückliste (CSV)."""
import os, csv
import schemdraw
import schemdraw.elements as elm

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
schemdraw.config(fontsize=10, lw=1.0)
FS = 9


def net(d, name, side="right"):
    d.add(elm.Label().label(name, loc="center", fontsize=FS, halign="left" if side == "right" else "right",
                            ofst=(0.15 if side == "right" else -0.15, 0)))


def block_title(d, xy, text):
    d.add(elm.Label().at(xy).label(text, fontsize=10.5, halign="left"))


with schemdraw.Drawing(show=False) as d:
    d.config(unit=2.0)
    d += elm.Label().at((0, 23.5)).label(
        "RD160-Nachbau · Knopfplatine (Drehgeber, LED-Ring, Einschalttaster) · Rev A · 2026-11-21",
        fontsize=13, halign="left")

    # =============== Block 1: LED-Ring ===============
    block_title(d, (0, 21.6), "LED-Ring: 12 × weiß, je 10 mA, PWM-gedimmt")
    x0, ytop, pitch = 1.0, 20.2, 1.55
    d += elm.Line().at((x0 - 0.8, ytop)).right(0.8 + 11 * pitch + 2.2)
    d.add(elm.Label().at((x0 - 0.8, ytop)).label("+5V_LED", loc="center", fontsize=FS, halign="right", ofst=(-0.15, 0)))
    for k in range(12):
        x = x0 + k * pitch
        d += elm.Dot().at((x, ytop))
        d += elm.Resistor().at((x, ytop)).down(1.6).label(f"R{3 + k}\n200 Ω", loc="top", fontsize=7)
        d += elm.LED().down(1.6).label(f"D{1 + k}", loc="top", fontsize=7)
    yk = ytop - 3.2
    d += elm.Line().at((x0, yk)).right(11 * pitch + 3.0)
    for k in range(12):
        d += elm.Dot().at((x0 + k * pitch, yk))
    d.add(elm.Label().at((x0 + 11 * pitch + 0.3, yk)).label("LED_K", fontsize=8, halign="left", ofst=(0, -0.35)))
    # C3 am Ende der Schiene
    xc3 = x0 + 11 * pitch + 2.2
    d += elm.Dot().at((xc3, ytop))
    d += elm.Capacitor().at((xc3, ytop)).down(1.4).label("C3\n10 µF", loc="bottom", fontsize=8)
    d += elm.Ground()
    # Q1 Low-Side-Schalter
    xq = x0 + 11 * pitch + 3.0
    Q1 = d.add(elm.NFet().theta(0).anchor("drain").at((xq, yk)).label("Q1\nAO3400A", loc="left", fontsize=8))
    d += elm.Ground().at(Q1.source)
    d += elm.Line().at(Q1.gate).right(0.6)
    g = d.add(elm.Dot())
    d += elm.Resistor().right(2.4).label("R15 220 Ω", loc="top", fontsize=8)
    net_end = d.here
    d.add(elm.Label().at(net_end).label("LED_PWM", fontsize=FS, halign="left", ofst=(0.15, 0)))
    d += elm.Resistor().at(g.center).down(1.6).label("R16\n100 kΩ", loc="top", fontsize=8)
    d += elm.Ground()

    # =============== Block 2: Stecker J1 ===============
    block_title(d, (0, 13.2), "Stecker zum Controller")
    pins = [("PWR_SW", "7", "sw"), ("LED_PWM", "6", "pwm"), ("SCL", "5", "scl"), ("SDA", "4", "sda"),
            ("+3V3", "3", "p33"), ("GND", "2", "gnd"), ("+5V", "1", "p5")]
    J1 = d.add(elm.Ic(pins=[elm.IcPin(name=n, pin=p, side="right", anchorname=a) for n, p, a in pins],
                      pinspacing=1.2, edgepadH=0.5, w=2.4,
                      label="J1  JST B7B-PH-K-S", lblloc="bottom").at((0.2, 3.0)).theta(0))
    for n, _, a in pins:
        p = getattr(J1, a)
        if n == "+5V":
            d += elm.Line().at(p).right(0.6)
            d += elm.Inductor2(loops=2).right(1.6).label("FB1", loc="top", fontsize=8)
            d += elm.Line().right(0.4)
            net(d, "+5V_LED")
        elif n == "GND":
            d += elm.Line().at(p).right(1.2)
            d += elm.Ground()
        else:
            d += elm.Line().at(p).right(2.6)
            net(d, n)

    # =============== Block 3: Drehgeber AS5600 ===============
    block_title(d, (9.0, 13.2), "Drehgeber (mittig unter dem Magneten)")
    as_pins = [elm.IcPin(name="VDD5V", pin="1", side="left", anchorname="vdd5"),
               elm.IcPin(name="VDD3V3", pin="2", side="left", anchorname="vdd33"),
               elm.IcPin(name="GND", pin="4", side="left", anchorname="gnd"),
               elm.IcPin(name="DIR", pin="8", side="left", anchorname="dir"),
               elm.IcPin(name="SDA", pin="6", side="right", anchorname="sda"),
               elm.IcPin(name="SCL", pin="7", side="right", anchorname="scl"),
               elm.IcPin(name="OUT", pin="3", side="right", anchorname="out"),
               elm.IcPin(name="PGO", pin="5", side="right", anchorname="pgo")]
    U1 = d.add(elm.Ic(pins=as_pins, pinspacing=1.6, edgepadH=0.6, w=3.0,
                      label="U1  AS5600-ASOM (SOIC-8)", lblloc="bottom").at((15.0, 4.4)).theta(0))
    xb = U1.vdd5[0] - 1.6
    d += elm.Line().at(U1.vdd5).left(1.6)
    nb = d.add(elm.Dot())
    d += elm.Line().at(U1.vdd33).left(1.6)
    d += elm.Dot()
    d += elm.Line().at((xb, U1.vdd5[1])).to((xb, U1.vdd33[1]))
    d += elm.Line().at((xb, U1.vdd33[1])).up(0.6)
    d.add(elm.Label().label("+3V3", loc="center", fontsize=FS, ofst=(0, 0.35)))
    d += elm.Line().at(nb.center).left(1.2)
    c1 = d.add(elm.Dot())
    d += elm.Capacitor().down(1.4).label("C1\n100 nF", loc="bottom", fontsize=8)
    d += elm.Ground()
    d += elm.Line().at(c1.center).left(1.6)
    d += elm.Capacitor().down(1.4).label("C2\n1 µF", loc="bottom", fontsize=8)
    d += elm.Ground()
    for a in ("gnd", "dir"):
        p = getattr(U1, a)
        d += elm.Line().at(p).left(0.9)
        d += elm.Ground()
    for a, n in (("sda", "SDA"), ("scl", "SCL")):
        d += elm.Line().at(getattr(U1, a)).right(1.6)
        net(d, n)
    d += elm.Line().at(U1.out).right(1.2)
    d += elm.Dot(open=True).label("TP1", loc="right", fontsize=8)
    d += elm.Line().at(U1.pgo).right(1.2)
    d += elm.Dot(open=True).label("TP2", loc="right", fontsize=8)

    # =============== Block 4: I²C-Pull-ups ===============
    block_title(d, (24.0, 13.2), "I²C-Pull-ups (nur einmal im Bus)")
    for i, (r, n) in enumerate((("R1", "SDA"), ("R2", "SCL"))):
        y = 11.6 - i * 1.6
        d.add(elm.Label().at((24.6, y)).label("+3V3", fontsize=FS, halign="right", ofst=(-0.15, 0)))
        d += elm.Line().at((24.6, y)).right(0.4)
        d += elm.Resistor().right(2.0).label(f"{r} 4,7 kΩ", loc="top", fontsize=8)
        d += elm.Line().right(0.4)
        net(d, n)

    # =============== Block 5: Einschalttaster ===============
    block_title(d, (24.0, 7.6), "Einschalttaster (aktiv low)")
    d.add(elm.Label().at((24.6, 6.0)).label("PWR_SW", fontsize=FS, halign="right", ofst=(-0.15, 0)))
    d += elm.Line().at((24.6, 6.0)).right(0.5)
    s0 = d.add(elm.Dot())
    d += elm.Resistor().right(2.0).label("R17 1 kΩ", loc="top", fontsize=8)
    s1 = d.add(elm.Dot())
    d += elm.Button().at(s1.center).down(1.8).label("SW1\nB3F-1000", loc="bottom" if False else "top", fontsize=8,
                                                     ofst=(0.9, 0))
    d += elm.Ground()
    d += elm.Capacitor().at(s0.center).down(1.8).label("C4\n10 nF", loc="bottom", fontsize=8)
    d += elm.Ground()

    # =============== Hinweise ===============
    notes = ("HINWEISE\n"
             "1  AS5600 im 3,3-V-Betrieb: VDD5V und VDD3V3 verbunden (laut Datenblatt). Chip exakt auf der Knopfachse.\n"
             "   DIR an GND: Winkel steigt beim Drehen im Uhrzeigersinn (Blick auf die Front); sonst in der Firmware umkehren.\n"
             "2  Luftspalt Magnet–Chipoberfläche zulässig 0,5–3 mm; Konstruktion 2,5 mm.\n"
             "3  LEDs weiß PLCC-2 3528: If = (5 V − 3,0 V) / 200 Ω ≈ 10 mA, gesamt ≈ 120 mA. Teilkreis Ø43,3 mm unter den Lichtfenstern.\n"
             "4  PWM ≥ 25 kHz (unhörbar); R15 macht die Schaltflanken weicher (weniger Einstreuung ins Audio).\n"
             "5  R1/R2 nur bestücken, wenn der Controller keine I²C-Pull-ups hat.\n"
             "6  PWR_SW: Pull-up im RP2040 (intern), aktiv low; R17/C4 = Entprellung und ESD-Schutz.\n"
             "7  Kabel J1 höchstens 30 cm; GND-Ader zwischen SDA und SCL.\n"
             "8  H1–H4 M3 nicht durchkontaktiert: keine Masseverbindung zum Rahmen über die Platine.")
    d += elm.Label().at((0, -1.4)).label(notes, fontsize=8.5, halign="left", valign="top")

    for ext in ("svg", "pdf"):
        d.save(os.path.join(OUT, f"RD160_Knopfplatine_Stromlaufplan.{ext}"))
    d.save(os.path.join(OUT, "RD160_Knopfplatine_Stromlaufplan.png"), dpi=150)

bom = [
    ("U1", 1, "AS5600-ASOM", "Magnet-Drehgeber 12 bit, I²C 0x36", "SOIC-8"),
    ("D1–D12", 12, "LED weiß PLCC-2 3528", "Leuchtring, ~3,0 V @ 10 mA", "PLCC-2 3528"),
    ("R3–R14", 12, "200 Ω 1 %", "LED-Vorwiderstand", "0603"),
    ("Q1", 1, "AO3400A", "N-MOSFET, Logikpegel", "SOT-23"),
    ("R15", 1, "220 Ω", "Gate-Widerstand", "0603"),
    ("R16", 1, "100 kΩ", "Gate-Pull-down", "0603"),
    ("R1, R2", 2, "4,7 kΩ", "I²C-Pull-up (optional)", "0603"),
    ("R17", 1, "1 kΩ", "Serienwiderstand Taster", "0603"),
    ("C1", 1, "100 nF X7R 16 V", "Entkopplung U1", "0603"),
    ("C2", 1, "1 µF X7R 16 V", "Entkopplung U1", "0603"),
    ("C3", 1, "10 µF X5R 10 V", "Puffer +5V_LED", "0805"),
    ("C4", 1, "10 nF X7R 50 V", "Entprellung / ESD", "0603"),
    ("FB1", 1, "Ferrit 600 Ω @ 100 MHz, ≥ 500 mA", "Trennt LED-Strom von der Zuleitung", "0805"),
    ("SW1", 1, "Omron B3F-1000", "Einschalttaster 6×6 mm, 4,3 mm hoch", "THT"),
    ("J1", 1, "JST B7B-PH-K-S", "Stecker 7-pol., Platinenrückseite", "THT"),
    ("TP1, TP2", 2, "Testpunkt", "AS5600 OUT, PGO", "Pad Ø1 mm"),
    ("–", 1, "Magnet diametral Ø6 × 2,5 mm, N35", "in der Knopfnabe", "–"),
]
with open(os.path.join(OUT, "RD160_Knopfplatine_Stueckliste.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["Referenz", "Anzahl", "Bauteil", "Funktion", "Gehäuse"])
    w.writerows(bom)
print("ok")
