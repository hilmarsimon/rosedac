"""Draufsicht der Front (Blick von oben) neben dem Draufsicht-Foto des Originals."""
import os, subprocess, cadquery as cq
import frontplatte as f
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
parts = [f.make_frame(), f.make_panel().translate((0, 0, f.CARRIER_T)), f.make_foam(), f.make_side_stub(1), f.make_side_stub(-1), f.make_tab_screws()]
for p in (f.make_knob_shell(), f.make_light_tube(), f.make_cone_insert()):
    parts.append(p.translate((f.KNOB_X, 0, 0)))
vals = [v for p in parts for v in p.vals()]
comp = cq.Workplane("XY").add(cq.Compound.makeCompound(vals).rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90))
svg = "/tmp/draufsicht.svg"
cq.exporters.export(comp, svg, opt={"width": 1600, "height": 600, "projectionDir": (0, 0, 1), "showHidden": False,
                                    "strokeWidth": 0.4})
subprocess.run(["rsvg-convert", "-b", "white", svg, "-o", "/tmp/draufsicht.png"], check=True)
print("ok")
