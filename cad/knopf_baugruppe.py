"""Drehknopf als eigenständige Baugruppe (STEP). Ursprung: Knopfachse, Z=0 = Lagerrückseite, Z=12 = Frontebene."""
import os, cadquery as cq
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def bearing_6805():
    w = f.BRG_W
    outer = cq.Workplane("XY").circle(f.BRG_OD / 2).circle(33.4 / 2).extrude(w)
    inner = cq.Workplane("XY").circle(f.BRG_IR_OD / 2).circle(f.BRG_ID / 2).extrude(w)
    seal = (cq.Workplane("XY").workplane(offset=0.4).circle(33.4 / 2).circle(f.BRG_IR_OD / 2).extrude(w - 0.8))
    return outer, inner, seal


def oring():
    cs = 2.0
    r_mid = f.ORING_GROOVE_D / 2 + cs / 2 + 0.01
    return cq.Workplane("XY").add(cq.Solid.makeTorus(r_mid, cs / 2)).translate((0, 0, f.BRG_W + 0.6 + f.ORING_GROOVE_W / 2))


def magnet():
    return cq.Workplane("XY").workplane(offset=f.HUB_Z0).circle(3.0).extrude(2.5)


def screws():
    import math
    pts = [cq.Vector(9.5 * math.cos(math.radians(90 + k * 120)), 9.5 * math.sin(math.radians(90 + k * 120)), 0) for k in range(3)]
    s = None
    for p in pts:
        head = cq.Workplane("XY").workplane(offset=f.HUB_Z0 - f.WASHER_T - 1.3).center(p.x, p.y).circle(2.35).extrude(1.3)
        shank = cq.Workplane("XY").workplane(offset=f.HUB_Z0 - f.WASHER_T).center(p.x, p.y).circle(1.0).extrude(6 - 0.01)
        part = head.union(shank)
        s = part if s is None else s.union(part)
    return s


def build():
    o, i, seal = bearing_6805()
    asm = cq.Assembly(name="RD160_Drehknopf")
    asm.add(f.make_knob_shell(), name="Becher_Alu", color=cq.Color(0.08, 0.08, 0.09))
    asm.add(f.make_light_tube(), name="Lichtleiter_PMMA", color=cq.Color(0.92, 0.95, 1.0, 0.7))
    asm.add(f.make_cone_insert(), name="Konuseinsatz_Alu", color=cq.Color(0.55, 0.56, 0.58))
    asm.add(f.make_washer().translate((0, 0, f.HUB_Z0 - f.WASHER_T)), name="Haltescheibe", color=cq.Color(0.6, 0.6, 0.62))
    asm.add(screws(), name="ISO7380_M2.5x6_3x", color=cq.Color(0.3, 0.3, 0.3))
    asm.add(o, name="6805-2RS_Aussenring", color=cq.Color(0.75, 0.75, 0.78))
    asm.add(i, name="6805-2RS_Innenring", color=cq.Color(0.75, 0.75, 0.78))
    asm.add(seal, name="6805-2RS_Dichtung", color=cq.Color(0.2, 0.2, 0.25))
    asm.add(oring(), name="O-Ring_26x2", color=cq.Color(0.1, 0.1, 0.1))
    asm.add(magnet(), name="Diametralmagnet_6x2.5", color=cq.Color(0.7, 0.15, 0.15))
    asm.add(f.make_knob_pcb(), name="Knopfplatine", color=cq.Color(0.1, 0.35, 0.6))
    cols = {"AS5600_SOIC8": (0.1, 0.1, 0.1), "LED_3528_12x": (1.0, 0.97, 0.8), "Taster_B3F-1000": (0.2, 0.2, 0.2),
            "Stecker_JST-PH_7p_hinten": (0.95, 0.95, 0.9), "Abstandsbolzen_M3x4_4x": (0.8, 0.7, 0.3),
            "Schrauben_M3x8_4x": (0.3, 0.3, 0.3)}
    for n, wp in f.make_pcb_parts().items():
        asm.add(wp, name=n, color=cq.Color(*cols[n]))
    return asm


if __name__ == "__main__":
    asm = build()
    asm.save(os.path.join(OUT, "RD160_Drehknopf_Baugruppe.step"))
    # Kollisionsprüfung (Schraubenschaft als Kernloch-Ø modelliert)
    parts = {c.name: c.obj for c in asm.children}
    ks = list(parts)
    hit = False
    for a in range(len(ks)):
        for b in range(a + 1, len(ks)):
            try:
                v = parts[ks[a]].intersect(parts[ks[b]]).val().Volume()
            except Exception:
                v = 0
            if v > 0.01:
                hit = True; print("INTERFERENZ", ks[a], ks[b], round(v, 3))
    print("Teile:", len(ks), "| Kollisionen:", "ja" if hit else "keine")
    # Ansichten: Halbschnitt iso + Front
    comp = cq.Workplane("XY")
    for c in asm.children:
        comp = comp.add(c.obj.vals() if hasattr(c.obj, "vals") else c.obj)
    whole = cq.Workplane("XY").add(cq.Compound.makeCompound([v for c in asm.children for v in c.obj.vals()]))
    half = whole.cut(cq.Workplane("XY").box(100, 60, 100, centered=(True, False, True)))
    cq.exporters.export(half, "/tmp/knob_half.svg",
                        opt={"width": 900, "height": 700, "projectionDir": (-0.9, 1.6, 0.7), "showHidden": False, "strokeWidth": 0.25})
    cq.exporters.export(whole, "/tmp/knob_iso.svg",
                        opt={"width": 900, "height": 700, "projectionDir": (-1.0, -1.2, 1.4), "showHidden": False, "strokeWidth": 0.25})
