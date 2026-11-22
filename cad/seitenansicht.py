"""Seitenansicht + Schrägansicht der Front mit Drehknopf zur Sichtprüfung der Proportionen."""
import os, cadquery as cq, subprocess
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# ---------- 3D-Gesamtmodell ----------
solids = [f.make_frame(), f.make_panel().translate((0, 0, f.CARRIER_T))]
for part in (f.make_knob_shell(), f.make_light_tube(), f.make_cone_insert()):
    solids.append(part.translate((f.KNOB_X, 0, 0)))
solids.append(f.make_power_cap().translate((f.PWR_X, f.PWR_Y, f.PCB_Z + f.SW_H - 0.1)))
cap = f.make_button_cap()
for x, y in f.btn_positions():
    solids.append(cap.translate((x, y, f.BTN_CB_DEPTH - 5.7)))
comp = cq.Workplane("XY").add(cq.Compound.makeCompound([s for w in solids for s in w.vals()]))
views = {"schraeg": (0.55, -0.35, 1.0), "front": (0.0, 0.0, 1.0)}
for name, pd in views.items():
    svg = f"/tmp/fp_{name}.svg"
    cq.exporters.export(comp, svg, opt={"width": 1600, "height": 700, "projectionDir": pd, "showHidden": False,
                                        "strokeWidth": 0.35, "marginLeft": 20, "marginTop": 20})
    subprocess.run(["rsvg-convert", "-b", "white", svg, "-o", f"/tmp/fp_{name}.png"], check=True)

# ---------- 2D-Seitenansicht mit Maßen (Blick von rechts, Front links) ----------
fig = plt.figure(figsize=(16.5, 11.7))
ax = fig.add_axes([0.04, 0.42, 0.42, 0.53]); ax.set_aspect("equal"); ax.axis("off")
H, T, CT = f.H, f.T, f.CARRIER_T
BLK, AL, PM = "#1c1d1f", "#b9bcc2", "#3a3b40"
# Z nach links = vorn (Front links), Y nach oben
def X(z): return -z
ax.add_patch(Rectangle((X(T), -H / 2), T, H, fc=AL, ec="k", lw=0.8))                       # Rahmen
ax.add_patch(Rectangle((X(T), -f.PANEL_H / 2), f.PANEL_T, f.PANEL_H, fc=PM, ec="k", lw=0.6))  # Plexiglas
# Knopf: Hülse
z0, z1 = f.KNOB_Z0, f.KNOB_Z1
ax.add_patch(Rectangle((X(z1), -f.KNOB_D / 2), z1 - T, f.KNOB_D, fc=BLK, ec="k", lw=0.8))
ax.add_patch(Rectangle((X(z1), -f.TUBE_OD / 2), 0.8, f.TUBE_OD, fc="#f3f3ef", ec="none"))       # Leuchtkante
# Einschaltkappe
ax.add_patch(Rectangle((X(T + 1.5), f.PWR_Y - f.PWR_D / 2), 1.5, f.PWR_D, fc="#9a9ca1", ec="k", lw=0.6))
# Gehäuse hinten angedeutet
ax.add_patch(Rectangle((0, -H / 2), 60, H, fc="none", ec="0.6", lw=0.6, ls="--"))
ax.text(30, 0, "Gehäuse\n(angedeutet)", ha="center", va="center", fontsize=9, color="0.5")
# Maße
def dimv(x, y1, y2, t, side="left"):
    ax.annotate("", (x, y1), (x, y2), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(x - 1.5 if side == "left" else x + 1.5, (y1 + y2) / 2, t, rotation=90, ha="right" if side == "left" else "left",
            va="center", fontsize=9)
def dimh(y, x1, x2, t):
    ax.annotate("", (x1, y), (x2, y), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text((x1 + x2) / 2, y + 1.5, t, ha="center", va="bottom", fontsize=9)
dimv(X(z1) - 6, -f.KNOB_D / 2, f.KNOB_D / 2, f"Ø{f.KNOB_D:.0f}")
dimv(8, -H / 2, H / 2, f"Front {H:.0f}", side="right")
dimh(H / 2 + 6, X(z1), X(T), f"Überstand {f.KNOB_PROT:.0f}")
dimh(-H / 2 - 8, X(T), 0, f"{T:.0f}")
for yy in (-f.KNOB_D / 2, f.KNOB_D / 2):
    ax.plot([X(z1) - 8, X(z1)], [yy, yy], lw=0.4, color="0.4")
ax.plot([X(z1), X(z1)], [f.KNOB_D / 2, H / 2 + 8], lw=0.4, color="0.4")
ax.plot([X(T), X(T)], [H / 2, H / 2 + 8], lw=0.4, color="0.4")
ax.set_xlim(-55, 75); ax.set_ylim(-H / 2 - 16, H / 2 + 16)
ax.set_title("Seitenansicht von rechts (Maße in mm)", fontsize=11, loc="left")

# Verhältnisse
r1 = f.KNOB_D / H; r2 = f.KNOB_PROT / f.KNOB_D; r3 = f.KNOB_D / f.W
txt = (f"Verhältnisse Nachbau\n"
       f"Knopf-Ø / Fronthöhe       = {f.KNOB_D:.0f} / {H:.0f} = {r1:.2f}\n"
       f"Überstand / Knopf-Ø       = {f.KNOB_PROT:.0f} / {f.KNOB_D:.0f} = {r2:.2f}\n"
       f"Knopf-Ø / Frontbreite     = {f.KNOB_D:.0f} / {f.W:.0f} = {r3:.3f}\n"
       f"Konus: Ø{f.CONE_LIP_ID:.0f} vorn → Ø{f.CONE_FLOOR_D:.0f} in Frontebene\n\n"
       f"Vergleich mit den Produktfotos (gemessen in Pixeln)\n"
       f"Knopf-Ø / Frontbreite     ≈ 0,12   → Knopf ≈ 51 mm  ✓\n"
       f"Knopf-Ø / Fronthöhe       ≈ 0,72   (Nachbau {r1:.2f})\n"
       f"Überstand / Knopf-Ø       ≈ 0,23 (Draufsicht-Foto: ca. 11,5 mm)\n\n"
       f"Folgerung: Überstand 12 mm. Original-Korpus ca. 70–74 mm\n"
       f"(88 mm Datenblatt inkl. Füße). Nachbau H = {H:.0f} mm, damit\n"
       f"die DFR0524 (71 mm) hineinpassen (+4 mm zum Original).")
fig.text(0.50, 0.93, txt, fontsize=10.5, va="top", family="DejaVu Sans Mono")

# 3D-Ansichten einsetzen
for (img, rect, title) in (("/tmp/fp_schraeg.png", [0.02, 0.03, 0.96, 0.36], "Schrägansicht (orthografisch, ohne verdeckte Kanten)"),
                           ("/tmp/fp_front.png", [0.48, 0.40, 0.50, 0.22], "Vorderansicht")):
    a = fig.add_axes(rect); a.imshow(plt.imread(img)); a.axis("off"); a.set_title(title, fontsize=10, loc="left")
fig.savefig(os.path.join(OUT, "RD160_Front_Seitenansicht.pdf"))
fig.savefig(os.path.join(OUT, "RD160_Front_Seitenansicht.png"), dpi=110)
print("ok")
