"""Gesamtbaugruppe Gehäuse: Front (Blende, Träger, Platte, Knopf, Kappen), Gehäuse (Deckel, Boden, Seitenteile, Rückwand,
Querleisten, Füße), Verbindungselemente, Rückwandbuchsen (Platzhalter). STEP mit Unterbaugruppen + Ansichten + Stückliste.
Innenleben: RD160_Platzplan.step (platzplan.py) dazuladen."""
import os, csv, subprocess
import cadquery as cq
import frontplatte as f

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
C = lambda r, g, b: cq.Color(r, g, b)
ALU_S, ALU_G, ALU_H, STAHL = C(0.12, 0.12, 0.13), C(0.45, 0.46, 0.48), C(0.75, 0.76, 0.78), C(0.25, 0.25, 0.27)

# ---------------- Füße (Annahme nach Fotos: Ø46 × 9,5, x ±165, 45 mm von vorn/hinten) ----------------
FOOT_D, FOOT_H, FOOT_X, FOOT_IN = 46.0, 9.5, 165.0, 45.0


def foot_points():
    return [(sx * FOOT_X, z) for sx in (1, -1) for z in (f.FL_Z0 - FOOT_IN, f.Z_REAR + FOOT_IN)]


def make_foot():
    ft = cq.Workplane("XZ").circle(FOOT_D / 2).extrude(FOOT_H)            # XZ-Ebene, Extrusion in -Y
    return ft.edges().fillet(1.0)


# ---------------- Schrauben (vereinfacht: Kopf + Schaft Nenn-Ø) ----------------
def screw(p, d, L, dk, k, kind, axis):
    """p: Auflagepunkt Kopf (Kopfunterseite bzw. Senkfläche oben), axis: Richtung Schaft (Vector, Einheitsachse)."""
    p, a = cq.Vector(*p), cq.Vector(*axis)
    if kind == "senk":                                             # Kopf versenkt: Kegel von dk auf d über k
        head = cq.Solid.makeCone(dk / 2, d / 2, k, p, a)
        shank = cq.Solid.makeCylinder(d / 2, L - k, p + a * k, a)
    else:                                                          # Zylinder-/Linsenkopf steht vor
        head = cq.Solid.makeCylinder(dk / 2, k, p - a * k, a)
        shank = cq.Solid.makeCylinder(d / 2, L, p, a)
    return head.fuse(shank)


UP, FWD = (0, 1, 0), (0, 0, 1)
screws = {}
# Rückwand 10× ISO 10642 M3×8 axial
screws["Rueckwand_ISO10642_M3x8"] = [screw((-v, y, f.Z_REAR), 3, 8, 6.72, 1.86, "senk", FWD) for v, y in f.rear_screw_points()]
# Deckel: 2× ISO 4762 M3×10 von unten durch die Wulst, 3× durch die obere Querleiste
y_cb = f.H / 2 - f.COVER_T - f.BEAD_H + 3.0
screws["Deckel_ISO4762_M3x10"] = [screw((x, y_cb, z), 3, 10, 5.5, 3.0, "zyl", UP)
                                  for x, z in f.cover_screw_points() + f.ql_fix_points()]
# Boden: 7× ISO 7380 M3×6 von unten
screws["Boden_ISO7380_M3x6"] = [screw((x, -f.H / 2, z), 3, 6, 5.7, 1.65, "zyl", UP)
                                for x, z in f.cover_screw_points() + f.ql_fix_points() + f.bot_front_points()]
# Blende ↔ Träger: 6× M2,5×6 Senkkopf von unten
screws["Blende_M2.5x6_Senk"] = [screw((x, -f.H / 2, f.BZ_SCREW_Z), 2.5, 6, 5.0, 1.25, "senk", UP) for x in f.BZ_SCREW_X]

# ---------------- Baugruppe ----------------
front = (cq.Assembly(name="Front")
         .add(f.make_bezel(), name="Blende", color=ALU_S)
         .add(f.make_carrier(), name="Traeger", color=ALU_G)
         .add(f.make_panel(), name="Plexiglas", loc=cq.Location((0, 0, f.CARRIER_T)), color=C(0.03, 0.03, 0.03))
         .add(f.make_foam(), name="Schaumstoff", color=C(0.08, 0.08, 0.08)))
kn = (cq.Assembly(name="Drehknopf", loc=cq.Location((f.KNOB_X, 0, 0)))
      .add(f.make_knob_shell(), name="Becher", color=ALU_S)
      .add(f.make_light_tube(), name="Lichtleiter", color=C(0.95, 0.95, 0.95))
      .add(f.make_cone_insert(), name="Konus", color=ALU_G)
      .add(f.make_washer(), name="Haltescheibe", loc=cq.Location((0, 0, f.HUB_Z0 - f.WASHER_T)), color=ALU_H)
      .add(f.make_knob_pcb(), name="Knopfplatine", color=C(0.1, 0.35, 0.15)))
front.add(kn)
cap = f.make_button_cap()
z_cap = f.BTN_CB_DEPTH - 5.7                                       # Bund liegt am Senkungsboden
for i in range(5):
    for j, yy in enumerate(f.BTN_ROWS_Y):
        front.add(cap, name=f"Tasterkappe_{j * 5 + i + 1}", loc=cq.Location((f.BTN_X0 + i * f.BTN_PITCH_X, yy, z_cap)), color=ALU_H)
front.add(f.make_power_cap(), name="Einschaltkappe", loc=cq.Location((f.PWR_X, f.PWR_Y, f.PCB_Z + f.SW_H - 0.1)), color=ALU_H)
front.add(f.make_tab_screws(), name="Laschenschrauben_ISO10642_M3x8", color=STAHL)

geh = (cq.Assembly(name="Gehaeuse")
       .add(f.make_cover(), name="Deckel", color=ALU_H)
       .add(f.make_bottom(), name="Bodenblech", color=C(0.2, 0.2, 0.21))
       .add(f.make_side_panel(1), name="Seitenteil_rechts", color=ALU_S)
       .add(f.make_side_panel(-1), name="Seitenteil_links", color=ALU_S)
       .add(f.make_rear_panel(), name="Rueckwand", color=ALU_S)
       .add(f.make_crossbar(True), name="Querleiste_oben", color=ALU_G)
       .add(f.make_crossbar(False), name="Querleiste_unten", color=ALU_G))
foot = make_foot()
for i, (x, z) in enumerate(foot_points(), 1):
    geh.add(foot, name=f"Fuss_{i}", loc=cq.Location((x, -f.H / 2, z)), color=ALU_H)

vb = cq.Assembly(name="Verbindungselemente")
for nm, lst in screws.items():
    vb.add(cq.Workplane("XY").add(cq.Compound.makeCompound(lst)), name=nm, color=STAHL)

bu = cq.Assembly(name="Rueckwand_Buchsen_Platzhalter")
for k, b in f.make_rear_connectors().items():
    bu.add(b, name=k, color=C(0.85, 0.7, 0.3))

asm = cq.Assembly(name="RD160_Gehaeuse").add(front).add(geh).add(vb).add(bu)
asm.save(f"{OUT}/RD160_Gehaeuse_Baugruppe.step")

# ---------------- Prüfung: Hauptteile untereinander ----------------
main = {"Blende": f.make_bezel(), "Traeger": f.make_carrier(), "Platte": f.make_panel().translate((0, 0, f.CARRIER_T)),
        "Deckel": f.make_cover(), "Boden": f.make_bottom(), "SR": f.make_side_panel(1), "SL": f.make_side_panel(-1),
        "Rueckwand": f.make_rear_panel(), "QL_o": f.make_crossbar(True), "QL_u": f.make_crossbar(False)}
for i, (x, z) in enumerate(foot_points(), 1):
    main[f"Fuss_{i}"] = foot.translate((x, -f.H / 2, z))
for k, b in f.make_rear_connectors().items():
    main["Buchse_" + k] = b
ks, hits = list(main), []
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        if ks[i].startswith("Buchse_") and ks[j].startswith("Buchse_"):
            continue
        v = main[ks[i]].intersect(main[ks[j]]).val().Volume()
        if v > 1e-3:
            hits.append((ks[i], ks[j], round(v, 2)))
print("Kollisionen Gesamtbaugruppe:", hits or "keine")

# ---------------- Stückliste ----------------
rows = [("Blende", 1, "EN AW-6061, schwarz eloxiert", "RD160_Front_Blende.step"),
        ("Träger", 1, "EN AW-6061, schwarz eloxiert", "RD160_Front_Traeger.step"),
        ("Plexiglasplatte", 1, "PLEXIGLAS LED B&W 9H04 SC / 7H25 GT, 3 mm", "RD160_Front_Plexiglas.step/.dxf"),
        ("Schaumstoff Deckelauflage", 1, "PE/EPDM 2 mm", "-"),
        ("Drehknopf (Becher, Lichtleiter, Konus, Haltescheibe)", 1, "Alu / PMMA", "RD160_Knopf_*.step"),
        ("Knopfplatine", 1, "FR4 (Eigenbau)", "knopfplatine_schaltplan.py"),
        ("Tasterkappe", 10, "Alu, eloxiert", "RD160_Tasterkappe.step"),
        ("Einschaltkappe", 1, "Alu, eloxiert", "RD160_Einschaltkappe.step"),
        ("Deckel", 1, "EN AW-6061, 5 mm", "RD160_Deckel.step"),
        ("Bodenblech", 1, "EN AW-5754, 1 mm", "RD160_Bodenplatte.step"),
        ("Seitenteil rechts/links", 2, "EN AW-6061, schwarz eloxiert", "RD160_Seitenteil_*.step"),
        ("Rückwand", 1, "EN AW-6061, 4 mm, schwarz eloxiert, Gravur", "RD160_Rueckwand.step/.dxf"),
        ("Querleiste oben/unten", 2, "Alu-Flachstange 10×10", "RD160_Querleiste_*.step"),
        ("Fuß Ø46 × 9,5 (Annahme)", 4, "Alu, Befestigung offen", "-"),
        ("ISO 10642 M3×8 (Laschen)", 4, "Stahl schwarz", "-"),
        ("ISO 10642 M3×8 (Rückwand)", len(screws["Rueckwand_ISO10642_M3x8"]), "Stahl schwarz", "-"),
        ("ISO 4762 M3×10 (Deckel)", len(screws["Deckel_ISO4762_M3x10"]), "Stahl", "-"),
        ("ISO 7380 M3×6 (Boden)", len(screws["Boden_ISO7380_M3x6"]), "Stahl schwarz", "-"),
        ("M2,5×6 Senkkopf (Blende)", len(screws["Blende_M2.5x6_Senk"]), "Stahl schwarz", "-"),
        ("Einbaubuchsen Rückwand", len(f.RP_CONN), "siehe RD160_Rueckwand_Buchsen.csv", "-")]
with open(f"{OUT}/RD160_Gehaeuse_Stueckliste.csv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["Teil", "Anzahl", "Material/Ausführung", "Datei"])
    w.writerows(rows)

# ---------------- Ansichten (Rx(90) auf dem Compound, PNG drehen: vorn +90, hinten −90) ----------------
def flat(a):
    vals = []
    for name, sub in a.traverse():
        if sub.obj is not None:
            loc = sub.loc
            par = sub.parent
            while par is not None:
                loc = par.loc * loc
                par = par.parent
            for v in (sub.obj.vals() if hasattr(sub.obj, "vals") else [sub.obj]):
                vals.append(v.moved(loc))
    return vals


comp = cq.Compound.makeCompound(flat(cq.Assembly().add(front).add(geh).add(bu))).rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)
for nm, pdir, rot in (("vorn", (0.55, -1.0, 0.55), "90"), ("hinten", (-0.55, 1.0, 0.55), "-90")):
    svg = f"/tmp/geh_{nm}.svg"
    cq.exporters.export(cq.Workplane("XY").add(comp), svg, opt={"width": 1600, "height": 1000, "projectionDir": pdir,
                                                              "showHidden": False, "strokeWidth": 0.3})
    subprocess.run(["rsvg-convert", "-b", "white", svg, "-o", f"/tmp/geh_{nm}.png"], check=True)
    subprocess.run(["convert", f"/tmp/geh_{nm}.png", "-trim", "-rotate", rot, "-bordercolor", "white", "-border", "20",
                    f"{OUT}/RD160_Gehaeuse_Baugruppe_{nm}.png"], check=True)
print("ok")
