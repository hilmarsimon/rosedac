"""Bodenblech: Ansicht von unten mit Schraubenbild, Schnitte durch die Auflagen (Front, Seitenwand, Rückwand), DXF."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.collections import PolyCollection
from matplotlib.backends.backend_pdf import PdfPages
import cadquery as cq
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
FOOT_D, FOOT_X, FOOT_IN = 46.0, 165.0, 45.0          # wie gehaeuse_baugruppe.py (Annahme Füße)
SCR_DK, SCR_K, SCR_L = 5.7, 1.65, 6.0                # ISO 7380 M3x6


def gruppen():
    """Schraubengruppen (Kennung, Text, Punkte (x, z), Farbe)."""
    return [("F", "Frontflansch (Träger), M3 6 tief", f.bot_flange_points(), "#c0392b"),
            ("W", "Wulst Seitenteil vorn", f.bot_front_points(), "#2471a3"),
            ("H", "Wulst Seitenteil hinten", f.cover_screw_points(), "#2471a3"),
            ("Q", "Querleiste unten, M3 7 tief", f.ql_fix_points(), "#1e8449")]


def schrauben():
    y = -f.H / 2
    sol = []
    for _, _, pts, _ in gruppen():
        for x, z in pts:
            sol.append(cq.Solid.makeCylinder(SCR_DK / 2, SCR_K, cq.Vector(x, y - SCR_K, z), cq.Vector(0, 1, 0))
                       .fuse(cq.Solid.makeCylinder(1.5, SCR_L, cq.Vector(x, y, z), cq.Vector(0, 1, 0))))
    return cq.Workplane("XY").add(cq.Compound.makeCompound(sol))


TEIL = [("Blende", f.make_bezel(), "#2b2b2d"), ("Träger", f.make_carrier(), "#8a8c90"),
        ("Seitenteil", f.make_side_panel(1), "#5d6066"), ("Rückwand", f.make_rear_panel(), "#5d6066"),
        ("Querleiste", f.make_crossbar(False), "#a7a9ad"), ("Boden", f.make_bottom(), "#e67e22"),
        ("Schrauben", schrauben(), "#c9a227")]


def schnitt(solid, achse, wert):
    """Schnittflächen in der Ebene achse = wert ('x': Ebene YZ -> (z, y); 'z': Ebene XY -> (x, y))."""
    if achse == "x":
        slab = cq.Workplane("YZ").workplane(offset=wert).rect(800, 800).extrude(0.001)
    else:
        slab = cq.Workplane("XY").workplane(offset=wert).rect(1000, 1000).extrude(0.001)
    sec = solid.intersect(slab, clean=False)
    polys = []
    for fc in sec.faces().vals():
        n = fc.normalAt()
        c = fc.Center()
        if achse == "x" and not (abs(c.x - wert) < 1e-4 and abs(n.x) > 0.99):
            continue
        if achse == "z" and not (abs(c.z - wert) < 1e-4 and abs(n.z) > 0.99):
            continue
        uv = (lambda p: ((p.z if achse == "x" else p.x), p.y))
        vs, tris = fc.tessellate(0.01, 0.2)
        tri = [[uv(vs[i]) for i in t] for t in tris]
        kanten = [[uv(e.positionAt(i / 16)) for i in range(17)] for e in fc.Edges()]
        polys.append((tri, kanten))
    return polys


def detail(ax, achse, wert, xlim, ylim, titel, notiz=None):
    for n, s, c in TEIL:
        for tri, kanten in schnitt(s, achse, wert):
            ax.add_collection(PolyCollection(tri, fc=c, ec=c, lw=0.2))
            for k in kanten:
                ax.plot(*zip(*k), color="k", lw=0.35)
    ax.axhline(-f.H / 2, color="k", lw=0.4, ls="--")
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.grid(lw=0.2)
    ax.set_title(titel, fontsize=8, loc="left")
    ax.set_xlabel("Z (hinten ← → vorn)" if achse == "x" else "X (innen ← → außen)", fontsize=7)
    ax.set_ylabel("Y", fontsize=7); ax.tick_params(labelsize=6)
    if notiz:
        ax.text(0.02, 0.97, notiz, transform=ax.transAxes, fontsize=6.3, va="top",
                bbox=dict(fc="white", ec="0.7", lw=0.4))


def ansicht_unten(ax):
    """Ansicht von unten, Front unten. Blick nach oben: rechte Geräteseite erscheint links (u = -x), v = -z."""
    b = f.make_bottom().val().BoundingBox()
    zf, zr = f.T, f.Z_REAR
    ax.add_patch(Rectangle((-f.W / 2, -zf), f.W, zf - zr, fc="#f2f2f2", ec="k", lw=0.8))   # Gehäuseumriss
    ax.add_patch(Rectangle((-b.xmax, -b.zmax), b.xlen, b.zlen, fc="#f6c89a", ec="#e67e22", lw=1.0))
    for sx in (1, -1):
        for z in (f.FL_Z0 - FOOT_IN, f.Z_REAR + FOOT_IN):
            ax.add_patch(Circle((-sx * FOOT_X, -z), FOOT_D / 2, fc="none", ec="0.45", lw=0.6, ls=":"))
    for k, txt, pts, col in gruppen():
        for x, z in pts:
            ax.add_patch(Circle((-x, -z), 1.7, fc="white", ec=col, lw=0.9))
            ax.add_patch(Circle((-x, -z), SCR_DK / 2, fc="none", ec=col, lw=0.4, ls="--"))
            ax.text(-x + 4, -z + 4, k, fontsize=7, color=col, weight="bold")
    # Schnittlinien
    for u, lab in ((0.0, "A"), (-f.cover_screw_points()[0][0], "B")):
        ax.plot([u, u], [-zf - 8, -zr + 8], color="0.3", lw=0.6, ls="-.")
        ax.text(u + 2, -zr + 5, lab, fontsize=8, weight="bold")
    zc = (f.FL_Z0 + f.Z_REAR) / 2
    ax.plot([-f.W / 2 - 8, -f.W / 2 + 40], [-zc, -zc], color="0.3", lw=0.6, ls="-.")
    ax.text(-f.W / 2 - 8, -zc + 3, "C", fontsize=8, weight="bold")
    ax.text(-f.W / 2 + 3, -zf - 9, "Gerät rechts", fontsize=7); ax.text(f.W / 2 - 40, -zf - 9, "Gerät links", fontsize=7)
    ax.text(0, -zf - 9, "FRONT", fontsize=8, ha="center", weight="bold")
    ax.text(0, -zr + 14, "RÜCKWAND", fontsize=8, ha="center", weight="bold")
    ax.annotate(f"Bodenblech {b.xlen:.1f} × {b.zlen:.1f} × {f.BOT_T:.0f}", (0, -zc + 40), fontsize=8, ha="center")
    ax.set_xlim(-f.W / 2 - 15, f.W / 2 + 15); ax.set_ylim(-zf - 14, -zr + 20)
    ax.set_aspect("equal"); ax.tick_params(labelsize=6); ax.grid(lw=0.15)
    ax.set_title("Ansicht von UNTEN (Front unten, Geräteseiten vertauscht) – Füße Ø46 punktiert (Annahme)", fontsize=8, loc="left")


def export_dxf():
    import ezdxf
    b = f.make_bottom().val().BoundingBox()
    d = ezdxf.new("R2010"); d.units = ezdxf.units.MM; m = d.modelspace()
    d.layers.add("KONTUR"); d.layers.add("BOHRUNG")
    # Ansicht von unten wie Zeichnung: u = -x, v = -z
    m.add_lwpolyline([(-b.xmax, -b.zmax), (-b.xmin, -b.zmax), (-b.xmin, -b.zmin), (-b.xmax, -b.zmin)], close=True,
                     dxfattribs={"layer": "KONTUR"})
    for _, _, pts, _ in gruppen():
        for x, z in pts:
            m.add_circle((-x, -z), 1.7, dxfattribs={"layer": "BOHRUNG"})
    d.saveas(f"{OUT}/RD160_Bodenplatte.dxf")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    xb = f.cover_screw_points()[0][0]
    fig = plt.figure(figsize=(16.5, 11.7))
    gs = fig.add_gridspec(3, 4, height_ratios=[1.35, 1, 1])
    ansicht_unten(fig.add_subplot(gs[0, :3]))
    axt = fig.add_subplot(gs[0, 3]); axt.axis("off")
    zeilen = [("Kenn.", "Gegenstück", "Anz.", "Rand Blech [mm]")]
    b = f.make_bottom().val().BoundingBox()
    for k, txt, pts, _ in gruppen():
        rd = min(min(abs(x - b.xmin), abs(b.xmax - x), abs(z - b.zmin), abs(b.zmax - z)) for x, z in pts) - 1.7
        zeilen.append((k, txt, str(len(pts)), f"{rd:.1f}"))
    tab = axt.table(cellText=zeilen[1:], colLabels=zeilen[0], loc="upper center", cellLoc="left", colWidths=[0.13, 0.5, 0.09, 0.28])
    tab.auto_set_font_size(False); tab.set_fontsize(7); tab.scale(1, 1.5)
    axt.text(0, 0.45, "\n".join([
        f"Bodenblech EN AW-5754, {f.BOT_T:.0f} mm, Rechteck {b.xlen:.1f} × {b.zlen:.1f}",
        f"liegt von unten im umlaufenden Absatz {f.BOT_T:.0f} tief:",
        f"  Front {f.BOT_ABS_FRONT:.0f} (Träger), Seitenwände {f.BOT_ABS_SIDE:.1f}, Rückwand {f.BOT_ABS_REAR:.0f}",
        "  Spiel 0,2 je Seite, Unterseite bündig mit Geräteunterkante",
        f"10× Ø3,4 für ISO 7380 M3×6 (Kopf Ø{SCR_DK} × {SCR_K} steht unten vor)",
        "Gewinde M3 in Träger, Wulst der Seitenteile und Querleiste",
        "Zugang: Blech ab → Deckelschrauben hinten (Wulst) frei",
        "Bohrbild in RD160_Bodenplatte.dxf (Ansicht von unten)"]),
        fontsize=7.2, va="top", family="monospace", transform=axt.transAxes)
    zf = f.bot_flange_points()[0][1]
    detail(fig.add_subplot(gs[1, 0]), "x", 0.0, (-14, 14), (-44, -26), "A – Front, x = 0: Schraube F in den Trägerflansch",
           f"Lochmitte z {zf:.1f}, Blechkante z {b.zmax:.1f}\nRand {b.zmax - zf - 1.7:.1f} mm")
    detail(fig.add_subplot(gs[1, 1]), "x", 0.0, (f.Z_REAR - 3, f.Z_REAR + 25), (-44, -26), "A – Rückwand, x = 0: Schraube Q in die Querleiste")
    detail(fig.add_subplot(gs[1, 2]), "x", xb, (f.BOT_FRONT_Z - 14, f.BOT_FRONT_Z + 14), (-44, -26), f"B – x = {xb:.1f}: Schraube W in die Wulst (vorn)")
    detail(fig.add_subplot(gs[1, 3]), "x", xb, (f.Z_REAR - 3, f.Z_REAR + 25), (-44, -26), f"B – x = {xb:.1f}: Schraube H in die Wulst (hinten)")
    zc = (f.FL_Z0 + f.Z_REAR) / 2
    detail(fig.add_subplot(gs[2, 0]), "z", zc, (f.W / 2 - 26, f.W / 2 + 2), (-44, -26), f"C – Seitenwand rechts, z = {zc:.0f}: Absatz {f.BOT_ABS_SIDE}")
    detail(fig.add_subplot(gs[2, 1]), "z", f.BOT_FRONT_Z, (f.W / 2 - 26, f.W / 2 + 2), (-44, -26), f"Seitenwand, z = {f.BOT_FRONT_Z:.1f}: Schraube W")
    detail(fig.add_subplot(gs[2, 2]), "z", zf, (-6, 22), (-44, -26), f"Front, z = {zf:.1f}: Schraube F (x = 0) quer")
    axl = fig.add_subplot(gs[2, 3]); axl.axis("off")
    for i, (n, _, c) in enumerate(TEIL):
        axl.add_patch(Rectangle((0.05, 0.85 - i * 0.11), 0.08, 0.07, fc=c, ec="k", lw=0.3, transform=axl.transAxes))
        axl.text(0.17, 0.885 - i * 0.11, n, fontsize=8, va="center", transform=axl.transAxes)
    axl.text(0.05, 0.05, "Strichlinie: Geräteunterkante y = −H/2", fontsize=7, transform=axl.transAxes)
    fig.suptitle(f"RD160 – Bodenblech und Befestigung (H = {f.H:.0f})", fontsize=11)
    fig.tight_layout()
    fig.savefig(f"{OUT}/RD160_Boden_Zeichnung.png", dpi=150)
    with PdfPages(f"{OUT}/RD160_Boden_Zeichnung.pdf") as pdf:
        pdf.savefig(fig)
    export_dxf()
    print("ok")
