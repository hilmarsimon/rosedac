"""Vorschau Testfront: Rückansicht (Displays, Sensorhalter) und Schrägansicht vorn."""
import os, subprocess, cadquery as cq
import frontplatte as f, testfront as t
OUT = t.OUT
parts = [t.half(-1).translate((-1.5, 0, 0)), t.half(1).translate((1.5, 0, 0)), t.sensor_holder().translate((1.5, 0, 0))]
parts += [f.make_display(f.DISP_CX[0]).translate((-1.5, 0, 0)), f.make_display(f.DISP_CX[1]).translate((1.5, 0, 0))]
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
