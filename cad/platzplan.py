"""Platzplan Innenraum (Draufsicht, Front unten): Platzhalter-Volumen der Baugruppen, Kollisionsprüfung gegen das
Gehäuse, STEP + Zeichnung. Maße mm, Koordinaten wie frontplatte.py (X quer, Y hoch, Z: Front = T, hinten negativ)."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import cadquery as cq
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
W, H = f.W, f.H
FLOOR = -H / 2 + f.BOT_T                 # Oberseite Bodenblech
ZR = f.Z_REAR + f.RP_T                   # Innenseite Rückwand

# name, gruppe, x0, x1, z_vorn, z_hinten, höhe, rund
PARTS = [
    ("Pi 5 + Kühlkörper\n(Ports nach hinten)", "steuer", -200, -144, -28, -113, 30, False),
    ("RP2040-Steuerung\n+ Standby-NT 5 V", "steuer", -132, -42, -32, -98, 18, False),
    ("Netzteil Digital\n3,3 / 5 V (T1)", "netz", -30, 82, -32, -108, 32, False),
    ("Pi-Netzteil 5 V/5 A\n(Stahlhaube)", "netz", 94, 168, -30, -72, 28, False),
    ("Sanftanlauf\n+ Trafo-Relais", "netz", 94, 158, -80, -112, 22, False),
    ("T2 Analog L\n25 VA", "netz", -155, -85, -120, -190, 38, True),
    ("T1 Digital\n25 VA", "netz", -35, 35, -120, -190, 38, True),
    ("T3 Analog R\n25 VA", "netz", 85, 155, -120, -190, 38, True),
    ("Kanal L: Netzteil L (unten)\nDAC L + I/V + MUSES (oben)", "dac", -200, -76, -222, ZR + 2, 62, False),
    ("Eingänge: XMOS, AK4118,\nHDMI-I²S, CPLD (unten)\nFIFO + Femto-Takt (oben)", "digital", -66, 66, -222, ZR + 2, 50, False),
    ("Kanal R: Netzteil R (unten)\nDAC R + I/V + MUSES (oben)", "dac", 76, 200, -222, ZR + 2, 62, False),
]
COL = {"steuer": "#d9c8ef", "netz": "#f7d2b4", "dac": "#c4dbf2", "digital": "#cfe3f7"}
FRONT_FIX = [  # schon konstruiert: Displays, Taster-/Knopfplatine (nur Darstellung)
    ("2× AMOLED 5,5\" hinter dem Träger", -125, 125, 0, -20),
    ("Taster-PCB", -205, -140, 0, -12),
    ("Knopf-PCB", 130, 203, -4, -22),
]


def solid(x0, x1, z0, z1, h, rund):
    if rund:
        d = x1 - x0
        return cq.Workplane("XZ").workplane(offset=-FLOOR - 0.5).center((x0 + x1) / 2, (z0 + z1) / 2) \
            .circle(d / 2).extrude(-h) if False else \
            cq.Workplane("XY").add(cq.Solid.makeCylinder(d / 2, h, cq.Vector((x0 + x1) / 2, FLOOR + 0.5, (z0 + z1) / 2),
                                                          cq.Vector(0, 1, 0)))
    return (cq.Workplane("XY").box(x1 - x0, h, z0 - z1, centered=False).translate((x0, FLOOR + 0.5, z1)))


housing = {"Front": f.make_frame(), "Deckel": f.make_cover(), "Boden": f.make_bottom(), "Rückwand": f.make_rear_panel(),
           "Seite R": f.make_side_panel(1), "Seite L": f.make_side_panel(-1)}
asm = cq.Assembly()
hits = []
for name, g, x0, x1, z0, z1, h, rund in PARTS:
    s = solid(x0, x1, z0, z1, h, rund)
    nm = name.split("\n")[0]
    asm.add(s, name="PH_" + "".join(c for c in nm if c.isalnum()), color=cq.Color(COL[g]))
    for hn, hp in housing.items():
        v = s.intersect(hp).val().Volume()
        if v > 1e-3:
            hits.append((nm, hn, round(v, 1)))
for hn, hp in housing.items():
    asm.add(hp, name=hn.replace(" ", "_").replace("ü", "ue"), color=cq.Color(0.6, 0.6, 0.62, 0.4))
asm.save(f"{OUT}/RD160_Platzplan_Platzhalter.step")
for bk, bs in f.make_rear_connectors().items():      # Buchsenkörper hinter der Rückwand
    asm.add(bs, name="Buchse_" + bk, color=cq.Color(0.85, 0.7, 0.3))
    for name, g, x0, x1, z0, z1, h, rund in PARTS:
        v = solid(x0, x1, z0, z1, h, rund).intersect(bs).val().Volume()
        if v > 1e-3:
            hits.append((name.split("\n")[0], "Buchse " + bk, round(v, 1)))
print("Kollisionen:", hits or "keine")

# ---------------- Zeichnung (Draufsicht, Front unten) ----------------
fig, ax = plt.subplots(figsize=(11.7, 9.0)); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Rectangle((-W / 2, f.Z_REAR), W, f.T - f.Z_REAR, fc="none", ec="k", lw=1.2))
for sx in (1, -1):   # Seitenteile mit Wulst
    ax.add_patch(Rectangle((sx * W / 2 - (f.SIDE_W if sx > 0 else 0), f.Z_REAR), f.SIDE_W, f.FL_Z0 - f.Z_REAR,
                           fc="#55585e", ec="k", lw=0.5, alpha=0.35))
ax.add_patch(Rectangle((-W / 2, f.FL_Z0), W, f.T - f.FL_Z0, fc="#c9ccd1", ec="k", lw=0.6))
ax.add_patch(Rectangle((-W / 2 + f.SIDE_T, f.Z_REAR), W - 2 * f.SIDE_T, f.RP_T, fc="#2b2b2e", ec="k", lw=0.5))
ax.text(0, f.T + 4, "FRONT", ha="center", va="top", fontsize=10)
ax.text(0, f.Z_REAR - 4, "RÜCKWAND: L-Ausgänge XLR+Cinch | USB-B, 2× Koax, Opt, AES, HDMI-I²S, RJ45 (Pi), Kaltgeräte+Sicherung"
        " | R-Ausgänge", ha="center", va="bottom", fontsize=7.5)
for nm, x0, x1, z0, z1 in FRONT_FIX:
    ax.add_patch(Rectangle((x0, z1), x1 - x0, z0 - z1, fc="#eeeeee", ec="#888", lw=0.5, hatch="///"))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, nm, ha="center", va="center", fontsize=6.5, color="#444")
for name, g, x0, x1, z0, z1, h, rund in PARTS:
    if rund:
        ax.add_patch(Circle(((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0) / 2, fc=COL[g], ec="k", lw=0.7))
    else:
        ax.add_patch(Rectangle((x0, z1), x1 - x0, z0 - z1, fc=COL[g], ec="k", lw=0.7))
    ax.text((x0 + x1) / 2, (z0 + z1) / 2, f"{name}\nH {h}", ha="center", va="center", fontsize=6.8)
# Maße
ax.annotate("", (-W / 2, f.Z_REAR - 30), (W / 2, f.Z_REAR - 30), arrowprops=dict(arrowstyle="<->", lw=0.6))
ax.text(0, f.Z_REAR - 32, f"{W:.0f}", ha="center", va="bottom", fontsize=8)
ax.annotate("", (W / 2 + 14, f.T), (W / 2 + 14, f.Z_REAR), arrowprops=dict(arrowstyle="<->", lw=0.6))
ax.text(W / 2 + 17, (f.T + f.Z_REAR) / 2, f"{f.T - f.Z_REAR:.0f}", rotation=90, va="center", fontsize=8)
inner_h = H - f.COVER_T - f.BOT_T
notes = (f"Innenhöhe {inner_h:.0f} mm (unter der Wulst an den Seiten {inner_h - 2 * f.BEAD_H:.0f} mm); nutzbare Breite zwischen den Wulsten "
         f"{W - 2 * f.SIDE_W:.0f} mm, Tiefe Front–Rückwand {f.FL_Z0 - ZR:.0f} mm.\n"
         "Zonen: vorn Steuerung/Pi/Digital-NT (kurze HDMI-Wege zu den Displays) · Mitte 3 Ringkerne in Reihe wie Original · "
         "hinten Dual-Mono: L links, Eingänge Mitte, R rechts, direkt an den Buchsen.\n"
         "Ringkerne Ø70 (25 VA) mit ≥ 30 mm Abstand zu den DAC-Modulen, Wicklungsaustritt quer; Pi 5 passiv über Wärmeleitpad an den Boden "
         "(Kühlkörper-Blech). H = Platzhalterhöhe über Bodenblech.")
fig.text(0.04, 0.02, notes, fontsize=7.5, va="bottom")
ax.set_xlim(-W / 2 - 10, W / 2 + 30); ax.set_ylim(f.Z_REAR - 48, f.T + 20)
ax.set_title("RD160-Nachbau – Platzplan Innenraum (Draufsicht, Front unten, Maße mm)", fontsize=11, loc="left")
ax.invert_yaxis()
fig.savefig(f"{OUT}/RD160_Platzplan.png", dpi=150, bbox_inches="tight")
fig.savefig(f"{OUT}/RD160_Platzplan.pdf", bbox_inches="tight")
print("ok")
