"""Rückwand: STEP, DXF (Ausschnitte + Gravur), Fertigungszeichnung, Optikvorschau, Stückliste CSV.
Alle Maße/Positionen aus frontplatte.py (RP_CONN). Zeichnung in Rückansicht (Blick auf die Rückwand), Ursprung Wandmitte."""
import os, csv, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Polygon
import cadquery as cq
import ezdxf
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
rp = f.make_rear_panel()
assert rp.val().isValid()
cq.exporters.export(rp, f"{OUT}/RD160_Rueckwand.step")
cq.exporters.export(f.make_crossbar(True), f"{OUT}/RD160_Querleiste_oben.step")
cq.exporters.export(f.make_crossbar(False), f"{OUT}/RD160_Querleiste_unten.step")

PW = f.W - 2 * f.SIDE_T - 0.2                     # Wandbreite
yT, yB = f.H / 2 - f.COVER_T, -f.H / 2 + f.BOT_T   # Ober-/Unterkante Wand
SCR = f.rear_screw_points()                       # (v, y) Rückansicht


# ---------------- DXF (Laserschnitt/Fräsen + Gravur) ----------------
doc = ezdxf.new("R2010"); doc.units = ezdxf.units.MM
for ly, col in (("KONTUR", 7), ("BOHRUNG", 1), ("SENKUNG", 3), ("GRAVUR", 5)):
    doc.layers.add(ly, color=col)
m = doc.modelspace()
m.add_lwpolyline([(-PW / 2, yB), (PW / 2, yB), (PW / 2, yT), (-PW / 2, yT)], close=True, dxfattribs={"layer": "KONTUR"})
for v, y in SCR:
    m.add_circle((v, y), 1.7, dxfattribs={"layer": "BOHRUNG"})
    m.add_circle((v, y), 3.3, dxfattribs={"layer": "SENKUNG"})
for c in f.RP_CONN:
    for h in f.rp_holes(c):
        if h[0] == "kreis":
            m.add_circle((h[1], h[2]), h[3] / 2, dxfattribs={"layer": "BOHRUNG"})
        elif h[0] == "rechteck":
            v, y, b, hh = h[1:]
            m.add_lwpolyline([(v - b / 2, y - hh / 2), (v + b / 2, y - hh / 2), (v + b / 2, y + hh / 2), (v - b / 2, y + hh / 2)],
                             close=True, dxfattribs={"layer": "BOHRUNG"})
        elif h[0] == "dflat":
            v, y, d, fl = h[1:]
            r = d / 2; yf = fl - r                         # Fläche oben
            a = math.degrees(math.asin(yf / r))
            m.add_arc((v, y), r, start_angle=180 - a, end_angle=360 + a, dxfattribs={"layer": "BOHRUNG"})
            xf = math.sqrt(r * r - yf * yf)
            m.add_line((v - xf, y + yf), (v + xf, y + yf), dxfattribs={"layer": "BOHRUNG"})
for v0, v1, y0, y1 in f.RP_FRAMES:
    m.add_lwpolyline([(v0, y0), (v1, y0), (v1, y1), (v0, y1)], close=True, dxfattribs={"layer": "GRAVUR"})
for p0, p1 in f.RP_LINES:
    m.add_line(p0, p1, dxfattribs={"layer": "GRAVUR"})
for txt, v, y, hh, rot in f.RP_TEXTS:
    m.add_text(txt, height=hh, rotation=rot, dxfattribs={"layer": "GRAVUR", "style": "Standard"}).set_placement(
        (v, y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
doc.saveas(f"{OUT}/RD160_Rueckwand.dxf")

# ---------------- Stückliste ----------------
with open(f"{OUT}/RD160_Rueckwand_Buchsen.csv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["Pos", "Gravur", "Bauteil", "v [mm]", "y [mm]", "Ausschnitt", "Tiefe innen [mm]"])
    for i, c in enumerate(f.RP_CONN, 1):
        m5, t = c[5], c[2]
        cut = (f"Ø{m5[0]}" if t == "rund" else f"Ø{m5[0]} / Fläche {m5[1]}" if t == "dflat" else
               "Ø24 + 2× M3 diagonal 19×24" if t == "neutrik_d" else
               f"{m5[0]}×{m5[1]} + 2× Ø3,2 Abst. {m5[2]:.0f}" if t == "iec" else
               f"{m5[0]}×{m5[1]}" + (f" + {len(m5[2])}× M3" if m5[2] else ""))
        w.writerow([i, c[1], c[7], c[3], c[4], cut, c[6][2]])


# ---------------- Zeichnung ----------------
def draw(ax, optik):
    ax.set_aspect("equal"); ax.axis("off")
    bg, fg, hole = ("#1c1d1f", "#e8e8e8", "#000000") if optik else ("white", "k", "white")
    ax.add_patch(Rectangle((-f.W / 2, -f.H / 2), f.W, f.H, fc="#2a2b2e" if optik else "#eeeeee", ec=fg, lw=0.6))  # Gehäuse
    ax.add_patch(Rectangle((-PW / 2, yB), PW, yT - yB, fc=bg, ec=fg, lw=0.9))
    for v, y in SCR:
        ax.add_patch(Circle((v, y), 3.0, fc="#0c0c0c" if optik else "white", ec="#666" if optik else fg, lw=0.6))
        ax.add_patch(Circle((v, y), 1.0, fc="#333" if optik else "white", ec=fg if not optik else "none", lw=0.3))
    gc = "#d8d8d8" if optik else "#3a6fb0"            # Gravur
    for v0, v1, y0, y1 in f.RP_FRAMES:
        ax.add_patch(FancyBboxPatch((v0, y0), v1 - v0, y1 - y0, boxstyle="round,pad=0,rounding_size=1.2", fc="none", ec=gc, lw=0.5))
    for p0, p1 in f.RP_LINES:
        ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=gc, lw=0.5)
    for txt, v, y, hh, rot in f.RP_TEXTS:
        ax.text(v, y, txt, ha="center", va="center", rotation=rot, fontsize=hh * 2.05, color=gc,
                fontweight="bold" if hh >= 2.2 else "normal", family="DejaVu Sans")
    for c in f.RP_CONN:
        key, txt, typ, v, y = c[:5]
        if optik:                                    # grobe Darstellung der Einbaubuchsen
            if typ == "neutrik_d":
                ax.add_patch(FancyBboxPatch((v - 12.5, y - 15), 25, 30, boxstyle="round,pad=0,rounding_size=4",
                                            fc="#3b3c3f", ec="#777", lw=0.5))
                for du, dy in (f.D_SCR, (-f.D_SCR[0], -f.D_SCR[1])):
                    ax.add_patch(Circle((v + du, y + dy), 1.4, fc="#999", ec="none"))
                ax.add_patch(Circle((v, y), 10.5, fc="#111", ec="#888", lw=0.6))
            elif typ == "iec":
                ax.add_patch(FancyBboxPatch((v - 25, y - 12), 50, 24, boxstyle="round,pad=0,rounding_size=3", fc="#111", ec="#666", lw=0.5))
                ax.add_patch(Polygon([(v - 12, y - 8), (v + 12, y - 8), (v + 12, y + 4), (v + 8, y + 8), (v - 8, y + 8), (v - 12, y + 4)],
                                     fc="#050505", ec="#444", lw=0.5))
            elif typ == "rect":
                b, hh, scr = c[5]
                ax.add_patch(Rectangle((v - b / 2 - 0.8, y - hh / 2 - 0.8), b + 1.6, hh + 1.6, fc="#3a3b3e", ec="#777", lw=0.4))
                ax.add_patch(Rectangle((v - b / 2 + 1, y - hh / 2 + 1), b - 2, hh - 2, fc="#050505", ec="#555", lw=0.4))
                for dv, dy in scr:
                    ax.add_patch(Circle((v + dv, y + dy), 1.5, fc="#222", ec="#888", lw=0.4))
            elif typ == "dflat":
                ax.add_patch(Circle((v, y), 7.5, fc="#2d2d2d", ec="#999", lw=0.5))
                ax.add_patch(Circle((v, y), 3.5, fc="#bbb", ec="#666", lw=0.5))
            else:
                d = c[5][0]
                gold = key.startswith(("RCA", "COX1"))
                ax.add_patch(Circle((v, y), d / 2 + 2.5, fc="#c8a24a" if gold else "#9a9a9a", ec="#555", lw=0.4))
                ax.add_patch(Circle((v, y), d / 2 - 1.5, fc="#111", ec="none"))
                ax.add_patch(Circle((v, y), 1.0, fc="#d9b75c" if gold else "#bbb", ec="none"))
        else:
            for h in f.rp_holes(c):
                if h[0] == "kreis":
                    ax.add_patch(Circle((h[1], h[2]), h[3] / 2, fc="white", ec="k", lw=0.6))
                elif h[0] == "rechteck":
                    ax.add_patch(Rectangle((h[1] - h[3] / 2, h[2] - h[4] / 2), h[3], h[4], fc="white", ec="k", lw=0.6))
                else:
                    import numpy as np
                    v0, y0, d, fl = h[1:]
                    t = np.linspace(0, 2 * np.pi, 120); xs, ys = v0 + d / 2 * np.cos(t), y0 + np.minimum(d / 2 * np.sin(t), fl - d / 2)
                    ax.fill(xs, ys, fc="white", ec="k", lw=0.6)
            ax.plot([v - 2, v + 2], [y, y], "k", lw=0.3); ax.plot([v, v], [y - 2, y + 2], "k", lw=0.3)
    ax.set_xlim(-f.W / 2 - 8, f.W / 2 + 8); ax.set_ylim(-f.H / 2 - (30 if not optik else 6), f.H / 2 + 6)


fig = plt.figure(figsize=(16.5, 11.7))
a1 = fig.add_axes([0.03, 0.60, 0.94, 0.34]); draw(a1, False)
a1.set_title("RD160-Nachbau – Rückwand 4 mm Alu (Rückansicht, Maße mm, Ursprung Wandmitte)", loc="left", fontsize=12)
# Bemaßung: v-Positionen (Kettenmaß von Wandmitte) unten, y-Reihen rechts
vs = sorted({c[3] for c in f.RP_CONN})
for v in vs:
    a1.plot([v, v], [yB - 1, -f.H / 2 - 9], color="#888", lw=0.3)
    a1.text(v, -f.H / 2 - 11, f"{v:+.0f}", rotation=90, ha="center", va="top", fontsize=6)
a1.text(f.W / 2 + 4, 0, "y-Maße:\nStückliste", fontsize=6, va="center")
a1.text(-PW / 2, -f.H / 2 - 27, f"Wand {PW:.1f} × {yT - yB:.0f} × {f.RP_T:.0f}. 10× Senkung 90° M3 (ISO 10642): oben/unten bei v ±{f.RP_SCR_X[0]}/±{f.RP_SCR_X[1]:.0f} "
        f"in die Querleisten 10×10, seitlich v ±{f.W / 2 - f.REAR_SCREW_U:.1f} | y {f.RP_SIDE_Y:+.0f} in den Seitenteil-Block. "
        f"Neutrik D: Ø24 + 2× M3 Gewinde diagonal (−9,5|+12)/(+9,5|−12). Gravur (blau) Laser nach Eloxal, Positionen nach Originalfoto.", fontsize=7)
a2 = fig.add_axes([0.03, 0.30, 0.94, 0.28]); draw(a2, True)
a2.set_title("Optik (schwarz eloxiert, Gravur hell) – Einbaubuchsen schematisch", loc="left", fontsize=10)
a3 = fig.add_axes([0.03, 0.02, 0.94, 0.26]); a3.axis("off")
rows = [[str(i), c[1], c[7], f"{c[3]:+.0f}", f"{c[4]:+.0f}", str(c[6][2])] for i, c in enumerate(f.RP_CONN, 1)]
tb = a3.table(cellText=rows, colLabels=["Pos", "Gravur", "Bauteil", "v", "y", "Tiefe innen"], loc="upper left",
              colWidths=[0.03, 0.08, 0.5, 0.04, 0.04, 0.07], cellLoc="left")
tb.auto_set_font_size(False); tb.set_fontsize(6.5); tb.scale(1, 0.95)
a3.text(0.80, 0.95, "Abweichungen vom Original:\n• SFP-Platz → LAN (RJ45 zum Pi 5)\n• SVC → USB-C zum RP2040\n• EXT. CLOCK entfällt (FifoPi Q7\n"
        "   ohne 10-MHz-Referenz), Schalter\n   EXT_CLOCK\n• Logo/Typenschild: eigene Gravur\n\nCOAX 2 (BNC) und AES/EBU: Relais-\nUmschaltung auf den Coax-Eingang\n"
        "der ReceiverPi DDC II (AES über\nÜbertrager 110 → 75 Ω), Steuerung\nRP2040.\n\nAusschnitte Cinch/BNC/Klinke/Toslink/\n"
        "IEC vor Fertigung gegen Datenblatt\nder bestellten Teile prüfen.",
        transform=a3.transAxes, fontsize=7.5, va="top")
fig.savefig(f"{OUT}/RD160_Rueckwand.png", dpi=150)
fig.savefig(f"{OUT}/RD160_Rueckwand.pdf")
print("Rückwand: gültig", rp.val().isValid(), "| Buchsen", len(f.RP_CONN))
