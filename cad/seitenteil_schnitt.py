"""Verbindung Front <-> Seitenteil wie im Original-Detailfoto: waagerechte Lasche im Absatz der Profilwulst,
M3-Senkschraube senkrecht. (1) Längsschnitt durch die Schraubenachse, (2) Querschnitt in Schraubenebene."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import cadquery as cq
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
T, H, W = f.T, f.H, f.W
yt = H / 2
xs = W / 2 - f.TAB_SCREW_U
ST = {"Front": ("#c9ccd1", "///"), "Deckel": ("#9fb3c8", "\\\\"), "Boden": ("#9fb3c8", "\\\\"),
      "Seitenteil": ("#55585e", "\\\\\\"), "Schraube": ("#e0a030", None), "Plexiglas": ("#2b2b2e", None),
      "Schaum": ("#444", None)}
L = 60
P = [("Front", cq.Workplane("XY").add(f.make_bezel().val().fuse(f.make_carrier().val()))), ("Plexiglas", f.make_panel().translate((0, 0, f.CARRIER_T))),
     ("Deckel", f.make_cover_edge(L)), ("Seitenteil", f.make_side_stub(1, L)), ("Schraube", f.make_tab_screws()),
     ("Schaum", f.make_foam())]


def draw(a, sec, name):
    col, hat = ST[name]
    for face in sec.faces().vals():
        n = 3000
        pts = [(p.x, p.y) for p in face.outerWire().positions([i / n for i in range(n + 1)])]
        a.add_patch(Polygon(pts, closed=True, fc=col, ec="k", lw=0.7, hatch=hat))
        for inner in face.innerWires():
            ip = [(p.x, p.y) for p in inner.positions([i / 200 for i in range(201)])]
            a.add_patch(Polygon(ip, closed=True, fc="white", ec="k", lw=0.5))


fig, (a1, a2) = plt.subplots(1, 2, figsize=(16.5, 6.2), gridspec_kw={"width_ratios": [1.5, 1]})
lab = dict(fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.4))
# (1) Längsschnitt X = Schraubenachse: waagerecht -Z (Front links), senkrecht Y
for n, p in P:
    try:
        draw(a1, p.rotate((0, 0, 0), (0, 1, 0), -90).translate((0, 0, -xs)).section(0.0), n)
    except Exception:
        pass
z0, zs = f.FL_Z0, f.TAB_SCREW_Z
yT = yt - f.COVER_T
a1.annotate(f"Seitenwand der Front {f.END_W:.0f} breit, Tiefe {f.DEPTH:.0f}", (-(T - 5), yt - 15), (-(T + 6), yt + 9), **lab)
a1.annotate(f"Lasche {f.TAB_W:.0f} × {f.TAB_T:.0f} × {f.TAB_L:.0f} (waagerecht),\nan Seitenwand + Flansch angefräst",
            (-(z0 - 3), yT - 1.5), (-(z0 - 8), yt + 11), **lab)
a1.annotate(f"ISO 10642 M3×{f.SCREW_LEN} senkrecht,\n{T - zs:.0f} hinter Frontfläche, {f.TAB_SCREW_U} vom Außenrand",
            (-zs, yT - 4), (-(zs - 18), yT - 22), **lab)
a1.annotate(f"Seitenteil-Wulst {f.BEAD_W:.0f} × {f.BEAD_H:.0f}: vorn Absatz {f.TAB_T:.0f} tief\nfür die Lasche, M3-Gewinde 6 tief",
            (-(z0 - 25), yT - 6), (-(z0 - 32), yT - 15), **lab)
a1.annotate(f"Deckel {f.COVER_T:.0f} mm liegt auf Wulst und Lasche,\ndeckt die Schraube ab", (-(z0 - 40), yt - 2),
            (-(z0 - 40), yt + 9), **lab)
a1.set_aspect("equal"); a1.axis("off")
a1.set_xlim(-(T + 8), -(z0 - L + 2)); a1.set_ylim(yt - 26, yt + 15)
a1.set_title(f"① Längsschnitt durch die Laschenschraube (X = {xs:.1f}), Front links", fontsize=10, loc="left")
# (2) Querschnitt Z = Schraubenebene (Blick von vorn)
for n, p in P:
    try:
        draw(a2, p.section(zs), n)
    except Exception:
        pass
a2.annotate("Deckel eben über Wand und Wulst,\naußen bündig", (W / 2 - 3, yt - 2),
            (W / 2 + 3, yt + 8), **lab)
a2.annotate(f"Seitenteil C-Profil: Wand {f.SIDE_T:.0f}, außen {f.RIB_N} Rippen\n(Nut {f.RIB_GROOVE_W:.0f} breit, {f.RIB_DEPTH} tief, Grund R{f.RIB_GROOVE_W/2}),\nWulst innen {f.BEAD_W:.0f} × {f.BEAD_H:.0f}",
            (W / 2 - 3, yt - 20), (W / 2 + 3, yt - 22), **lab)
a2.annotate("Lasche im Absatz,\nSenkschraube", (xs, yT - 1.5), (W / 2 - 34, yt + 8), **lab)
a2.set_aspect("equal"); a2.axis("off")
a2.set_xlim(W / 2 - 36, W / 2 + 26); a2.set_ylim(yt - 26, yt + 15)
a2.set_title(f"② Querschnitt {T - zs:.0f} mm hinter der Front (Blick von vorn, rechte Seite)", fontsize=10, loc="left")
fig.suptitle("RD160-Nachbau – Verbindung Front ↔ Seitenteil (wie Original-Detailfoto), mm", fontsize=11, x=0.02, ha="left")
fig.savefig(os.path.join(OUT, "RD160_Seitenteil_Befestigung.png"), dpi=140, bbox_inches="tight")
fig.savefig(os.path.join(OUT, "RD160_Seitenteil_Befestigung.pdf"), bbox_inches="tight")
print("ok")
