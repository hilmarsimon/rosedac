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
FLOOR = -H / 2 + f.BOT_LIP + f.BOT_T     # Oberseite Bodenblech
ZR = f.Z_REAR + f.RP_T                   # Innenseite Rückwand

# name, gruppe, x0, x1, z_vorn, z_hinten, höhe, rund   (Variante Acko + Ian Canada + Eigenbau, Stand 11/2026)
# Hinten: Platinen enden bei z = -262 (Buchsenkörper ragen bis -266, Querleisten bis -301).
PARTS = [
    # vorn
    ("Pi 5 + Kühler\n(Ports nach hinten)", "steuer", -200, -144, -28, -113, 30, False),
    ("Steuerplatine\nRP2040 + Standby\n(Eigenbau)", "steuer", -135, -45, -32, -98, 18, False),
    ("IC PurePi II\n3,3 V sauber\n(Superkond.)", "netz", -35, 65, -32, -100, 40, False),
    ("Pi-Netzteil\n5 V/5 A\n(Stahlhaube)", "netz", 72, 122, -30, -75, 28, False),
    ("T1 Digital\n25 VA", "netz", 125, 195, -35, -105, 38, True),
    ("T2 Analog\n30 VA", "netz", 115, 195, -110, -190, 40, True),
    ("±15 V linear\n(Acko)", "netz", 66, 110, -110, -188, 30, False),
    # hinten
    ("Eingangsplatine\nRelais-Mux, AES-Übertr.\n(Eigenbau)", "digital", -200, -125, -205, -262, 20, False),
    ("AckoDAC AKD49S\n(Maße ANFRAGEN,\nPlatzhalter 175×102)", "dac", -115, 60, -160, -262, 30, False),
    ("IC ReceiverPi DDC II\n+ FifoPi Q7 III\n(gestapelt)", "digital", 66, 151, -195, -262, 35, False),
    ("Netzfilter\nSanftanlauf\nRelais", "netz", 156, 200, -195, -262, 30, False),
]
COL = {"steuer": "#d9c8ef", "netz": "#f7d2b4", "dac": "#c4dbf2", "digital": "#cfe3f7"}
FRONT_FIX = [  # schon konstruiert: Displays, Taster-/Knopfplatine (nur Darstellung)
    ("2× Waveshare 5,5\" + Winkelstecker", f.DISP_X - f.DISP_GW, f.DISP_X + f.DISP_GW, 0, -15),
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


housing = {"Front": f.make_frame(), "Deckel": f.make_cover(), "Boden": f.make_bottom(), "Rückwand": f.make_rear_panel(), "Querleiste o": f.make_crossbar(True), "Querleiste u": f.make_crossbar(False),
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
asm.save(f"{OUT}/RD160_Platzplan.step")
for bk, bs in f.make_rear_connectors().items():      # Buchsenkörper hinter der Rückwand
    asm.add(bs, name="Buchse_" + bk, color=cq.Color(0.85, 0.7, 0.3))
    for name, g, x0, x1, z0, z1, h, rund in PARTS:
        v = solid(x0, x1, z0, z1, h, rund).intersect(bs).val().Volume()
        if v > 1e-3:
            hits.append((name.split("\n")[0], "Buchse " + bk, round(v, 1)))
for i in range(len(PARTS)):                          # Platzhalter untereinander
    for j in range(i + 1, len(PARTS)):
        v = solid(*PARTS[i][2:]).intersect(solid(*PARTS[j][2:])).val().Volume()
        if v > 1e-3:
            hits.append((PARTS[i][0].split("\n")[0], PARTS[j][0].split("\n")[0], round(v, 1)))
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
ax.text(0, f.Z_REAR - 4, "RÜCKWAND (Rückansicht gespiegelt): Netz + Breaker rechts | Kanal R | Trigger/SVC, AES, Coax 1/2, Opt, I²S, USB, LAN | Kanal L links", ha="center", va="bottom", fontsize=7.5)
for bk, bs in f.make_rear_connectors().items():
    bb = bs.val().BoundingBox()
    ax.add_patch(Rectangle((bb.xmin, bb.zmin), bb.xlen, bb.zlen, fc="#e8c766", ec="#8a6d1f", lw=0.4))
for qy in (True,):
    bb = f.make_crossbar(True).val().BoundingBox()
    ax.add_patch(Rectangle((bb.xmin, bb.zmin), bb.xlen, bb.zlen, fc="#b8bcc2", ec="#666", lw=0.4))
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
notes = ("Signalweg: Coax 1/2, AES (Übertrager) → Relais-Mux (Eingangsplatine) → ReceiverPi DDC II (+ Optical, I²S) → FifoPi Q7 III (Reclocking, MCLK) → "
         "AKD49S I²S-Direkteingang + ext. MCLK. PC AUDIO IN (USB-B) → USB-Eingang des AKD49S. Ausgänge AKD49S (XLR/Cinch-Option als Stiftleiste) → Einbaubuchsen.\n"
         "Steuerung: RP2040 ↔ Pi 5 (UART/JSON), RP2040 ↔ AKD49S-Controller (I²C/API: Eingang, Lautstärke AK4191, Filter), Relais, Trigger, Sanftanlauf.\n"
         "Gelb: Buchsenkörper hinter der Rückwand, grau: Querleiste. Acko-Maße fehlen (Platzhalter), IC-Maße teils ca. H = Platzhalterhöhe über Bodenblech, "
         f"Innenhöhe {H - f.COVER_T - f.BOT_LIP - f.BOT_T:.0f}.")
fig.text(0.04, 0.02, notes, fontsize=7.5, va="bottom")
ax.set_xlim(-W / 2 - 10, W / 2 + 30); ax.set_ylim(f.Z_REAR - 48, f.T + 20)
ax.set_title("RD160-Nachbau – Platzplan AckoDAC AKD49S + Ian Canada + Eigenbau, Draufsicht, Front unten, mm", fontsize=11, loc="left")
ax.invert_yaxis()
fig.savefig(f"{OUT}/RD160_Platzplan.png", dpi=150, bbox_inches="tight")
fig.savefig(f"{OUT}/RD160_Platzplan.pdf", bbox_inches="tight")
print("ok")
