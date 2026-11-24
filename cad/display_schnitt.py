"""Schnitte durch Front + Display (YZ): an einer Displayschraube und im Flansch-Freischnitt (Winkelstecker HDMI)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import cadquery as cq
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
TEIL = [("Blende", f.make_bezel(), "#2b2b2d"), ("Träger", f.make_carrier(), "#8a8c90"),
        ("Platte", f.make_panel().translate((0, 0, f.CARRIER_T)), "#101010"),
        ("Display", f.make_display(f.DISP_CX[1]), "#3d6fb0"), ("Deckel", f.make_cover(), "#c0c2c6"),
        ("Boden", f.make_bottom(), "#555"), ("Schrauben", f.make_display_screws(), "#c08a2a")]


def faces_at(solid, x):
    """Schnittflächen bei X = x als Liste von Polygonen (Y, Z)."""
    half = cq.Workplane("YZ").workplane(offset=x).rect(400, 400).extrude(0.001)
    sec = solid.intersect(half)
    polys = []
    from OCP.BRepTools import BRepTools_WireExplorer
    fcs = [fc for fc in sec.faces().vals() if abs(fc.Center().x - x) < 1e-4 and abs(fc.normalAt().x) > 0.99]
    for fc in fcs:
        pts = []
        ex = BRepTools_WireExplorer(fc.outerWire().wrapped)
        while ex.More():
            e = cq.Edge(ex.Current())
            ps = [e.positionAt(i / 12) for i in range(13)]
            if e.wrapped.Orientation().name == "TopAbs_REVERSED":
                ps = ps[::-1]
            pts += [(p.y, p.z) for p in ps]
            ex.Next()
        polys.append(pts)
    return polys


def draw(ax, x, titel):
    for n, s, c in TEIL:
        for pts in faces_at(s, x):
            ax.add_patch(Polygon(pts, closed=True, fc=c, ec="k", lw=0.3, alpha=0.9))
    ax.set_xlim(-f.H / 2 - 3, -f.H / 2 + 22); ax.set_ylim(-24, 15)
    ax.set_aspect("equal"); ax.grid(lw=0.2); ax.set_title(titel, fontsize=8, loc="left")
    ax.set_xlabel("Y (unten → oben)", fontsize=7); ax.set_ylabel("Z (hinten → vorn)", fontsize=7); ax.tick_params(labelsize=6)


if __name__ == "__main__":
    xs = f.DISP_SCREW_PTS[-1][0]                                   # untere Schraube rechtes Display
    xn = f.DISP_CX[1] + (f.DISP_HDMI[0] + f.DISP_HDMI[1]) / 2      # Mitte HDMI rechtes Display
    fig, axs = plt.subplots(1, 2, figsize=(12, 5.5))
    draw(axs[0], xs, f"Unterkante bei X = {xs:.2f}: Displayschraube M2,5 durch den Flansch")
    draw(axs[1], xn, f"Unterkante bei X = {xn:.2f}: HDMI-Buchse, Flansch ausgespart (Winkelstecker)")
    for a in axs:
        a.annotate("Glas an der Platte", (-f.DISP_GH / 2 + 3, f.CARRIER_T - 1), (-30, 12), fontsize=6.5,
                   arrowprops=dict(arrowstyle="->", lw=0.4))
    fig.suptitle(f"RD160 – Display Waveshare 5,5\" in der Front (H = {f.H:.0f})", fontsize=10)
    fig.tight_layout(); fig.savefig(f"{OUT}/RD160_Display_Schnitt.png", dpi=150)
    print("ok")
