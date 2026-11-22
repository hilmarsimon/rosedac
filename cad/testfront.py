"""Druckbare Testfront 1:1 für Display-, Plexiglas- und Reglertest (ohne DAC).
Basis ist der echte Träger aus frontplatte.py (nur Z 0..T, ohne Flansche/Seitenwände/Laschen), geteilt bei X = 0
in zwei Hälften (Druckbett ≥ 220 mm). Änderungen für den Druck: Gewinde M3 -> Aufnahme für Einschmelzmuttern,
Passstifte Ø3 an der Trennfläche. Dazu: Displayklammern, Sensor-/LED-Halter statt Knopfplatine, halbe
Plexiglasplatten als DXF, Knopfteile als STL.  Druck: Rückseite (Z = 0) aufs Bett, Front oben."""
import os, math
import cadquery as cq
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "testfront")
os.makedirs(OUT, exist_ok=True)
W, H, T = f.W, f.H, f.T

INSERT_D, INSERT_L = 4.0, 6.0          # M3-Einschmelzmutter (Ruthex M3×5,7: Bohrung Ø4,0)
DOWEL_D, DOWEL_L = 3.1, 8.0            # Passstift Ø3×15 (Stahl/Filament), je Seite 8 tief
DOWEL_PTS = [(40.0, 4.5), (-40.0, 4.5)]   # (Y, Z) im Steg ober-/unterhalb der Displaytasche
DISP_T = 3.0                            # Annahme Dicke Displaymodul (Glas+Folie) – am echten Modul messen!
CLAMP_GAP = 0.5                         # Luft Klammerfinger -> Display (Schaumstoff 1 mm dazwischen)


def plate():
    body = f.make_frame().intersect(cq.Workplane("XY").box(W + 2, H + 2, T, centered=(True, True, False)))
    pts = [pt for v in f.M3_HOLES.values() for pt in v]
    body = body.cut(cq.Workplane("XY").pushPoints(pts).circle(INSERT_D / 2).extrude(INSERT_L))
    return body


def half(sx):
    b = plate().intersect(cq.Workplane("XY").box(W / 2 + 1, H + 2, T + 2, centered=(False, True, False))
                          .translate((-(W / 2 + 1) if sx < 0 else 0, 0, -1)))
    for y, z in DOWEL_PTS:
        b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(DOWEL_D / 2, DOWEL_L, cq.Vector(0, y, z),
                                                               cq.Vector(sx, 0, 0))))
    return b


def display_clamp():
    """Klammer an den Panel-Klemmrahmen-Bohrungen (±127, ±25): Lasche 14×12×3 mit Finger in die Displaytasche."""
    finger = f.CARRIER_T - DISP_T - CLAMP_GAP      # vom Trägerrücken bis kurz vor das Display
    c = cq.Workplane("XY").box(14, 12, 3, centered=(True, True, False)).translate((0, 0, -3))
    c = c.union(cq.Workplane("XY").box(5, 10, finger, centered=(True, True, False)).translate((-5.5, 0, 0)))
    return c.cut(cq.Workplane("XY").circle(1.7).extrude(10).translate((0, 0, -5)))


def sensor_holder():
    """Ersatz für die Knopfplatine im Test: Umriss wie PCB_OUTLINE, 4 mm stark, Front bei Z = PCB_Z.
    Tasche für AS5600-Breakout 23,5×23,5×1,6 mittig (Chip zeigt nach vorn, 2,5 mm zum Magneten),
    12 Bohrungen Ø3,1 für 3-mm-LEDs auf dem Lichtkreis, Taster B3F-1000 an der Einschaltposition,
    4 Distanzbuchsen bis zum Träger (M3 in Einschmelzmuttern)."""
    z0, t = f.PCB_Z - 4.0, 4.0
    p = cq.Workplane("XY").workplane(offset=z0).polyline(f.PCB_OUTLINE).close().extrude(t)
    p = p.edges("|Z").fillet(1.0)
    p = p.cut(cq.Workplane("XY").workplane(offset=f.PCB_Z - 1.6).rect(23.5, 23.5).extrude(1.7))
    p = p.cut(cq.Workplane("XY").workplane(offset=z0 - 1).rect(14, 14).extrude(t))          # Lötpunkte/Kabel
    leds = [(f.WIN_PCD / 2 * math.cos(math.radians(k * 30)), f.WIN_PCD / 2 * math.sin(math.radians(k * 30)))
            for k in range(f.WIN_N)]
    p = p.cut(cq.Workplane("XY").workplane(offset=z0 - 1).pushPoints(leds).circle(1.55).extrude(t + 2))
    sx, sy = f.PWR_X - f.KNOB_X, f.PWR_Y
    p = p.cut(cq.Workplane("XY").workplane(offset=z0 - 1)
              .pushPoints([(sx + a * 3.25, sy + b * 2.25) for a in (-1, 1) for b in (-1, 1)]).circle(0.6).extrude(t + 2))
    holes = [(x - f.KNOB_X, y) for x, y in f.M3_HOLES["LED/Encoder-PCB"]]
    p = p.union(cq.Workplane("XY").workplane(offset=f.PCB_Z).pushPoints(holes).circle(3.5).extrude(-f.PCB_Z))
    p = p.cut(cq.Workplane("XY").workplane(offset=z0 - 1).pushPoints(holes).circle(1.7).extrude(t + 10))
    return p.translate((f.KNOB_X, 0, 0))


def panel_half(sx):
    """Halbe Plexiglasplatte 210,0 breit (passt aus A4-Muster 210×297), Trennung bei X = 0."""
    pw = 210.0
    x0 = -0.25 - pw if sx < 0 else 0.25
    p = f.make_panel().intersect(cq.Workplane("XY").box(pw, H, 10, centered=(False, True, False)).translate((x0, 0, -1)))
    return p


if __name__ == "__main__":
    parts = {"Testfront_links": half(-1), "Testfront_rechts": half(1), "Displayklammer": display_clamp(),
             "Sensorhalter_Knopf": sensor_holder(),
             "Knopf_Becher": f.make_knob_shell(), "Knopf_Lichtleiter": f.make_light_tube(),
             "Knopf_Konus": f.make_cone_insert(), "Knopf_Haltescheibe": f.make_washer(),
             "Tasterkappe": f.make_button_cap(), "Einschaltkappe": f.make_power_cap()}
    for n, p in parts.items():
        v = p.val()
        assert v.isValid(), n
        cq.exporters.export(p, f"{OUT}/{n}.step")
        cq.exporters.export(p, f"{OUT}/{n}.stl", tolerance=0.02, angularTolerance=0.1)
        bb = v.BoundingBox()
        print(f"{n:22s} {bb.xlen:6.1f} × {bb.ylen:5.1f} × {bb.zlen:5.1f} mm")
    for sx, n in ((-1, "links"), (1, "rechts")):
        ph = panel_half(sx)
        cq.exporters.export(ph.section(f.PANEL_T / 2), f"{OUT}/Plexiglas_Testhaelfte_{n}.dxf")
    # Kollisionsprüfung Sensorhalter <-> Knopf/Scheibe/Träger
    sh = sensor_holder()
    others = {"Träger": plate(), "Becher": f.make_knob_shell().translate((f.KNOB_X, 0, 0)),
              "Haltescheibe": f.make_washer().translate((f.KNOB_X, 0, f.HUB_Z0 - f.WASHER_T))}
    for n, o in others.items():
        v = sh.intersect(o).val().Volume()
        print("Sensorhalter vs", n, "Überschneidung", round(v, 3))
    print("ok")
