"""Oberkante im Schnitt: (1) senkrecht bei X = 0 (Front, Auflage, Schaumstoff, Deckel),
(2) quer durch die rechte Seite hinter der Front (Seitenteil-L, Deckel-L, Lasche, Schraube)."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import cadquery as cq
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
T, H = f.T, f.H
yt = H / 2
ST = {"Front (Alu)": ("#c9ccd1", "///"), "Plexiglas": ("#2b2b2e", None), "Schaumstoff": ("#444", None),
      "Deckel": ("#9fb3c8", "\\\\"), "Seitenteil": ("#55585e", "\\\\\\"), "Schraube": ("#e0a030", None)}


def parts():
    return [("Front (Alu)", f.make_frame()), ("Plexiglas", f.make_panel().translate((0, 0, f.CARRIER_T))),
            ("Schaumstoff", f.make_foam()), ("Deckel", f.make_cover_edge(45)),
            ("Seitenteil", f.make_side_stub(1, 45)), ("Schraube", f.make_tab_screws())]


def draw(ax, wp, name):
    col, hat = ST[name]
    try:
        sec = wp
    except Exception:
        return
    for face in sec.faces().vals():
        n = 4000
        pts = [(p.x, p.y) for p in face.outerWire().positions([i / n for i in range(n + 1)])]
        ax.add_patch(Polygon(pts, closed=True, fc=col, ec="k", lw=0.7, hatch=hat))
        for inner in face.innerWires():
            ip = [(p.x, p.y) for p in inner.positions([i / 100 for i in range(101)])]
            ax.add_patch(Polygon(ip, closed=True, fc="white", ec="k", lw=0.5))


fig, (a1, a2) = plt.subplots(1, 2, figsize=(16.5, 5.2), gridspec_kw={"width_ratios": [1.25, 1]})
lab = dict(fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.4))

# (1) Schnitt X = 0: Achse waagerecht = -Z (Front links), senkrecht = Y
for name, wp in parts():
    try:
        s = wp.rotate((0, 0, 0), (0, 1, 0), -90).section(0.0)       # X -> Z, Schnitt X = 0
    except Exception:
        continue
    draw(a1, s, name)
zb, z0 = T - f.BAND, f.FL_Z0
a1.annotate(f"Band {f.BAND:.0f}, volle Höhe", (-(T - 4), yt), (-(T + 14), yt + 6), **lab)
a1.annotate(f"Auflage {f.SEAT_L:.0f} tief, {f.SEAT_D} unter Oberkante\nmit Schaumstoff", (-(zb - 6), yt - f.SEAT_D - 1),
            (-(z0 - 6), yt - 18), **lab)
a1.annotate(f"Schaumstoff {f.FOAM_T:.0f} → {f.FOAM_C} mm", (-(zb - 3), yt - f.SEAT_D + 0.8), (-(z0 - 6), yt + 10), **lab)
a1.annotate(f"Deckel {f.COVER_T:.0f} mm, oben bündig,\nvorn bis ans Band (0,3 Luft)", (-(z0 - 15), yt - 2.5),
            (-(z0 - 15), yt + 4), **lab)
a1.annotate(f"Nut {f.GROOVE_H} × {f.GROOVE_D:.0f} tief in der Bandrückseite,\nSteg darüber {f.GROOVE_TOP:.0f} mm (Scheibenfräser)", (-(zb + 2), yt - f.GROOVE_TOP - 0.3),
            (-(T + 14), yt + 10), **lab)
a1.annotate(f"Feder einseitig {f.TONGUE_T:.0f} × {f.TONGUE_L}, oben um {f.GROOVE_TOP:.0f} abgesetzt:\nSchaum drückt sie oben an den Steg → Deckel vorn gehalten",
            (-(zb + 1), yt - f.COVER_T + 0.8), (-(z0 - 6), yt - 27), **lab)
a1.annotate("Plexiglas 3 mm", (-(T - 1.5), yt - 15), (-(T + 14), yt - 25), **lab)
a1.set_aspect("equal"); a1.axis("off")
a1.set_xlim(-(T + 16), -(z0 - 42)); a1.set_ylim(yt - 32, yt + 16)
a1.set_title("① Oberkante, Schnitt bei X = 0 (Front links)", fontsize=10, loc="left")

# (2) Querschnitt Z = Laschenschraube: Achse waagerecht = X, senkrecht = Y (Blick von vorn, rechte Seite)
zc = f.TAB_SCREW_Z
for name, wp in parts():
    try:
        s = wp.section(zc)
    except Exception:
        continue
    draw(a2, s, name)
xo = f.W / 2
a2.annotate(f"Seitenteil C-Profil: Wand {f.SIDE_T:.0f}, außen {f.RIB_N} Rippen,\nWulst {f.BEAD_W:.0f} × {f.BEAD_H:.0f}",
            (xo - 3, yt - 20), (xo + 4, yt - 24), **lab)
a2.annotate("Deckel eben, liegt auf Wand und Wulst,\naußen bündig", (xo - 3, yt - 2), (xo + 4, yt + 6), **lab)
a2.annotate(f"Lasche {f.TAB_W:.0f} × {f.TAB_T:.0f} im Absatz der Wulst,\nISO 10642 M3×{f.SCREW_LEN} senkrecht", (xo - f.TAB_SCREW_U, yt - f.COVER_T - 2),
            (xo - 44, yt + 6), **lab)
a2.set_aspect("equal"); a2.axis("off")
a2.set_xlim(xo - 46, xo + 30); a2.set_ylim(yt - 30, yt + 14)
a2.set_title(f"② Querschnitt rechte Seite, {T - zc:.0f} mm hinter der Frontfläche (Blick von vorn)", fontsize=10, loc="left")
fig.suptitle("RD160-Nachbau – Oberkante: Nut im Band + Deckelfeder; Seitenteil-C-Profil, ebener Deckel (mm)", fontsize=11, x=0.02, ha="left")
fig.savefig(os.path.join(OUT, "RD160_Oberkante_Schnitt.png"), dpi=140, bbox_inches="tight")
fig.savefig(os.path.join(OUT, "RD160_Oberkante_Schnitt.pdf"), bbox_inches="tight")
print("ok")
