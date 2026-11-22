"""
RD160-Nachbau – Front: Alu-Rahmen/Träger + vollflächige Plexiglas-Front, Tasterkappe
Parametrisch (CadQuery). Koordinaten: Ursprung Plattenmitte, X rechts, Y oben,
Z: Rückseite = 0, Front = T.  Alle Maße in mm.

Aufbau: Ein Alu-Teil (Rahmen + Träger). Vorn eine Tasche, die die ganze Front bis auf
einen schmalen Rand ausfüllt; darin liegt eine 3-mm-PLEXIGLAS-LED-Black-&-White-Platte.
Display, Taster und LED-Ring sitzen im Träger dahinter.

Display: 2x DFRobot DFR0524 5,5" AMOLED 1080x1920 (HDMI), quer nebeneinander,
         Outline je 124 x 71, aktiv je 121,42 x 68,3.
"""
import cadquery as cq

# ---------------- Rahmen / Träger ----------------
W, H, T = 430.0, 88.0, 12.0           # Außenmaß, Gesamtdicke
FRAME_B = 4.0                         # sichtbarer Alu-Rand
FRAME_R = 2.0                         # Innenradius Fronttasche
EDGE_CHAMFER = 0.5

# ---------------- Ober-/Unterkante wie RD160 (Draufsicht-Foto + Kommentare H. Simon) ----------------
# Oben und unten läuft ein Flansch nach hinten (Gesamttiefe DEPTH = Band + Auflage). An beiden Enden Seitenwände
# END_W breit, volle Höhe, volle Tiefe. OBEN: keine Lippe; Nut in der Rückseite des Bands (Scheibenfräser), darin die
# einseitige Feder des Deckels. Hinter dem Band Auflage SEAT_D tief mit Schaumstoff: drückt den Deckel hoch, Feder
# liegt oben in der Nut an -> Deckel vorn gehalten, ohne Schrauben. Deckeloberseite bündig. UNTEN: Auflage BOT_T tief (Bodenblech).
# Seitenteile L-förmig (Falz oben innen), Deckel mit L-förmigen Rändern als Gegenstück -> Deckel seitlich geführt,
# liegt auf den Seitenteilen; vorn auf Schaumstoff und Laschen.
FL_H = 9.0                            # Flanschhöhe (nach innen)
BAND = 10.0                           # vorderes Band, volle Höhe
END_W = 11.0                          # Seitenwand der Front (in X)
COVER_T = 5.0                         # Deckeldicke (Rückseitenfoto: ca. 5 mm)
SEAT_L = 9.0                          # Auflage hinter dem Band (Draufsicht: Band+Auflage 19-20 mm)
DEPTH = BAND + SEAT_L                 # Gesamttiefe 19 mm
FOAM_T, FOAM_C = 2.0, 1.5             # Schaumstoff: frei / eingebaut (25 % gepresst)
SEAT_D = COVER_T + FOAM_C             # Auflage unter Oberkante = 6,5
GROOVE_TOP = 2.0                      # Steg über der Nut (= Absatz der Feder oben)
TONGUE_T = COVER_T - GROOVE_TOP       # Feder am Deckel, oben abgesetzt = 3,0
GROOVE_H = TONGUE_T + 0.3             # Nuthöhe (0,3 Luft unten, Schaum drückt Feder nach oben)
GROOVE_D = 4.0                        # Nuttiefe ins Band (Restband vorn 6 mm)
TONGUE_L = GROOVE_D - 0.3             # Federlänge (Deckelstirn 0,3 vor dem Band)
CUTTER_R = 10.0                       # Scheibenfräser Ø20: Auslauf an den Nutenden
SEAT_R = 3.0                          # senkrechte Innenecken Auflage/Seitenwand (Fräser Ø6), Foto
DECO_W, DECO_D = 0.6, 0.15            # Ziernut im Deckel: Breite, Tiefe (Foto); Lage siehe deco_rect()
BOT_T = 1.0                           # Bodenblech 1 mm (Auflage unten in der Front gleich tief)
# Seitenteile (Detailfoto Innenecke): C-Profil = Wand SIDE_T + innen oben/unten Wulst BEAD_W x BEAD_H, Höhe
# zwischen Deckel und Boden. Deckel (5 mm) und Bodenblech (1 mm) sind ebene Platten über die volle Breite W,
# liegen auf Wand und Wulst und decken die Seitenteile oben/unten ab (außen bündig). Front <-> Seitenteil: waagerechte Lasche (oben/unten) liegt in einem Absatz der
# Wulst am vorderen Profilende, oberseitig bündig mit der Wulst; M3-Senkschraube SENKRECHT durch die Lasche in die
# Wulst (wie Original: Schraube 9 mm vom Rand, ca. 27 mm hinter der Front). Deckel deckt die Schraube ab.
SIDE_T = 5.0                          # Wand Seitenteil
BEAD_W, BEAD_H = 9.0, 10.0            # Wulst innen (X, Y) -> Profil oben/unten 14 mm breit
SIDE_W = SIDE_T + BEAD_W
LAP_GAP = 0.1                         # Spiel Deckel/Boden/Lasche zur Wand
TAB_U0, TAB_W = SIDE_T + LAP_GAP, BEAD_W - 2 * LAP_GAP   # Lasche über der Wulst: 5,1..13,9 mm vom Außenrand
TAB_T = 3.0                           # Laschendicke (Y) = Absatztiefe in der Wulst
TAB_L = 12.0                          # Laschenlänge nach hinten ab Flanschende (Ende 31 mm hinter Front, Foto ca. 30)
TAB_SCREW_U = TAB_U0 + TAB_W / 2      # 8,5 mm vom Außenrand
TAB_SCREW_Z = T - 26.0                # 26 mm hinter der Frontfläche (Foto: 26-28 mm)
SCREW_LEN = 8                         # ISO 10642 M3x8 (Lasche 3 + Gewinde 5)
FL_Z0 = T - DEPTH                     # Z der Flanschrückseite

# ---------------- Frontplatte (Plexiglas) ----------------
PANEL_T = 3.0                         # PLEXIGLAS LED B&W 9H04 SC / 7H25 GT
PANEL_GAP = 0.3                       # Spiel je Seite (Wärmedehnung PMMA!)
CARRIER_T = T - PANEL_T               # Trägerdicke = 9
POCKET_W, POCKET_H = W - 2 * FRAME_B, H - 2 * FRAME_B
PANEL_W, PANEL_H = POCKET_W - 2 * PANEL_GAP, POCKET_H - 2 * PANEL_GAP

# ---------------- Display ----------------
DISP_W, DISP_H = 2 * 124.0, 71.0      # 2x DFR0524 Outline, Stoß bei X=0
DISP_CLR = 0.5
DISP_X = 0.0
PNL_W = DISP_W + 2 * DISP_CLR
PNL_H = DISP_H + 2 * DISP_CLR
PNL_DEPTH = CARRIER_T                 # von hinten bis an die Plexiglasplatte

# ---------------- Taster (2 x 5) ----------------
BTN_X0, BTN_PITCH_X = -198.0, 13.0
BTN_ROWS_Y = (11.0, -11.0)
BTN_HOLE_D = 6.2                      # Kappe Ø6, Träger
BTN_PANEL_D = 6.6                     # Bohrung in Plexiglas
BTN_CB_D, BTN_CB_DEPTH = 9.0, 5.0     # Bund-Senkung von hinten

def btn_positions():
    return [(BTN_X0 + i * BTN_PITCH_X, y) for y in BTN_ROWS_Y for i in range(5)]

# ---------------- Drehknopf / LED-Ring ----------------
KNOB_X = 166.0
RING_ID, RING_OD = 41.0, 46.0         # Lichtkanal vorn (durchgehend) unter den Knopf-Lichtfenstern
RING_FRONT_DEPTH = 5.0                # ab Trägerfront
LIGHT_ID, LIGHT_OD = 41.0, 47.0       # Lichttasche hinten mit Stegen
LIGHT_DEPTH = CARRIER_T - RING_FRONT_DEPTH
BRIDGE_W = 5.0
BEARING_D, BEARING_DEPTH = 37.0, 7.0  # 6805-2RS, Ø37 H7 von hinten
SHAFT_HOLE_D = 30.0                   # Bund Ø28 + O-Ring 26x2 (Laufbohrung)
SHAFT_PANEL_D = 51.0                  # Knopfboden sitzt in der Platte

# ---------------- Einschalttaster ----------------
PWR_X, PWR_Y = 196.0, 27.0
PWR_D, PWR_HOLE_D, PWR_PANEL_D = 12.0, 12.2, 12.6
PWR_CB_D, PWR_CB_DEPTH = 16.0, 5.0

# ---------------- Gewinde M3 (Sackloch von hinten) ----------------
M3_TAP_D, M3_DRILL_DEPTH, M3_THREAD_DEPTH = 2.5, 7.0, 6.0
M3_HOLES = {
    "Chassis":       [(-128, 0), (128, 0)],
    "Taster-PCB":    [(x, sy * 31) for x in (-191, -153) for sy in (-1, 1)],   # y31: Abstandsbolzen frei vom Flansch (y35)
    "LED/Encoder-PCB": [(KNOB_X - 30, 24), (KNOB_X - 30, -24), (KNOB_X + 22, -30), (KNOB_X + 6, 31)],
    "Panel-Klemmrahmen": [(sx * 127, sy * 25) for sx in (-1, 1) for sy in (-1, 1)],
}


def rrect(w, h, r):
    return cq.Sketch().rect(w, h).vertices().fillet(r)


def make_frame():
    p = cq.Workplane("XY").box(W, H, T, centered=(True, True, False))
    p = p.faces(">Z").edges().chamfer(EDGE_CHAMFER)

    # Ober-/Unterkante: Flansch nach hinten, Lippe + Schlitz (oben) bzw. Auflage (unten), Eckschrauben
    zb = T - BAND                                  # Rückseite Band
    ix = W / 2 - END_W
    for sy, seat in ((1, SEAT_D), (-1, BOT_T)):
        p = p.union(cq.Workplane("XY").box(W, FL_H, -FL_Z0, centered=(True, True, False))
                    .translate((0, sy * (H / 2 - FL_H / 2), FL_Z0)))
        # Auflage hinter dem Band: oben Deckel + Schaumstoff, unten Bodenplatte
        p = p.cut(cq.Workplane("XY").box(2 * ix, seat + 0.01, zb - FL_Z0 + 0.01, centered=(True, True, False))
                  .translate((0, sy * (H / 2 - seat / 2 + 0.005), FL_Z0 - 0.01)))
    # Nut für die Deckelfeder in der Bandrückseite (zwischen den Seitenwänden, Enden mit Fräserauslauf R)
    import math
    run = math.sqrt(CUTTER_R ** 2 - (CUTTER_R - GROOVE_D) ** 2)  # Auslauflänge an der Rückseite
    g = (cq.Workplane("XZ").workplane(offset=-(H / 2 - GROOVE_TOP))   # Ebene y = H/2 - GROOVE_TOP, Normale -Y
         .center(0, zb).rect(2 * (ix - run), 2 * GROOVE_D).extrude(GROOVE_H))
    for sx in (1, -1):
        g = g.union(cq.Workplane("XY").add(cq.Solid.makeCylinder(
            CUTTER_R, GROOVE_H, cq.Vector(sx * (ix - run), H / 2 - GROOVE_TOP - GROOVE_H, zb + GROOVE_D - CUTTER_R),
            cq.Vector(0, 1, 0))))
    p = p.cut(g.intersect(cq.Workplane("XY").box(2 * ix, H, zb + GROOVE_D - FL_Z0 + 1, centered=(True, True, False))
                          .translate((0, 0, FL_Z0 - 1))))

    # Innenecken der Auflage (Band-Rückseite / Seitenwand) senkrecht ausgerundet SEAT_R (Fräserradius, wie Original)
    for sy, seat in ((1, SEAT_D), (-1, BOT_T)):
        for sx in (1, -1):
            blk = (cq.Workplane("XY").box(SEAT_R, seat, SEAT_R, centered=(False, True, False))
                   .translate((sx * ix - (SEAT_R if sx > 0 else 0), sy * (H / 2 - seat / 2), zb - SEAT_R)))
            cyl = cq.Solid.makeCylinder(SEAT_R, seat + 0.2, cq.Vector(sx * (ix - SEAT_R), sy * (H / 2 + 0.1), zb - SEAT_R),
                                        cq.Vector(0, -sy, 0))
            p = p.union(blk.cut(cq.Workplane("XY").add(cyl)))

    # Seitenwände: volle Höhe, volle Tiefe (Front umgreift die Ecke wie beim Original)
    for sx in (1, -1):
        p = p.union(cq.Workplane("XY").box(END_W, H, -FL_Z0, centered=(True, True, False))
                    .translate((sx * (W / 2 - END_W / 2), 0, FL_Z0)))

    # Laschen waagerecht oben/unten, liegen im Absatz der Seitenteil-Wulst; Senkbohrung M3 von außen (Deckel-/Bodenseite)
    for sx in (1, -1):
        xc = sx * (W / 2 - TAB_U0 - TAB_W / 2)
        for sy in (1, -1):
            yf = sy * (H / 2 - (COVER_T if sy > 0 else BOT_T))      # Außenfläche Lasche = Deckel-/Bodenunterseite
            p = p.union(cq.Workplane("XY").box(TAB_W, TAB_T, TAB_L + 0.01, centered=(True, True, False))
                        .edges("|Y and <Z").fillet(1.5)
                        .translate((xc, yf - sy * TAB_T / 2, FL_Z0 - TAB_L)))
            xs = sx * (W / 2 - TAB_SCREW_U)
            p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.7, TAB_T + 0.2, cq.Vector(xs, yf + sy * 0.1, TAB_SCREW_Z),
                                                                   cq.Vector(0, -sy, 0))))
            p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCone(3.3, 1.5, 1.8, cq.Vector(xs, yf + sy * 0.01, TAB_SCREW_Z),
                                                               cq.Vector(0, -sy, 0))))

    # Fronttasche für vollflächige Plexiglasplatte
    p = p.cut(cq.Workplane("XY").workplane(offset=CARRIER_T)
              .placeSketch(rrect(POCKET_W, POCKET_H, FRAME_R)).extrude(PANEL_T + 1))

    # Displaytasche von hinten, durch den Träger bis an die Platte, mit Eckfreistichen
    cut = cq.Workplane("XY").center(DISP_X, 0).rect(PNL_W, PNL_H).extrude(PNL_DEPTH)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cut = cut.union(cq.Workplane("XY")
                            .center(DISP_X + sx * (PNL_W / 2 - 0.6), sy * (PNL_H / 2 - 0.6))
                            .circle(2.0).extrude(PNL_DEPTH))
    p = p.cut(cut)

    # Taster
    pts = btn_positions()
    p = p.cut(cq.Workplane("XY").pushPoints(pts).circle(BTN_HOLE_D / 2).extrude(T + 1))
    p = p.cut(cq.Workplane("XY").pushPoints(pts).circle(BTN_CB_D / 2).extrude(BTN_CB_DEPTH))


    # Einschalttaster
    p = p.cut(cq.Workplane("XY").center(PWR_X, PWR_Y).circle(PWR_HOLE_D / 2).extrude(T + 1))
    p = p.cut(cq.Workplane("XY").center(PWR_X, PWR_Y).circle(PWR_CB_D / 2).extrude(PWR_CB_DEPTH))

    # Lichtkanal vorn (durchgehender Ring bis an die Platte)
    p = p.cut(cq.Workplane("XY").workplane(offset=CARRIER_T - RING_FRONT_DEPTH).center(KNOB_X, 0)
              .circle(RING_OD / 2).circle(RING_ID / 2).extrude(RING_FRONT_DEPTH + 0.01))
    # Lichttasche hinten mit 4 Stegen
    ring = (cq.Workplane("XY").center(KNOB_X, 0)
            .circle(LIGHT_OD / 2).circle(LIGHT_ID / 2).extrude(LIGHT_DEPTH))
    for a in (45, 135):
        bar = (cq.Workplane("XY").center(KNOB_X, 0)
               .rect(LIGHT_OD + 4, BRIDGE_W).extrude(LIGHT_DEPTH)
               .rotate((KNOB_X, 0, 0), (KNOB_X, 0, 1), a))
        ring = ring.cut(bar)
    p = p.cut(ring)
    # Lagersitz + Wellenbohrung
    if BEARING_DEPTH > 0:
        p = p.cut(cq.Workplane("XY").center(KNOB_X, 0).circle(BEARING_D / 2).extrude(BEARING_DEPTH))
    p = p.cut(cq.Workplane("XY").center(KNOB_X, 0).circle(SHAFT_HOLE_D / 2).extrude(T + 1))

    # M3-Kernlöcher
    allm3 = [pt for v in M3_HOLES.values() for pt in v]
    p = p.cut(cq.Workplane("XY").pushPoints(allm3).circle(M3_TAP_D / 2).extrude(M3_DRILL_DEPTH))
    return p


def make_panel():
    p = cq.Workplane("XY").placeSketch(rrect(PANEL_W, PANEL_H, FRAME_R + PANEL_GAP)).extrude(PANEL_T)
    p = p.cut(cq.Workplane("XY").pushPoints(btn_positions()).circle(BTN_PANEL_D / 2).extrude(PANEL_T))
    p = p.cut(cq.Workplane("XY").center(KNOB_X, 0).circle(SHAFT_PANEL_D / 2).extrude(PANEL_T))
    p = p.cut(cq.Workplane("XY").center(PWR_X, PWR_Y).circle(PWR_PANEL_D / 2).extrude(PANEL_T))
    return p


def make_button_cap():
    # Stößel Ø3 x 4,2 | Bund Ø8,6 x 1,5 | Schaft Ø6: 4 Träger + 3 Platte + 1,5 Überstand
    stem = cq.Workplane("XY").circle(1.5).extrude(4.2)
    collar = cq.Workplane("XY").workplane(offset=4.2).circle(4.3).extrude(1.5)
    shaft_len = (T - BTN_CB_DEPTH) + 1.5
    shaft = (cq.Workplane("XY").workplane(offset=5.7).circle(3.0).extrude(shaft_len)
             .faces(">Z").edges().fillet(0.5))
    return stem.union(collar).union(shaft)


# ---------------- Drehknopf-Baugruppe (kompakt, wie RD160) ----------------
# Becher mit angedrehter Nabe läuft in EINEM Dünnringlager 6805-2RS (25x37x7) direkt im Träger.
# Keine Welle, kein Lagerblock. Diametralmagnet in der Nabenstirn, AS5600 + 12 LEDs auf EINER
# kleinen Platine direkt hinter dem Rahmen (wie die Platine im RD160-Innenfoto).
KNOB_D, KNOB_PROT = 50.0, 12.0                   # Überstand aus Draufsicht-Foto: ca. 11,5 mm
KNOB_Z0 = CARRIER_T + 0.5
FLOOR_TOP = T
KNOB_Z1 = T + KNOB_PROT
SHELL_ID = 45.2
TUBE_OD, TUBE_ID = 45.0, 41.6
INS_OD, CONE_LIP_ID, CONE_FLOOR_D = 41.5, 40.0, 24.0
WIN_N, WIN_D = 12, 2.5
WIN_PCD = (TUBE_OD + TUBE_ID) / 2
BRG_ID, BRG_OD, BRG_W = 25.0, 37.0, 7.0          # 6805-2RS
BRG_IR_OD = 28.6                                 # Innenring-Schulter max.
COLLAR_D = 28.0                                  # Nabenbund (drückt auf Innenring)
ORING_GROOVE_D, ORING_GROOVE_W = 26.2, 2.1       # O-Ring 26x2 als Dämpfung (Nyogel 767A)
HUB_Z0 = 0.0                                     # Nabenende = Lagerrückseite, Haltescheibe dahinter
WASHER_D, WASHER_T = 28.0, 1.5                   # Haltescheibe 3x M2,5 auf Nabenstirn
MAGNET_D, MAGNET_H = 6.1, 2.6                    # Diametralmagnet 6x2,5
PCB_Z = -4.0                                     # Vorderseite Knopfplatine (Abstandsbolzen 4 mm)


def make_foam():
    """Schaumstoffstreifen oben auf der Auflage hinter dem Band (eingebaut 1,5 mm)."""
    zb = T - BAND
    L = 2 * (W / 2 - END_W - SEAT_R) - 1.0
    return (cq.Workplane("XY").box(L, FOAM_C, zb - 0.5 - FL_Z0 - 0.1, centered=(True, True, False))
            .translate((0, H / 2 - SEAT_D + FOAM_C / 2, FL_Z0 + 0.1)))


def _plate(top, length, tongue):
    """Deckel (top=True) bzw. Bodenplatte, eben: vorn zwischen den Seitenwänden der Front bis ans Band,
    dahinter volle Breite über die Seitenteile; Deckel mit Feder."""
    import math
    sy = 1 if top else -1
    t = COVER_T if top else BOT_T
    zb = T - BAND
    yc = sy * (H / 2 - t / 2)
    wf = 2 * (W / 2 - END_W) - 1.0
    wb = W                                     # ebene Platte über die Seitenwände, außen bündig
    z_end = FL_Z0 - 0.3
    front = (cq.Workplane("XY").box(wf, t, zb - 0.3 - FL_Z0 + 0.31, centered=(True, True, False))
             .translate((0, yc, FL_Z0 - 0.31)))
    front = front.edges("|Y and >Z").fillet(SEAT_R + 0.5)       # passt in die ausgerundeten Innenecken
    body = (cq.Workplane("XY").box(wb, t, length, centered=(True, True, False)).translate((0, yc, z_end - length)))
    p = front.union(body)
    if tongue:
        run = math.sqrt(CUTTER_R ** 2 - (CUTTER_R - GROOVE_D) ** 2)
        wt = 2 * (W / 2 - END_W - run - 1.0)
        p = p.union(cq.Workplane("XY").box(wt, TONGUE_T, TONGUE_L + 0.01, centered=(True, True, False))
                    .translate((0, H / 2 - GROOVE_TOP - TONGUE_T / 2, zb - 0.3 - 0.01)))
    return p


def make_cover_edge(length=60.0):
    """Vorderer Deckelausschnitt (Darstellung/Prüfung)."""
    return _plate(True, length, True)


# ---------------- Gehäuse hinten ----------------
DEV_D = 327.0                          # Gerätetiefe ohne Knopf (Datenblatt 430 x 327 x 87)
Z_REAR = T - DEV_D                     # Z der Geräterückseite
RP_T = 4.0                             # Rückwand zwischen den Seitenteil-Wänden; Wulste enden davor
COVER_SCREW_U = SIDE_T + BEAD_W / 2    # 9,5 vom Rand (Mitte Wulst): Deckel von unten verschraubt, Boden von unten
COVER_THREAD = 3.0                     # Sackgewinde M3 in der Deckelunterseite (2 mm Restwand, oben unsichtbar)
REAR_SCREW_U = SIDE_T + BEAD_W / 2     # Rückwandschrauben axial, Mitte Wulst 9,5
COVER_SCREW_Z = Z_REAR + RP_T + 12.0   # frei von den axialen Rückwandgewinden (7 tief)
REAR_SCREW_Y = H / 2 - COVER_T - BEAD_H / 2   # Rückwandschrauben axial in die Wulst (Foto Rückseite: an den Ecken)


def cover_screw_points():
    return [(sx * (W / 2 - COVER_SCREW_U), COVER_SCREW_Z) for sx in (1, -1)]


def _csk_holes(p, pts_xz, y_face, sy):
    for x, z in pts_xz:
        p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.7, 10, cq.Vector(x, y_face + sy * 0.1, z), cq.Vector(0, -sy, 0))))
        p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCone(3.3, 1.5, 1.8, cq.Vector(x, y_face + sy * 0.01, z), cq.Vector(0, -sy, 0))))
    return p


def cover_outline():
    """Deckel-Draufsicht (X, Z) ohne Feder: vorn zwischen den Seitenwänden der Front, dahinter volle Breite."""
    zf, z1, wf = T - BAND - 0.3, FL_Z0 - 0.3, W / 2 - END_W - 0.5
    return [(-wf, zf), (wf, zf), (wf, z1), (W / 2, z1), (W / 2, Z_REAR), (-W / 2, Z_REAR), (-W / 2, z1), (-wf, z1)]


def deco_rect():
    """Mittellinie der Ziernut, Rechteck mit rechten Winkeln (Foto): vorn direkt am Stoß Deckel/Front (offen zur
    Deckelstirn), seitlich in Flucht der Innenkante der Front-Seitenwände, nach hinten auslaufend (keine Querlinie)."""
    zf = T - BAND - 0.3
    u = END_W + 0.5 + DECO_W / 2                  # 11,8 mm von der Außenkante
    return (-(W / 2 - u), W / 2 - u, Z_REAR + u, zf - DECO_W / 2)


def make_deco_groove():
    """Ziernut DECO_W breit, DECO_D tief, als Rechteckrahmen mit scharfen Ecken."""
    x0, x1, z0, z1 = deco_rect()
    h = DECO_W / 2
    def box(xa, xb, za, zb_):
        return (cq.Workplane("XY").box(xb - xa, DECO_D + 0.01, zb_ - za, centered=False)
                .translate((xa, H / 2 - DECO_D, za)))
    zr = Z_REAR - 1.0                              # hinten keine Querlinie: Seitenlinien laufen nach hinten aus
    return box(x0 - h, x1 + h, zr, z1 + h + 1.0).cut(box(x0 + h, x1 - h, zr - 1.0, z1 - h))   # vorn zur Stirn offen


def make_cover():
    """Deckel komplett: ebene 5-mm-Platte ohne sichtbare Bohrungen. Vorn Feder in der Nut, Ziernut; hinten
    2x M3-Sackgewinde in der Unterseite: ISO 4762 M3x10 von unten durch die obere Wulst der Seitenteile."""
    c = _plate(True, FL_Z0 - 0.3 - Z_REAR, True)
    c = c.cut(make_deco_groove())
    for x, z in cover_screw_points():
        c = c.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.25, COVER_THREAD, cq.Vector(x, H / 2 - COVER_T, z),
                                                               cq.Vector(0, 1, 0))))
    return c


def make_bottom():
    """Bodenblech 1 mm: volle Breite, vorn in der Auflage der Front, hinten 2x ISO 7380 M3x6 in die Wulst."""
    b = _plate(False, FL_Z0 - 0.3 - Z_REAR, False)
    for x, z in cover_screw_points():          # 1 mm Blech: Ø3,4 für ISO 7380 M3x6 (Linsenkopf)
        b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.7, BOT_T + 0.2, cq.Vector(x, -H / 2 - 0.1, z), cq.Vector(0, 1, 0))))
    return b


RIB_N = 10                             # Rippen außen (Foto: ca. 10 über die Höhe)
RIB_GROOVE_W = 3.0                     # Nutbreite zwischen den Rippen
RIB_DEPTH = 2.5                        # Nuttiefe (Nutgrund halbrund R1,5); Restwand 2,5
RIB_CROWN = 0.6                        # Wölbung der Rippenoberfläche


def side_profile_face(sx):
    """Querschnitt Seitenteil (XY) als Face: C-Profil, außen geriffelt (RIB_N gewölbte Rippen, halbrunde Nuten)."""
    yT, yB = H / 2 - COVER_T, -H / 2 + BOT_T
    X = lambda u: sx * (W / 2 - u)
    pitch = (yT - yB) / RIB_N
    g, r = RIB_GROOVE_W, RIB_GROOVE_W / 2
    ue = RIB_CROWN                      # Rippenflanke
    uc = RIB_DEPTH - r                  # Mittelpunkt Nutgrund
    wp = cq.Workplane("XY").workplane(offset=Z_REAR).moveTo(X(0), yB)
    y = yB
    for k in range(RIB_N):
        y0 = y
        y1 = yT if k == RIB_N - 1 else yB + pitch * (k + 1) - r
        if k == 0:
            wp = wp.lineTo(X(0), y0 + (y1 - y0) / 2).threePointArc((X(ue * 0.3), y0 + (y1 - y0) * 0.8), (X(ue), y1))
        elif k == RIB_N - 1:
            wp = wp.threePointArc((X(ue * 0.3), y0 + (y1 - y0) * 0.2), (X(0), y0 + (y1 - y0) / 2)).lineTo(X(0), y1)
        else:
            wp = wp.threePointArc((X(0), (y0 + y1) / 2), (X(ue), y1))
        if k < RIB_N - 1:
            c = yB + pitch * (k + 1)
            wp = (wp.lineTo(X(uc), c - r).threePointArc((X(RIB_DEPTH), c), (X(uc), c + r)).lineTo(X(ue), c + r))
            y = c + r
    for u, yy in ((SIDE_W, yT), (SIDE_W, yT - BEAD_H), (SIDE_T, yT - BEAD_H), (SIDE_T, yB + BEAD_H),
                  (SIDE_W, yB + BEAD_H), (SIDE_W, yB)):
        wp = wp.lineTo(X(u), yy)
    wire = wp.close().wire().val()
    return cq.Face.makeFromWires(wire)


def make_side_panel(sx):
    """Seitenteil (C-Profil, Wand volle Höhe) volle Länge mit Absätzen für die Frontlaschen, Gewinden und Rückwandanschluss."""
    yT, yB = H / 2 - COVER_T, -H / 2 + BOT_T
    L = FL_Z0 - Z_REAR
    p = cq.Workplane("XY").workplane(offset=Z_REAR).add(side_profile_face(sx)).toPending().extrude(L)
    uc = W / 2 - (SIDE_T + SIDE_W) / 2
    for sy, yf in ((1, yT), (-1, yB)):
        # Absatz vorn für die Lasche
        p = p.cut(cq.Workplane("XY").box(BEAD_W + 0.02, TAB_T + 0.01, TAB_L + 0.3 + 0.01, centered=(True, True, False))
                  .translate((sx * uc, yf - sy * (TAB_T / 2 - 0.005), FL_Z0 - TAB_L - 0.3)))
        # Wulst hinten um die Rückwanddicke kürzer
        p = p.cut(cq.Workplane("XY").box(BEAD_W + 0.02, BEAD_H + 0.02, RP_T + 0.01, centered=(True, True, False))
                  .translate((sx * (W / 2 - SIDE_T - BEAD_W / 2 - 0.01), yf - sy * BEAD_H / 2, Z_REAR - 0.01)))
        # Gewinde M3: Lasche (senkrecht), Deckel/Boden (senkrecht), Rückwand (axial)
        p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.25, 6.0, cq.Vector(sx * (W / 2 - TAB_SCREW_U), yf - sy * TAB_T,
                                                                                TAB_SCREW_Z), cq.Vector(0, -sy, 0))))
        xc = sx * (W / 2 - COVER_SCREW_U)
        if sy > 0:   # Deckelschraube von unten: Ø3,4 durch die Wulst, Senkung Ø6,5 x 3 von unten
            p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.7, BEAD_H + 0.2, cq.Vector(xc, yf - BEAD_H - 0.1, COVER_SCREW_Z),
                                                                   cq.Vector(0, 1, 0))))
            p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(3.25, 3.0, cq.Vector(xc, yf - BEAD_H - 0.01, COVER_SCREW_Z),
                                                                   cq.Vector(0, 1, 0))))
        else:        # Bodenblech: Gewinde M3 von unten
            p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.25, 7.0, cq.Vector(xc, yf, COVER_SCREW_Z), cq.Vector(0, 1, 0))))
        p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.25, 7.0, cq.Vector(sx * (W / 2 - REAR_SCREW_U), sy * REAR_SCREW_Y,
                                                                                    Z_REAR + RP_T), cq.Vector(0, 0, 1))))
    return cq.Workplane("XY").add(p.val().Solids()[0])


def make_side_stub(sx, length=70.0):
    """Vorderer Ausschnitt des Seitenteils (Darstellung)."""
    p = make_side_panel(sx).intersect(cq.Workplane("XY").box(W, H + 2, length, centered=(True, True, False))
                                      .translate((0, 0, FL_Z0 - length)))
    return cq.Workplane("XY").add(p.val().Solids()[0])


def make_rear_panel():
    """Rückwand (nur Kontur + 4 Senkbohrungen): zwischen den Seitenteil-Wänden, hinter den Wulsten."""
    yT, yB = H / 2 - COVER_T, -H / 2 + BOT_T
    r = (cq.Workplane("XY").box(W - 2 * SIDE_T - 0.2, yT - yB, RP_T, centered=(True, True, False))
         .translate((0, (yT + yB) / 2, Z_REAR)))
    for sx in (1, -1):
        for sy in (1, -1):
            x, y = sx * (W / 2 - REAR_SCREW_U), sy * REAR_SCREW_Y
            r = r.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.7, RP_T + 0.2, cq.Vector(x, y, Z_REAR - 0.1), cq.Vector(0, 0, 1))))
            r = r.cut(cq.Workplane("XY").add(cq.Solid.makeCone(3.3, 1.5, 1.8, cq.Vector(x, y, Z_REAR - 0.01), cq.Vector(0, 0, 1))))
    return r


def tab_screw_points():
    """(x, y_Außenfläche, sy) je Laschenschraube."""
    return [(sx * (W / 2 - TAB_SCREW_U), sy * (H / 2 - (COVER_T if sy > 0 else BOT_T)), sy) for sx in (1, -1) for sy in (1, -1)]


def make_tab_screws():
    """ISO 10642 M3x8 senkrecht durch die Laschen in die Wulst der Seitenteile."""
    out = None
    for x, yf, sy in tab_screw_points():
        head = cq.Solid.makeCone(3.0, 1.5, 1.6, cq.Vector(x, yf - sy * 0.05, TAB_SCREW_Z), cq.Vector(0, -sy, 0))
        shank = cq.Solid.makeCylinder(1.25, SCREW_LEN - 1.6, cq.Vector(x, yf - sy * 1.65, TAB_SCREW_Z), cq.Vector(0, -sy, 0))
        w = cq.Workplane("XY").add(head).union(cq.Workplane("XY").add(shank))
        out = w if out is None else out.union(w)
    return out


def make_knob_shell():
    """Absolute Z-Koordinaten, Achse bei X=Y=0."""
    k = cq.Workplane("XY").workplane(offset=KNOB_Z0).circle(KNOB_D / 2).extrude(KNOB_Z1 - KNOB_Z0)
    k = k.faces(">Z").edges().chamfer(0.3)
    k = k.cut(cq.Workplane("XY").workplane(offset=FLOOR_TOP).circle(SHELL_ID / 2).extrude(KNOB_PROT + 1))
    # Bund (Z BRG_W..KNOB_Z0) mit O-Ring-Nut, Lagersitz Ø25 k6 (Z 0..BRG_W), Ende bis HUB_Z0
    k = k.union(cq.Workplane("XY").workplane(offset=BRG_W).circle(COLLAR_D / 2).extrude(KNOB_Z0 - BRG_W + 0.01))
    k = k.cut(cq.Workplane("XY").workplane(offset=BRG_W + 0.6).circle(COLLAR_D / 2 + 1)
              .circle(ORING_GROOVE_D / 2).extrude(ORING_GROOVE_W))
    k = k.union(cq.Workplane("XY").workplane(offset=HUB_Z0).circle(BRG_ID / 2).extrude(BRG_W - HUB_Z0 + 0.01))
    k = k.cut(cq.Workplane("XY").workplane(offset=HUB_Z0).circle(MAGNET_D / 2).extrude(MAGNET_H))
    k = k.cut(cq.Workplane("XY").workplane(offset=HUB_Z0).polarArray(9.5, 90, 360, 3)
              .circle(2.05 / 2).extrude(7))                                      # M2,5 Kernloch
    k = k.cut(cq.Workplane("XY").workplane(offset=KNOB_Z0)
              .polarArray(WIN_PCD / 2, 0, 360, WIN_N).circle(WIN_D / 2).extrude(FLOOR_TOP - KNOB_Z0))
    return k


def make_light_tube():
    return (cq.Workplane("XY").workplane(offset=FLOOR_TOP).circle(TUBE_OD / 2).circle(TUBE_ID / 2)
            .extrude(KNOB_PROT))


def make_cone_insert():
    c = cq.Workplane("XY").workplane(offset=FLOOR_TOP).circle(INS_OD / 2).extrude(KNOB_PROT)
    cone = cq.Solid.makeCone(CONE_FLOOR_D / 2, CONE_LIP_ID / 2, KNOB_PROT + 0.02,
                             pnt=cq.Vector(0, 0, FLOOR_TOP - 0.01))
    return c.cut(cq.Workplane("XY").add(cone))


def make_washer():
    w = cq.Workplane("XY").circle(WASHER_D / 2).circle(MAGNET_D / 2 + 1.5).extrude(WASHER_T)
    return w.cut(cq.Workplane("XY").polarArray(9.5, 90, 360, 3).circle(2.8 / 2).extrude(WASHER_T))


def make_knob():
    return make_knob_shell().union(make_light_tube()).union(make_cone_insert())


SW_H = 4.3                                       # Omron B3F-1000
PWR_STEM = (PWR_CB_DEPTH - 1.5) - (PCB_Z + SW_H) + 0.1   # Stößel bis Tasterkuppe, 0,1 Vorspannung


def make_power_cap():
    """Lokal: Z=0 = Stößelende."""
    stem = cq.Workplane("XY").circle(1.5).extrude(PWR_STEM)
    collar = cq.Workplane("XY").workplane(offset=PWR_STEM).circle(PWR_CB_D / 2 - 0.2).extrude(1.5)
    shaft = (cq.Workplane("XY").workplane(offset=PWR_STEM + 1.5).circle(PWR_D / 2).extrude(T - PWR_CB_DEPTH + 1.5)
             .faces(">Z").edges().fillet(1.5))
    return stem.union(collar).union(shaft)


# ---------------- Knopfplatine (Encoder + LED-Ring + Einschalttaster) ----------------
PCB_T = 1.6
PCB_OUTLINE = [(-34, -34.5), (34, -34.5), (34, 16), (37, 16), (37, 34.5), (-34, 34.5)]   # relativ zur Knopfachse
LED_L, LED_W, LED_H = 3.5, 2.8, 1.9               # PLCC-2 3528, weiß, Top-View
SOIC_L, SOIC_W, SOIC_H = 4.9, 3.9, 1.5            # AS5600


def make_knob_pcb():
    """Lokale Koordinaten relativ zur Knopfachse, absolute Z. Bestückung vorn (Richtung Front)."""
    p = cq.Workplane("XY").workplane(offset=PCB_Z - PCB_T).polyline(PCB_OUTLINE).close().extrude(PCB_T)
    p = p.edges("|Z").fillet(1.0)
    holes = [(x - KNOB_X, y) for x, y in M3_HOLES["LED/Encoder-PCB"]]
    return p.cut(cq.Workplane("XY").workplane(offset=PCB_Z - PCB_T).pushPoints(holes).circle(3.2 / 2).extrude(PCB_T))


def make_pcb_parts():
    """dict Name -> Workplane, relativ zur Knopfachse."""
    import math
    z = PCB_Z
    parts = {}
    parts["AS5600_SOIC8"] = cq.Workplane("XY").workplane(offset=z).rect(SOIC_L, SOIC_W).extrude(SOIC_H)
    leds = None
    for k in range(WIN_N):
        a = math.radians(k * 360 / WIN_N)
        l = (cq.Workplane("XY").workplane(offset=z).rect(LED_L, LED_W).extrude(LED_H)
             .rotate((0, 0, 0), (0, 0, 1), k * 360 / WIN_N + 90)
             .translate((WIN_PCD / 2 * math.cos(a), WIN_PCD / 2 * math.sin(a), 0)))
        leds = l if leds is None else leds.union(l)
    parts["LED_3528_12x"] = leds
    sx, sy = PWR_X - KNOB_X, PWR_Y
    sw = cq.Workplane("XY").workplane(offset=z).center(sx, sy).rect(6, 6).extrude(3.5)
    sw = sw.union(cq.Workplane("XY").workplane(offset=z + 3.5).center(sx, sy).circle(1.75).extrude(SW_H - 3.5))
    parts["Taster_B3F-1000"] = sw
    parts["Stecker_JST-PH_7p_hinten"] = (cq.Workplane("XY").workplane(offset=z - PCB_T - 6.0)
                                         .center(-16, -30).rect(15.9, 4.5).extrude(6.0))
    holes = [(x - KNOB_X, y) for x, y in M3_HOLES["LED/Encoder-PCB"]]
    so = None
    for hx, hy in holes:
        b = (cq.Workplane("XY").workplane(offset=z).center(hx, hy).polygon(6, 5.5 / math.cos(math.pi / 6))
             .extrude(-z).cut(cq.Workplane("XY").workplane(offset=z).center(hx, hy).circle(1.6).extrude(-z)))
        sc = (cq.Workplane("XY").workplane(offset=z - PCB_T - 2.0).center(hx, hy).circle(2.75).extrude(2.0)
              .union(cq.Workplane("XY").workplane(offset=z - PCB_T).center(hx, hy).circle(1.25).extrude(PCB_T - z)))
        so = b if so is None else so.union(b)
        parts.setdefault("_screws", []).append(sc)
    parts["Abstandsbolzen_M3x4_4x"] = so
    scr = parts.pop("_screws")
    s0 = scr[0]
    for sc in scr[1:]:
        s0 = s0.union(sc)
    parts["Schrauben_M3x8_4x"] = s0
    return parts


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    for fn in os.listdir(out):                       # nur Dateien der Frontplatte löschen, Unterordner bleiben
        if os.path.isfile(os.path.join(out, fn)):
            os.remove(os.path.join(out, fn))
    frame = make_frame()
    panel = make_panel()
    cq.exporters.export(frame, f"{out}/RD160_Front_Rahmen.step")
    cq.exporters.export(panel, f"{out}/RD160_Front_Plexiglas.step")
    cq.exporters.export(panel.section(PANEL_T / 2), f"{out}/RD160_Front_Plexiglas.dxf")
    cq.exporters.export(make_button_cap(), f"{out}/RD160_Tasterkappe.step")
    asm = (cq.Assembly()
           .add(frame, name="Rahmen", color=cq.Color(0.16, 0.16, 0.17))
           .add(panel, name="Plexiglas", loc=cq.Location((0, 0, CARRIER_T)),
                color=cq.Color(0.05, 0.05, 0.05)))
    for name, fn in (("Knopf_Becher", make_knob_shell), ("Knopf_Lichtleiter_PMMA", make_light_tube),
                     ("Knopf_Konuseinsatz", make_cone_insert), ("Knopf_Haltescheibe", make_washer),
                     ("Einschaltkappe", make_power_cap)):
        cq.exporters.export(fn(), f"{out}/RD160_{name}.step")
    asm.add(make_knob_shell(), name="Knopf_Becher", loc=cq.Location((KNOB_X, 0, 0)), color=cq.Color(0.1, 0.1, 0.1))
    asm.add(make_light_tube(), name="Knopf_Lichtleiter", loc=cq.Location((KNOB_X, 0, 0)), color=cq.Color(0.95, 0.95, 0.95))
    asm.add(make_cone_insert(), name="Knopf_Konus", loc=cq.Location((KNOB_X, 0, 0)), color=cq.Color(0.45, 0.45, 0.47))
    asm.add(make_foam(), name="Schaumstoff", color=cq.Color(0.08, 0.08, 0.08))
    asm.add(make_washer(), name="Haltescheibe", loc=cq.Location((KNOB_X, 0, HUB_Z0 - WASHER_T)), color=cq.Color(0.6, 0.6, 0.6))
    asm.add(make_power_cap(), name="Einschaltkappe",
            loc=cq.Location((PWR_X, PWR_Y, PCB_Z + SW_H - 0.1)), color=cq.Color(0.7, 0.7, 0.72))
    for sx, nm in ((1, "rechts"), (-1, "links")):
        asm.add(make_side_stub(sx), name=f"Seitenteil_{nm}_Ausschnitt", color=cq.Color(0.1, 0.1, 0.11))
    asm.add(make_tab_screws(), name="Laschenschrauben_M3x8_ISO10642", color=cq.Color(0.3, 0.3, 0.3))
    asm.add(make_cover_edge(), name="Deckel_Ausschnitt", color=cq.Color(0.75, 0.76, 0.78))
    asm.save(f"{out}/RD160_Front_Baugruppe.step")
    # Kollisionsprüfung Rahmen / Seitenteile / Deckel / Schaumstoff / Schrauben
    chk = {"Rahmen": frame, "Seitenteil_r": make_side_panel(1), "Seitenteil_l": make_side_panel(-1),
           "Deckel": make_cover(), "Boden": make_bottom(), "Rueckwand": make_rear_panel(),
           "Schaum": make_foam(), "Schrauben": make_tab_screws()}
    ks = list(chk)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            v = chk[ks[i]].intersect(chk[ks[j]]).val().Volume() if True else 0
            if v > 1e-3:
                print("KOLLISION", ks[i], ks[j], round(v, 3))
    print("Kollisionsprüfung fertig")
    bb = frame.val().BoundingBox()
    print("Rahmen BB:", round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2),
          "| Platte:", round(PANEL_W, 1), "x", round(PANEL_H, 1), "x", PANEL_T)
