"""Deckel komplett: STEP, Eckklotz hinten, Gehäuse-Baugruppe (Vorschau), Zeichnung mit Draufsicht + Schnitten."""
import os, math, subprocess
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle
import cadquery as cq
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
cover = f.make_cover()
cq.exporters.export(cover, f"{OUT}/RD160_Deckel.step")
cq.exporters.export(f.make_bottom(), f"{OUT}/RD160_Bodenplatte.step")
cq.exporters.export(f.make_side_panel(1), f"{OUT}/RD160_Seitenteil_rechts.step")
cq.exporters.export(f.make_side_panel(-1), f"{OUT}/RD160_Seitenteil_links.step")

side_len = f.FL_Z0 - f.Z_REAR
asm = (cq.Assembly()
       .add(f.make_frame(), name="Front_Rahmen", color=cq.Color(0.16, 0.16, 0.17))
       .add(f.make_panel(), name="Plexiglas", loc=cq.Location((0, 0, f.CARRIER_T)), color=cq.Color(0.05, 0.05, 0.05))
       .add(cover, name="Deckel", color=cq.Color(0.75, 0.76, 0.78))
       .add(f.make_foam(), name="Schaumstoff", color=cq.Color(0.08, 0.08, 0.08))
       .add(f.make_rear_panel(), name="Rueckwand", color=cq.Color(0.12, 0.12, 0.13))
       .add(f.make_crossbar(True), name="Querleiste_oben", color=cq.Color(0.5, 0.5, 0.52))
       .add(f.make_crossbar(False), name="Querleiste_unten", color=cq.Color(0.5, 0.5, 0.52))
       .add(f.make_bottom(), name="Bodenplatte", color=cq.Color(0.2, 0.2, 0.21))
       .add(f.make_tab_screws(), name="Laschenschrauben", color=cq.Color(0.3, 0.3, 0.3)))
for sx, nm in ((1, "rechts"), (-1, "links")):
    asm.add(f.make_side_panel(sx), name=f"Seitenteil_{nm}", color=cq.Color(0.1, 0.1, 0.11))
for p, nm in ((f.make_knob_shell(), "Knopf"), (f.make_light_tube(), "Lichtleiter"), (f.make_cone_insert(), "Konus")):
    asm.add(p, name=nm, loc=cq.Location((f.KNOB_X, 0, 0)), color=cq.Color(0.2, 0.2, 0.2))
asm.save(f"{OUT}/RD160_Gehaeuse_Vorschau.step")

# Iso-Ansicht des Gehäuses (Deckel aufgelegt)
vals = [v for _, p in [(0, f.make_frame()), (0, cover), (0, f.make_side_panel(1)), (0, f.make_side_panel(-1)),
                       (0, f.make_panel().translate((0, 0, f.CARRIER_T))),
                       (0, f.make_knob_shell().translate((f.KNOB_X, 0, 0)))] for v in p.vals()]
comp = cq.Workplane("XY").add(cq.Compound.makeCompound(vals).rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90))
cq.exporters.export(comp, "/tmp/geh_iso.svg", opt={"width": 1400, "height": 900, "projectionDir": (0.55, -1.0, 0.55),
                                                    "showHidden": False, "strokeWidth": 0.35})
subprocess.run(["rsvg-convert", "-b", "white", "/tmp/geh_iso.svg", "-o", "/tmp/geh_iso.png"], check=True)
subprocess.run(["convert", "/tmp/geh_iso.png", "-trim", "-rotate", "90", "-bordercolor", "white", "-border", "20",
                f"{OUT}/RD160_Gehaeuse_Iso.png"], check=True)

# ---------------- Zeichnung ----------------
W, T = f.W, f.T
zb = T - f.BAND
zf = zb - f.JOINT                    # Deckelstirn
run = math.sqrt(f.CUTTER_R ** 2 - (f.CUTTER_R - f.GROOVE_D) ** 2)
wf = 2 * (W / 2 - f.END_W - f.JOINT)
wl = W                                  # volle Breite über die Seitenteile
wt = 2 * (W / 2 - f.END_W - run - 1.0)
z1 = f.FL_Z0                         # Ende Frontbereich (Absatz)
zr = f.Z_REAR
L = zf - zr                          # Deckellänge ohne Feder
# Koordinaten Zeichnung: u = x, v = Abstand von der Deckelstirn nach hinten (v = zf - z)
V = lambda z: zf - z

fig = plt.figure(figsize=(16.5, 11.7))
ax = fig.add_axes([0.03, 0.30, 0.62, 0.64]); ax.set_aspect("equal"); ax.axis("off")
outline = [(-wf / 2, V(zf)), (wf / 2, V(zf)), (wf / 2, V(z1 - 0.3)), (wl / 2, V(z1 - 0.3)), (wl / 2, V(zr)),
           (-wl / 2, V(zr)), (-wl / 2, V(z1 - 0.3)), (-wf / 2, V(z1 - 0.3))]
ax.add_patch(Polygon(outline, closed=True, fc="#e4e6ea", ec="k", lw=1.0))
_fa, _fb = f.GROOVE_X0 + run + 1.0, W / 2 - f.END_W - run - 1.0      # Feder: zwei Abschnitte neben der Displaytasche
_tl = f.TONGUE_L + f.JOINT - 0.3
for _s in (1, -1):
    ax.add_patch(Rectangle((min(_s * _fa, _s * _fb), -_tl), _fb - _fa, _tl, fc="#c9ccd1", ec="k", lw=0.8))
_xo, _zf, _xi, _zi = f.deco_rect()
ax.add_patch(Rectangle((-_xo, V(_zf)), 2 * _xo, V(_zi) - V(_zf), fc="#b03030", ec="#b03030", lw=0.6))      # Stirnlinie
for _s in (1, -1):
    ax.add_patch(Rectangle((_xi if _s > 0 else -_xi - f.DECO_W - f.JOINT, V(_zf)), f.DECO_W + f.JOINT, V(f.Z_REAR) - V(_zf), fc="#b03030", ec="#b03030", lw=0.6))
ax.annotate(f"Ziernut {f.DECO_W} breit, {f.DECO_D} tief: vorn entlang dem Stoß zur Front, Innenecke R{f.DECO_IR} (nicht um die Radien),\n"
            f"seitlich {f.W / 2 - _xo - f.JOINT:.1f}..{f.W / 2 - _xi:.1f} von der Kante ({f.DECO_W + f.JOINT:.1f} = Nut + Fuge vorn) gerade bis hinten (offen)",
            (_xi, V(_zf) + 40), (-200, V(f.Z_REAR) - 60), fontsize=8.5, color="#b03030",
            arrowprops=dict(arrowstyle="-", lw=0.4, color="#b03030"))
for x, z in f.cover_screw_points():
    ax.add_patch(Circle((x, V(z)), 1.25, fc="none", ec="k", lw=0.7, ls="--"))
ax.invert_yaxis()


def dim_h(x0, x1, y, txt, off=0):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text((x0 + x1) / 2, y - 2 + off, txt, ha="center", va="bottom", fontsize=8.5)


def dim_v(x, y0, y1, txt):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(x + 2, (y0 + y1) / 2, txt, ha="left", va="center", fontsize=8.5, rotation=90)


dim_h(-wl / 2, wl / 2, V(zr) + 14, f"{wl:.1f} (volle Breite, liegt auf den Seitenteilen, außen bündig)")
dim_h(-wf / 2, wf / 2, -14, f"{wf:.1f} (vorn zwischen den Seitenwänden der Front)")
dim_h(_fa, _fb, -26, f"Feder 2× {_fb - _fa:.1f} × {_tl:.1f} × {f.TONGUE_T:.0f} (oben {f.GROOVE_TOP:.0f} abgesetzt)")
dim_v(wl / 2 + 8, 0, V(zr), f"{L:.1f} ohne Feder")
dim_v(wl / 2 + 22, 0, V(z1 - 0.3), f"{V(z1 - 0.3):.1f}")
x, z = f.cover_screw_points()[0]
ax.annotate(f"2× M3-Sackgewinde von UNTEN, {f.COVER_THREAD:.0f} tief (oben unsichtbar)\n{f.COVER_SCREW_U} vom Außenrand, {f.COVER_SCREW_Z - f.Z_REAR:.0f} vor Hinterkante",
            (x, V(z)), (x - 150, V(z) - 40), fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.4))
ax.annotate(f"Eckausklinkung {(wl - wf) / 2:.1f} × {V(z1 - 0.3):.1f}\n(Seitenwand der Front)", (-wf / 2 - 3, V(z1 - 0.3) - 3),
            (-wl / 2 + 15, 60), fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.4))
ax.text(0, V(zr) / 2, "DECKEL – Draufsicht\nEN AW-6061-T6, 5 mm", ha="center", va="center", fontsize=12, color="#555")
ax.text(0, -40, "FRONT", ha="center", fontsize=10, color="#555")
ax.set_xlim(-wl / 2 - 20, wl / 2 + 40); ax.set_ylim(V(zr) + 34, -46)

# Schnitte aus dem CAD
ST = {"Front": ("#c9ccd1", "///"), "Deckel": ("#9fb3c8", "\\\\"), "Seitenteil": ("#55585e", "\\\\\\"),
      "Schaum": ("#444", None), "Klotz": ("#b8bcc2", "xx"), "Rückwand": ("#2b2b2e", None)}


def draw(a, sec, name):
    col, hat = ST[name]
    for face in sec.faces().vals():
        n = 3000
        pts = [(p.x, p.y) for p in face.outerWire().positions([i / n for i in range(n + 1)])]
        a.add_patch(Polygon(pts, closed=True, fc=col, ec="k", lw=0.7, hatch=hat))
        for inner in face.innerWires():
            ip = [(p.x, p.y) for p in inner.positions([i / 200 for i in range(201)])]
            a.add_patch(Polygon(ip, closed=True, fc="white", ec="k", lw=0.5))


yt = f.H / 2
P = [("Front", cq.Workplane("XY").add(f.make_bezel().val().fuse(f.make_carrier().val()))), ("Deckel", cover), ("Seitenteil", f.make_side_panel(1)),
     ("Schaum", f.make_foam()), ("Rückwand", f.make_rear_panel())]
# A: Längsschnitt vorn bei X = 0
a1 = fig.add_axes([0.67, 0.68, 0.31, 0.24]); a1.set_aspect("equal"); a1.axis("off")
for n, p in P:
    try:
        draw(a1, p.rotate((0, 0, 0), (0, 1, 0), -90).section(0.0), n)
    except Exception:
        pass
a1.set_xlim(-(T + 2), -(f.FL_Z0 - 25)); a1.set_ylim(yt - 12, yt + 3)
a1.set_title("A  Vorderkante, Schnitt X = 0: Feder in der Nut, Schaum darunter", fontsize=9, loc="left")
# B: Querschnitt Seitenrand
a2 = fig.add_axes([0.67, 0.40, 0.31, 0.24]); a2.set_aspect("equal"); a2.axis("off")
for n, p in P:
    try:
        draw(a2, p.section(-150.0), n)
    except Exception:
        pass
a2.set_xlim(W / 2 - 22, W / 2 + 2); a2.set_ylim(yt - 18, yt + 3)
a2.set_title(f"B  Seitenrand: Deckel über Wand und Wulst, außen bündig", fontsize=9, loc="left")
# C: Hinterkante: Schnitt durch Deckelschraube
a3 = fig.add_axes([0.67, 0.10, 0.31, 0.26]); a3.set_aspect("equal"); a3.axis("off")
xs = f.cover_screw_points()[0][0]
for n, p in P:
    try:
        draw(a3, p.rotate((0, 0, 0), (0, 1, 0), -90).translate((0, 0, -xs)).section(0.0), n)
    except Exception:
        pass
a3.set_xlim(-(f.Z_REAR + 30), -(f.Z_REAR - 3)); a3.set_ylim(yt - 20, yt + 3)
a3.set_title(f"C  Hinterkante: M3 von unten durch Wulst in Deckel",
             fontsize=9, loc="left")

notes = [
    f"FERTIGUNG DECKEL (Bodenblech {f.BOT_T:.0f} mm: Rechteck im umlaufenden Absatz von Front, Seitenteilen und Rückwand, unten bündig, 10× Ø3,4 für ISO 7380 M3×6)",
    f"1. EN AW-6061-T6 Platte 5 mm, Zuschnitt {wl:.1f} × {L + f.TONGUE_L:.1f} (inkl. Feder). Planheit ≤ 0,2.",
    "2. Ebene Platte, keine Absätze an den Längsseiten; Kanten oben Fase 0,3.",
    f"3. Vorn: Eckausklinkungen {(wl - wf) / 2:.1f} × {V(z1 - 0.3):.1f}; Feder 2× {_fb - _fa:.1f} breit (ab ±{_fa:.1f}), oben {f.GROOVE_TOP:.0f} abgesetzt, {_tl:.1f} lang.",
    f"4. Hinten 2× M3-Sackgewinde von unten, Kernloch Ø2,5 × 4, Gewinde {f.COVER_THREAD:.0f} tief (2 mm Restwand) – keine Bohrungen oben.",
    f"5. Ziernut oben {f.DECO_W} × {f.DECO_D} tief: vorn entlang der Stirn, Innenecke R{f.DECO_IR}, seitlich {f.W / 2 - f.deco_rect()[0] - f.JOINT:.1f}..{f.W / 2 - f.deco_rect()[2]:.1f} von der Kante ({f.DECO_W + f.JOINT:.1f} breit) gerade bis hinten offen (Gravierfräser Ø0,6), vor dem Eloxieren. Frontzone {2 * (f.W / 2 - f.END_W - f.JOINT):.1f} breit, Ecken R{f.SEAT_R - f.JOINT:.1f}, Fuge {f.JOINT} zur Front.",
    "6. Oberfläche wie Rahmen (Glasperlen + Eloxal schwarz) oder gebürstet + Eloxal natur.",
    "MONTAGE: Deckel von hinten flach einschieben (liegt auf den Seitenteilen), Feder in die Nut; liegt auf Wulst, Laschen",
    f"und Schaumstoff ({f.FOAM_T:.0f} → {f.FOAM_C}). Hinten 2× ISO 4762 M3×10 von unten durch die Wulst (Zugang bei abgenommenem Bodenblech).",
    f"Masse ca. {cover.val().Volume() * 2.7e-3 / 1000:.2f} kg.",
]
fig.text(0.03, 0.03, "\n".join(notes), fontsize=9, va="bottom", family="DejaVu Sans")
fig.suptitle("RD160-Nachbau – Deckel (Maße mm)", x=0.03, ha="left", fontsize=13)
fig.savefig(f"{OUT}/RD160_Deckel_Zeichnung.pdf")
fig.savefig(f"{OUT}/RD160_Deckel_Zeichnung.png", dpi=120)
print("ok", round(L, 1), round(wl, 1), round(wf, 1), round(wt, 1))
