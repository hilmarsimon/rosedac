"""Eckansicht Rahmen (Blick von hinten oben auf die rechte Geräteecke) zum Vergleich mit dem Innenfoto."""
import os, subprocess, cadquery as cq
import frontplatte as f
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
clip = cq.Workplane("XY").box(140, 120, 80).translate((f.W / 2 - 60, 0, 0))
parts = [f.make_frame(), f.make_panel().translate((0, 0, f.CARRIER_T)), f.make_foam(), f.make_side_stub(1), f.make_side_stub(-1), f.make_tab_screws(), f.make_cover_edge(40),
         f.make_knob_pcb().translate((f.KNOB_X, 0, 0))]
for p in (f.make_knob_shell(), f.make_light_tube(), f.make_cone_insert()):
    parts.append(p.translate((f.KNOB_X, 0, 0)))
vals = []
for p in parts:
    try:
        vals += p.intersect(clip).vals()
    except Exception:
        pass
comp = cq.Workplane("XY").add(cq.Compound.makeCompound(vals).rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90))
for name, pd in (("ecke_hinten_oben", (0.45, 1.0, 0.9)), ("ecke_vorn_oben", (0.6, -1.0, 0.8))):
    svg = f"/tmp/{name}.svg"
    cq.exporters.export(comp, svg, opt={"width": 1100, "height": 800, "projectionDir": pd, "showHidden": False, "strokeWidth": 0.35})
    subprocess.run(["rsvg-convert", "-b", "white", svg, "-o", f"/tmp/{name}.png"], check=True)
for name, rot in (("ecke_hinten_oben", "-90"), ("ecke_vorn_oben", "90")):
    subprocess.run(["convert", f"/tmp/{name}.png", "-trim", "-rotate", rot, "-bordercolor", "white", "-border", "30",
                    f"/tmp/{name}_r.png"], check=True)
subprocess.run(["convert", "/tmp/ecke_hinten_oben_r.png", "/tmp/ecke_vorn_oben_r.png", "-background", "white",
                "-gravity", "center", "-append", os.path.join(OUT, "RD160_Rahmen_Ecke.png")], check=True)
print("ok")
