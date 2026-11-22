"""Schrägansicht von vorn links unten wie Review-Foto: geriffelte Seitenteile."""
import os, subprocess, cadquery as cq
import frontplatte as f
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
parts = [f.make_frame(), f.make_cover(), f.make_bottom(), f.make_side_panel(1), f.make_side_panel(-1),
         f.make_panel().translate((0, 0, f.CARRIER_T)), f.make_knob_shell().translate((f.KNOB_X, 0, 0)),
         f.make_light_tube().translate((f.KNOB_X, 0, 0))]
vals = [v for p in parts for v in p.vals()]
comp = cq.Workplane("XY").add(cq.Compound.makeCompound(vals).rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90))
cq.exporters.export(comp, "/tmp/rippen.svg", opt={"width": 1600, "height": 900, "projectionDir": (-1.0, -0.75, 0.3),
                                                   "showHidden": False, "strokeWidth": 0.3})
subprocess.run(["rsvg-convert", "-b", "white", "/tmp/rippen.svg", "-o", "/tmp/rippen.png"], check=True)
subprocess.run(["convert", "/tmp/rippen.png", "-trim", "-bordercolor", "white", "-border", "20", os.path.join(OUT, "RD160_Gehaeuse_Rippen.png")], check=True)
print("ok")
