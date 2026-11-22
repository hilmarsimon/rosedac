"""Schnitt durch die Drehknopf-Baugruppe (Y=0), Maße aus frontplatte.py. Vertikal = radial, horizontal = Z (Front rechts)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "RD160_Drehknopf_Schnitt.pdf")
fig, ax = plt.subplots(figsize=(11.69, 8.27))
ax.set_aspect("equal"); ax.axis("off")


def ring(r0, r1, z0, z1, fc, hatch=None, ec="k"):
    for s in (1, -1):
        y0, y1 = sorted((s * r0, s * r1))
        ax.add_patch(Rectangle((z0, y0), z1 - z0, y1 - y0, fc=fc, ec=ec, lw=0.6, hatch=hatch))


def poly(pts, fc, hatch=None):
    for s in (1, -1):
        ax.add_patch(Polygon([(z, s * r) for z, r in pts], fc=fc, ec="k", lw=0.6, hatch=hatch))


AL, BLK, ST, PM, PCB, LUX = "#c9ccd1", "#3b3b3e", "#9aa0a8", "#2b2b2e", "#3a7d44", "#fff6b0"
T, CT = f.T, f.CARRIER_T
W = 44
# Rahmen/Träger
ring(f.LIGHT_OD / 2, W, 0, CT, AL, "///")
ring(f.RING_OD / 2, f.LIGHT_OD / 2, f.LIGHT_DEPTH, CT, AL, "///")
ring(f.BEARING_D / 2, f.RING_ID / 2, 0, CT, AL, "///")                          # Insel (hinten mit Stegen)
ring(f.SHAFT_HOLE_D / 2, f.BEARING_D / 2, f.BEARING_DEPTH, CT, AL, "///")       # Lagerschulter
ring(f.SHAFT_PANEL_D / 2, W, CT, T, PM)
# Lager 6805
ring(f.BRG_ID / 2, f.BRG_OD / 2, 0, f.BRG_W, ST, "xx")
# Knopf
z0, z1, ft = f.KNOB_Z0, f.KNOB_Z1, f.FLOOR_TOP
ring(f.SHELL_ID / 2, f.KNOB_D / 2, z0, z1, BLK, "\\\\")
ring(f.MAGNET_D / 2, f.SHELL_ID / 2, z0, ft, BLK, "\\\\")
ax.add_patch(Rectangle((f.HUB_Z0 + f.MAGNET_H, -f.MAGNET_D / 2), ft - f.HUB_Z0 - f.MAGNET_H, f.MAGNET_D, fc=BLK, ec="k", lw=0.6, hatch="\\\\"))
ring(f.MAGNET_D / 2, f.COLLAR_D / 2, f.BRG_W, z0, BLK, "\\\\")
ring(f.MAGNET_D / 2, f.BRG_ID / 2, f.HUB_Z0, f.BRG_W, BLK, "\\\\")
ring(f.ORING_GROOVE_D / 2, f.SHAFT_HOLE_D / 2, f.BRG_W + 0.6, f.BRG_W + 0.6 + f.ORING_GROOVE_W, "#222")
ring(f.WIN_PCD / 2 - f.WIN_D / 2, f.WIN_PCD / 2 + f.WIN_D / 2, z0, ft, LUX)
ring(f.TUBE_ID / 2, f.TUBE_OD / 2, ft, z1, "#e9f3ff", "....")
ring(f.TUBE_ID / 2, f.TUBE_OD / 2, z1 - 0.6, z1, LUX)
poly([(ft, f.CONE_FLOOR_D / 2), (ft, f.INS_OD / 2), (z1, f.INS_OD / 2), (z1, f.CONE_LIP_ID / 2)], AL, "\\\\")
# Haltescheibe, Magnet
ring(f.MAGNET_D / 2 + 1.5, f.WASHER_D / 2, f.HUB_Z0 - f.WASHER_T, f.HUB_Z0, "#8d9096")
ax.add_patch(Rectangle((f.HUB_Z0, -3), f.MAGNET_H, 6, fc="#b33", ec="k", lw=0.6))
# Knopfplatine: AS5600 Mitte + LEDs
ring(0, W, f.PCB_Z - 1.6, f.PCB_Z, PCB)
ax.add_patch(Rectangle((f.PCB_Z, -2.5), 1.5, 5, fc="#222", ec="k", lw=0.6))
ring(f.WIN_PCD / 2 - 1.5, f.WIN_PCD / 2 + 1.5, f.PCB_Z, f.PCB_Z + 0.8, LUX)
# Lichtweg
for s in (1, -1):
    r = s * f.WIN_PCD / 2
    ax.annotate("", (f.KNOB_Z1 + 3, r), (f.PCB_Z + 1, r), arrowprops=dict(arrowstyle="->", color="#e0a800", lw=1.2, ls="--"))

ax.set_xlim(-25, f.KNOB_Z1 + 75); ax.set_ylim(-W - 14, W + 28)
lab = dict(fontsize=7.5, arrowprops=dict(arrowstyle="-", lw=0.4))
X = f.KNOB_Z1 + 8
ax.annotate(f"Becher Alu Ø{f.KNOB_D:.0f} mit Nabe (ein Drehteil), ragt {f.KNOB_PROT:.0f} mm vor,\nschwarz eloxiert; Boden bündig in Ø{f.SHAFT_PANEL_D:.0f}-Bohrung, 12 Lichtfenster",
            (f.KNOB_Z1 - 4, f.KNOB_D / 2), (X, 40), **lab)
ax.annotate(f"Lichtleiter PMMA klar Ø{f.TUBE_OD:.0f}/{f.TUBE_ID}, Vorderkante mattiert", (f.KNOB_Z1 - 0.3, f.WIN_PCD / 2), (X, 28), **lab)
ax.annotate(f"Konuseinsatz Alu Ø{f.CONE_LIP_ID:.0f} → Ø{f.CONE_FLOOR_D:.0f}, eingeklebt", (f.KNOB_Z1 - 10, 17), (X, 16), **lab)
ax.annotate("Mittelscheibe = Becherboden, bündig mit Front", (ft - 0.5, 4), (X, 4), **lab)
ax.annotate(f"Dünnringlager 6805-2RS ({f.BRG_ID:.0f}×{f.BRG_OD:.0f}×{f.BRG_W:.0f}) im Träger, Ø{f.BEARING_D:.0f} H7", (3.5, -f.BRG_OD / 2 + 1), (X, -12), **lab)
ax.annotate("O-Ring 26×2 + Nyogel 767A in Bohrung Ø30 = Dämpfung", (f.BRG_W + 1.6, -f.SHAFT_HOLE_D / 2 + 0.5), (X, -22), **lab)
ax.annotate(f"Haltescheibe Ø{f.WASHER_D:.0f}×{f.WASHER_T}, 3× ISO 7380 M2,5 – klemmt Innenring", (f.HUB_Z0 - 0.8, -12), (-22, -58), **lab)
ax.annotate("Knopfplatine (wie RD160): AS5600 mittig, 12 LEDs auf Ø43,\n4-mm-Bolzen an Pos. C, Kabel zum Controller", (f.PCB_Z - 0.8, 30), (-24, 66), **lab)
ax.annotate("Diametralmagnet 6×2,5 in Nabe, Spalt 2,5 mm", (f.HUB_Z0 + 1, 2), (-24, 48), **lab)
ax.annotate(f"Lichtkanal Ø{f.RING_ID:.0f}/{f.RING_OD:.0f}", (CT - 2, f.RING_OD / 2 - 1), (CT + 22, 56), **lab)
ax.plot([f.T, f.T], [-W, W], lw=0.5, ls="-.", color="#c00")
ax.annotate(f"Frontebene", (f.T, -W), (f.T + 4, -W - 10), **lab)
ax.set_title("Drehknopf RD160-Stil – Schnitt durch die Achse (Front rechts, gelb gestrichelt = Lichtweg)", fontsize=10, loc="left")
fig.savefig(OUT); fig.savefig(OUT.replace(".pdf", ".png"), dpi=130)
print("ok")
