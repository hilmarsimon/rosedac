"""Vorschau Testfront: Rückansicht (Klammern, Sensorhalter) und Schrägansicht vorn."""
import os, subprocess, cadquery as cq
import frontplatte as f, testfront as t
OUT = t.OUT
cl = t.display_clamp()
clamps = [cl.translate((127, 25, 0)), cl.translate((127, -25, 0)),
          cl.rotate((0, 0, 0), (0, 0, 1), 180).translate((-127, 25, 0)), cl.rotate((0, 0, 0), (0, 0, 1), 180).translate((-127, -25, 0))]
parts = [t.half(-1).translate((-1.5, 0, 0)), t.half(1).translate((1.5, 0, 0)), t.sensor_holder().translate((1.5, 0, 0))]
parts += [c.translate((1.5 if i < 2 else -1.5, 0, 0)) for i, c in enumerate(clamps)]
front = parts + [t.panel_half(-1).translate((-1.5, 0, f.CARRIER_T)), t.panel_half(1).translate((1.5, 0, f.CARRIER_T)),
                 f.make_knob().translate((f.KNOB_X + 1.5, 0, 0))]
def render(ps, name, pd, rot):
    vals = [v for p in ps for v in p.vals()]
    comp = cq.Workplane("XY").add(cq.Compound.makeCompound(vals).rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90))
    cq.exporters.export(comp, f"/tmp/{name}.svg", opt={"width": 1400, "height": 700, "projectionDir": pd, "showHidden": False, "strokeWidth": 0.3})
    subprocess.run(["rsvg-convert", "-b", "white", f"/tmp/{name}.svg", "-o", f"/tmp/{name}.png"], check=True)
    subprocess.run(["convert", f"/tmp/{name}.png", "-trim", "-rotate", rot, "-bordercolor", "white", "-border", "20", f"/tmp/{name}_r.png"], check=True)
render(parts, "tf_hinten", (0.25, 1.0, 0.35), "-90")
render(front, "tf_vorn", (0.3, -1.0, 0.45), "90")
subprocess.run(["convert", "/tmp/tf_vorn_r.png", "/tmp/tf_hinten_r.png", "-background", "white", "-gravity", "center", "-append",
                os.path.join(OUT, "Testfront_Vorschau.png")], check=True)
print("ok")
