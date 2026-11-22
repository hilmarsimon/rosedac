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
W, H, T = 430.0, 78.0, 13.5           # Außenmaß (Korpus ohne Füße; Fotos: ca. 74 + Füße, 78 wegen DFR0524), Frontdicke
                                      # (Lippe 1,5 + Platte 3 + Träger 9)
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
JOINT = DECO_W                        # Fuge Deckel/Boden ↔ Front ringsum = Ziernutbreite: eine durchgehende Linie
BOT_T = 1.0                           # Bodenblech 1 mm
BOT_LIP = 1.0                         # Steg unter der Bodennut (Front, Seitenteile, Rückwand): Blech unsichtbar eingesetzt
BOT_CLR = 0.2                         # Nutspiel über dem Blech
BOT_IN = BOT_LIP + BOT_T + BOT_CLR    # Unterkante Wulst/Lasche/Querleiste über der Geräteunterkante
BOT_NUT_FRONT, BOT_NUT_SIDE, BOT_NUT_REAR = 5.0, 2.5, 2.0   # Nuttiefen: Front (in z), Seitenwand (in x), Rückwand (in z)
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

# ---------------- Front zweiteilig: Blende + Platte + Träger ----------------
# Blende (Alu, sichtbar): Ring W x H mit Lippe LIP_T vorn, Fenster POCKET_W x POCKET_H (Rand FRAME_B), dahinter Falz für die
# Platte; Wände 2,5 mm, Seitenwände volle Tiefe (Front umgreift die Ecke). Plexiglasplatte wird VON HINTEN eingelegt,
# Kante + Dehnspalt liegen verdeckt hinter der Lippe -> keine sichtbare Fuge. Träger (Alu) von hinten eingesetzt: Display-
# tasche, Taster, Knopflager, Flansche/Auflage, Laschen. Blende <-> Träger: M2,5 Senkschrauben von unten (Unterseite).
LIP_T = 1.5                           # Lippe vor der Platte
LIP_CH = 0.4                          # 45°-Fase an der Fensterkante
PANEL_T = 3.0                         # PLEXIGLAS LED B&W 9H04 SC / 7H25 GT
PANEL_OVL = 1.2                       # Platte unter der Lippe je Seite
PANEL_GAP = 0.3                       # Dehnspalt je Seite im Falz (PMMA ~3x Alu)
SEAT_GAP = 0.3                        # Träger-Vorderseite hinter der Platte (Poron 0,5 dazwischen, PMMA-Dickentoleranz)
CARRIER_T = T - LIP_T - PANEL_T       # Plattenrückseite = 9 (Träger-Vorderseite CARRIER_T - SEAT_GAP)
POCKET_W, POCKET_H = W - 2 * FRAME_B, H - 2 * FRAME_B          # Fenster in der Lippe
PANEL_W, PANEL_H = POCKET_W + 2 * PANEL_OVL, POCKET_H + 2 * PANEL_OVL
PANEL_R = FRAME_R + PANEL_OVL
RAB_X, RAB_Y = PANEL_W / 2 + PANEL_GAP, PANEL_H / 2 + PANEL_GAP   # Falz/Durchgang in der Blende (halbe Maße)
RAB_R = PANEL_R + PANEL_GAP
BZ_CLR = 0.1                          # Spiel Träger <-> Blende
BZ_SCREW_X = (-208.0, -172.0, -135.0, 135.0, 172.0, 208.0)       # M2,5 Senk von unten (Unterseite), außerhalb der Displaytasche
BZ_SCREW_Z = (T - BAND + CARRIER_T - SEAT_GAP) / 2                 # Mitte Band-Rückseite .. Trägerfront

# ---------------- Display ----------------
DISP_W, DISP_H = 2 * 124.0, 71.0      # 2x DFR0524 Outline, Stoß bei X=0
DISP_CLR = 0.5
DISP_X = 0.0
PNL_W = DISP_W + 2 * DISP_CLR
PNL_H = DISP_H + 2 * DISP_CLR
PNL_DEPTH = CARRIER_T                 # von hinten bis an die Plexiglasplatte
GROOVE_X0 = PNL_W / 2 + 4.0           # Deckelnut/Feder nur außerhalb der Displaytasche (H = 78: Tasche reicht bis y 36)

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
PWR_X, PWR_Y = 196.0, 22.0             # 13 mm unter Fensteroberkante, Schalterkörper frei vom Flansch
PWR_D, PWR_HOLE_D, PWR_PANEL_D = 12.0, 12.2, 12.6
PWR_CB_D, PWR_CB_DEPTH = 16.0, 5.0

# ---------------- Gewinde M3 (Sackloch von hinten) ----------------
M3_TAP_D, M3_DRILL_DEPTH, M3_THREAD_DEPTH = 2.5, 7.0, 6.0
M3_HOLES = {
    "Chassis":       [(-128, 0), (128, 0)],
    "Taster-PCB":    [(x, sy * 26) for x in (-191, -153) for sy in (-1, 1)],   # y26: Abstandsbolzen Ø5 frei vom Flansch (y30)
    "LED/Encoder-PCB": [(KNOB_X - 30, 24), (KNOB_X - 30, -24), (KNOB_X + 22, -25), (KNOB_X + 8, 25)],
    "Panel-Klemmrahmen": [(sx * 127, sy * 25) for sx in (-1, 1) for sy in (-1, 1)],
}


def rrect(w, h, r):
    return cq.Sketch().rect(w, h).vertices().fillet(r)


def _groove_tool():
    """Nut für die Deckelfeder (Bandrückseite, Scheibenfräser), zwei Abschnitte neben der Displaytasche."""
    import math
    zb = T - BAND
    ix = W / 2 - END_W
    run = math.sqrt(CUTTER_R ** 2 - (CUTTER_R - GROOVE_D) ** 2)  # Auslauflänge an der Rückseite
    g = None
    for sx in (1, -1):                         # zwei Nutabschnitte links/rechts der Displaytasche, je 2 Fräserausläufe
        xa, xb = GROOVE_X0 + run, ix - run
        seg = (cq.Workplane("XZ").workplane(offset=-(H / 2 - GROOVE_TOP)).center(sx * (xa + xb) / 2, zb)
               .rect(xb - xa, 2 * GROOVE_D).extrude(GROOVE_H))
        for xc in (xa, xb):
            seg = seg.union(cq.Workplane("XY").add(cq.Solid.makeCylinder(
                CUTTER_R, GROOVE_H, cq.Vector(sx * xc, H / 2 - GROOVE_TOP - GROOVE_H, zb + GROOVE_D - CUTTER_R),
                cq.Vector(0, 1, 0))))
        g = seg if g is None else g.union(seg)
    return g.intersect(cq.Workplane("XY").box(2 * ix, H, zb + GROOVE_D - FL_Z0 + 1, centered=(True, True, False))
                       .translate((0, 0, FL_Z0 - 1)))


def _front_body(front_pocket=False):
    """Front als Vollkörper (alte einteilige Geometrie) – Basis für Träger (Schnitt) und Testfront."""
    p = cq.Workplane("XY").box(W, H, T, centered=(True, True, False))
    p = p.faces(">Z").edges().chamfer(EDGE_CHAMFER)

    # Ober-/Unterkante: Flansch nach hinten; oben Auflage für Deckel, unten Bodennut
    zb = T - BAND                                  # Rückseite Band
    ix = W / 2 - END_W
    for sy in (1, -1):                         # Flansch oben und unten
        p = p.union(cq.Workplane("XY").box(W, FL_H, -FL_Z0, centered=(True, True, False))
                    .translate((0, sy * (H / 2 - FL_H / 2), FL_Z0)))
    for sy, seat in ((1, SEAT_D),):          # Auflage nur oben (Deckel + Schaumstoff); unten Bodennut, siehe _bottom_slot_front
        p = p.cut(cq.Workplane("XY").box(2 * ix, seat + 0.01, zb - FL_Z0 + 0.01, centered=(True, True, False))
                  .translate((0, sy * (H / 2 - seat / 2 + 0.005), FL_Z0 - 0.01)))
    p = p.cut(_groove_tool())

    # Innenecken der Auflage (Band-Rückseite / Seitenwand) senkrecht ausgerundet SEAT_R (Fräserradius, wie Original)
    for sy, seat in ((1, SEAT_D),):          # nur oben: Bodenblech ist ein Rechteck und stößt hinten an die Front
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
            yf = sy * (H / 2 - (COVER_T if sy > 0 else BOT_IN))     # Außenfläche Lasche = Deckelunterseite / Wulstunterkante
            p = p.union(cq.Workplane("XY").box(TAB_W, TAB_T, TAB_L + 0.01, centered=(True, True, False))
                        .edges("|Y and <Z").fillet(1.5)
                        .translate((xc, yf - sy * TAB_T / 2, FL_Z0 - TAB_L)))
            xs = sx * (W / 2 - TAB_SCREW_U)
            p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.7, TAB_T + 0.2, cq.Vector(xs, yf + sy * 0.1, TAB_SCREW_Z),
                                                                   cq.Vector(0, -sy, 0))))
            p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCone(3.3, 1.5, 1.8, cq.Vector(xs, yf + sy * 0.01, TAB_SCREW_Z),
                                                               cq.Vector(0, -sy, 0))))

    if front_pocket:                           # nur Testfront: Platte von vorn in Fenstergröße, zurückgesetzt wie hinter der Lippe
        p = p.cut(cq.Workplane("XY").workplane(offset=CARRIER_T)
                  .placeSketch(rrect(POCKET_W, POCKET_H, FRAME_R)).extrude(T - CARRIER_T + 1))

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


def make_bezel():
    """Blende: Ring mit Lippe + Fenster (Fase), Falz für die Platte, Seitenwände volle Tiefe, Nut-Oberkante, Senkungen unten."""
    zb = T - BAND
    b = cq.Workplane("XY").box(W, H, T - FL_Z0, centered=(True, True, False)).translate((0, 0, FL_Z0))
    b = b.faces(">Z").edges().chamfer(EDGE_CHAMFER)
    inner = (cq.Workplane("XY").workplane(offset=FL_Z0 - 1).placeSketch(rrect(2 * RAB_X, 2 * RAB_Y, RAB_R))
             .extrude(T - LIP_T - FL_Z0 + 1))
    # hinter dem Band: Deckel-/Bodenzone frei; Ecken |x| > W/2-END_W oben/unten bleiben Blende (sichtbare Ecke ohne Fuge)
    behind = (cq.Workplane("XY").box(2 * (W / 2 - END_W), H + 2, zb - FL_Z0 + 1, centered=(True, True, False))
              .translate((0, 0, FL_Z0 - 1)))
    win = cq.Workplane("XY").workplane(offset=T - LIP_T - 0.1).placeSketch(rrect(POCKET_W, POCKET_H, FRAME_R)).extrude(LIP_T + 1)
    b = b.cut(inner).cut(behind).cut(win)
    b = b.edges(cq.selectors.BoxSelector((-POCKET_W / 2 - 0.2, -POCKET_H / 2 - 0.2, T - 0.05),
                                         (POCKET_W / 2 + 0.2, POCKET_H / 2 + 0.2, T + 0.05))).chamfer(LIP_CH)
    b = b.cut(_groove_tool())
    for blk in _bezel_corner_blocks(0.0):      # Innenecken Band/Seitenwand R SEAT_R, passend zur Deckel-/Bodenrundung
        b = b.union(blk)
    b = b.cut(_bottom_slot_front())
    b = b.cut(cq.Workplane("XY").box(2 * RAB_X, H / 2 - RAB_Y - BOT_LIP, BOT_NUT_FRONT + 1, centered=(True, False, False))
              .translate((0, -H / 2 + BOT_LIP, FL_Z0 - 1)))   # kein Reststeg über der Nut in den unteren Ecken
    for x in BZ_SCREW_X:                       # M2,5 Senkkopf von unten (Unterseite)
        b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.4, H / 2 - RAB_Y + 0.2, cq.Vector(x, -H / 2 - 0.1, BZ_SCREW_Z),
                                                               cq.Vector(0, 1, 0))))
        b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCone(2.75, 1.25, 1.5, cq.Vector(x, -H / 2 - 0.01, BZ_SCREW_Z),
                                                           cq.Vector(0, 1, 0))))
    return cq.Workplane("XY").add(b.val().Solids()[0])


def _bottom_slot_front():
    """Bodennut in der Front-Rückseite, über die ganze Breite bis in die Seitenteilnut (Scheibenfräser durchgehend)."""
    xs = W / 2 - SIDE_T + BOT_NUT_SIDE
    return (cq.Workplane("XY").box(2 * xs, BOT_T + BOT_CLR, BOT_NUT_FRONT + 1, centered=(True, False, False))
            .translate((0, -H / 2 + BOT_LIP, FL_Z0 - 1)))


def _bezel_corner_blocks(clr):
    """Ausrundungsblöcke der sichtbaren Innenecken (oben über dem Falz, unten Bodenauflage). clr > 0: Freischnitt im Träger."""
    zb, ix = T - BAND, W / 2 - END_W
    out = []
    for sx in (1, -1):
        for y0, y1 in ((RAB_Y, H / 2),):
            h = y1 - y0 + 2 * clr
            blk = (cq.Workplane("XY").box(SEAT_R + clr, h, SEAT_R + clr, centered=(False, False, False))
                   .translate((sx * ix - (SEAT_R + clr if sx > 0 else 0), y0 - clr, zb - SEAT_R - clr)))
            if clr == 0:
                cyl = cq.Solid.makeCylinder(SEAT_R, h + 0.2, cq.Vector(sx * (ix - SEAT_R), y0 - 0.1, zb - SEAT_R), cq.Vector(0, 1, 0))
                blk = blk.cut(cq.Workplane("XY").add(cyl))
            out.append(blk)
    return out


def make_carrier():
    """Träger: Vollkörper innerhalb der Blende, vorn SEAT_GAP hinter der Platte; Gewinde M2,5 für die Blende."""
    zb = T - BAND
    z0 = FL_Z0 - TAB_L - 5
    reg = (cq.Workplane("XY").workplane(offset=z0).placeSketch(rrect(2 * (RAB_X - BZ_CLR), 2 * (RAB_Y - BZ_CLR), RAB_R - BZ_CLR))
           .extrude(CARRIER_T - SEAT_GAP - z0))
    reg = reg.union(cq.Workplane("XY").box(2 * (W / 2 - END_W - BZ_CLR), H + 2, zb - z0, centered=(True, True, False))
                    .translate((0, 0, z0)))
    c = _front_body().intersect(reg).cut(_bottom_slot_front())
    for blk in _bezel_corner_blocks(BZ_CLR):  # sichtbare Eckausrundung gehört zur Blende
        c = c.cut(blk)
    for x in BZ_SCREW_X:
        c = c.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.03, 6.0, cq.Vector(x, -RAB_Y, BZ_SCREW_Z), cq.Vector(0, 1, 0))))
    return cq.Workplane("XY").add(c.val().Solids()[0])


def make_frame():
    """Blende + Träger als Compound (Darstellung, Kollisionsprüfung)."""
    return cq.Workplane("XY").add(cq.Compound.makeCompound([make_bezel().val(), make_carrier().val()]))


def make_front_onepiece():
    """Testfront: einteilig, Platte von vorn in Fenstergröße, 1,5 zurückgesetzt."""
    return _front_body(front_pocket=True)


def make_panel():
    p = cq.Workplane("XY").placeSketch(rrect(PANEL_W, PANEL_H, PANEL_R)).extrude(PANEL_T)
    p = p.cut(cq.Workplane("XY").pushPoints(btn_positions()).circle(BTN_PANEL_D / 2).extrude(PANEL_T))
    p = p.cut(cq.Workplane("XY").center(KNOB_X, 0).circle(SHAFT_PANEL_D / 2).extrude(PANEL_T))
    p = p.cut(cq.Workplane("XY").center(PWR_X, PWR_Y).circle(PWR_PANEL_D / 2).extrude(PANEL_T))
    return p


def make_button_cap():
    # Stößel Ø3 x 4,2 | Bund Ø8,6 x 1,5 | Schaft Ø6: 4 Träger + 3 Platte + 1,5 Überstand
    stem = cq.Workplane("XY").circle(1.5).extrude(4.2)
    collar = cq.Workplane("XY").workplane(offset=4.2).circle(4.3).extrude(1.5)
    shaft_len = (CARRIER_T + PANEL_T - BTN_CB_DEPTH) + 1.5   # 1,5 über Plattenfront
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
    wf = 2 * (W / 2 - END_W - JOINT)           # Fuge JOINT zu den Seitenwänden der Front
    wb = W                                     # ebene Platte über die Seitenwände, außen bündig
    z_end = FL_Z0 - 0.3
    front = (cq.Workplane("XY").box(wf, t, zb - JOINT - FL_Z0 + 0.31, centered=(True, True, False))
             .translate((0, yc, FL_Z0 - 0.31)))
    front = front.edges("|Y and >Z").fillet(SEAT_R - JOINT)     # konzentrisch zur Innenecke R SEAT_R: Fuge rundum JOINT
    body = (cq.Workplane("XY").box(wb, t, length, centered=(True, True, False)).translate((0, yc, z_end - length)))
    p = front.union(body)
    if tongue:                                 # zwei Federabschnitte passend zu den Nutabschnitten (je 1 mm kürzer)
        run = math.sqrt(CUTTER_R ** 2 - (CUTTER_R - GROOVE_D) ** 2)
        xa, xb = GROOVE_X0 + run + 1.0, W / 2 - END_W - run - 1.0
        for sx in (1, -1):
            p = p.union(cq.Workplane("XY").box(xb - xa, TONGUE_T, TONGUE_L + JOINT - 0.3 + 0.01, centered=(True, True, False))
                        .translate((sx * (xa + xb) / 2, H / 2 - GROOVE_TOP - TONGUE_T / 2, zb - JOINT - 0.01)))
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
REAR_SCREW_U = SIDE_T + BEAD_W / 2     # seitliche Rückwandschrauben axial in den Mittelblock der Seitenteile, 9,5 vom Rand
COVER_SCREW_Z = Z_REAR + RP_T + 12.0   # Deckel-/Bodenschrauben in der Wulst, frei von der Querleiste (10 tief)

# ---------------- Rückwand: Anordnung nach Originalfoto ----------------
# Foto Rückseite (Hersteller), Maßstab über die Gerätebreite 430 mm. Rückansicht: v = -x (nach rechts beim Blick auf die
# Rückwand), y wie Gerät. Kanal R links, Digital Mitte, Kanal L rechts. Befestigung wie Original: 10 Schrauben – je 4 oben/unten
# in Querleisten (Alu 10x10 unter dem Deckel / auf dem Boden), je 1 seitlich mittig in einen Block der Seitenteile.
RP_YT, RP_YB = H / 2 - COVER_T, -H / 2              # Ober-/Unterkante Rückwand (unten bis zur Geräteunterkante, Bodennut innen)
QL_H, QL_D = 10.0, 10.0                # Querleiste: Höhe, Tiefe (hinter der Rückwand)
QL_FIX_X = (0.0, -120.0, 120.0)        # Querleiste ↔ Deckel (Sackgewinde von unten) bzw. ↔ Bodenblech (ISO 7380 von unten)
RP_SCR_X = (61.3, 185.0)               # Foto: obere/untere Schrauben bei ±61 und ±185
RP_SIDE_Y = -2.0                       # Foto: seitliche Schrauben mittig
SIDE_BOSS_H, SIDE_BOSS_D = 12.0, 12.0  # Block im Seitenteil (Wulstbreite) für die seitliche Schraube


def rear_screw_points():
    """(v, y) Rückansicht aller 10 Rückwandschrauben (M3 Senkkopf ISO 10642)."""
    pts = [(sv * v, y) for v in RP_SCR_X for sv in (1, -1) for y in (RP_YT - QL_H / 2, -H / 2 + BOT_IN + QL_H / 2)]
    return pts + [(sv * (W / 2 - REAR_SCREW_U), RP_SIDE_Y) for sv in (1, -1)]


EXT_CLOCK = False                      # 10-MHz-Eingang (75 Ω BNC / 50 Ω): FifoPi Q7 ohne 10-MHz-Referenz → Buchsen entfallen
D_HOLE, D_SCR = 24.0, (-9.5, 12.0)     # Neutrik D-Serie: Ø24, 2x M3 diagonal (−9,5|+12) (+9,5|−12) wie Foto
RP_YC = -8.2                           # Mitte XLR/Cinch-Ausgänge
# key, Bezeichnung, Typ, v, y, Maße, Körper hinter der Wand (b, h, Tiefe inkl. Stecker), Bauteil
# Typ rund: (d,) | dflat: (d, Schlüsselweite) | neutrik_d: () | iec: (b, h, Lochabstand) | rect: (b, h, [(dv, dy) M3])
RP_CONN = [
    ("BRK", "CIRCUIT BREAKER", "dflat", -184.5, 13.0, (9.6, 8.9), (32, 14, 30), "E-T-A 1658-G21-02-P10-2A (3/8-27, D-Fläche)"),
    ("GND", "GND", "rund", -155.7, 9.5, (6.5,), (12, 12, 20), "Polklemme 4 mm vergoldet, isoliert"),
    ("IEC", "POWER / AC INPUT", "iec", -174.1, -10.0, (27.8, 20.0, 40.0), (30, 24, 40), "Kaltgeräte C14 mit Sicherung, Schraubbef. 40 mm"),
    ("XLR_R", "BALANCED R", "neutrik_d", -95.8, RP_YC, (), (26, 31, 35), "Neutrik NC3MD-L-1"),
    ("RCA_R", "UNBALANCED R", "rund", -64.9, RP_YC, (10.0,), (16, 16, 28), "Cinch Einbau isoliert, Wand ≤ 5 mm"),
    ("TRI", "TRIGGER IN", "rund", -39.0, 9.7, (6.2,), (10, 12, 20), "Klinke 3,5 mm Einbau"),
    ("TRO", "TRIGGER OUT", "rund", -39.0, -6.5, (6.2,), (10, 12, 20), "Klinke 3,5 mm Einbau"),
    ("SVC", "SVC PORT", "rect", -39.2, -19.3, (9.6, 3.9, []), (14, 8, 30), "USB-C Einbaubuchse mit Kabel → RP2040 (Firmware)"),
    ("AES", "AES/EBU INPUT", "neutrik_d", -13.8, -7.2, (), (26, 31, 35), "Neutrik NC3FD-L-1"),
    ("COX1", "COAX.1 IN", "rund", 13.4, 9.7, (10.0,), (16, 16, 28), "Cinch Einbau isoliert"),
    ("OPT", "OPTICAL IN", "rect", 13.4, -14.9, (9.5, 10.0, [(0, 10.2)]), (16, 14, 30), "Toslink-Einbaubuchse, Winkel an M3 oben"),
    ("COX2", "COAX.2 IN", "rund", 37.1, 9.7, (9.7,), (14, 14, 28), "BNC 75 Ω Einbau isoliert"),
    ("I2S", "I2S INPUT", "rect", 37.1, -17.1, (16.0, 7.0, [(0, 9.9)]), (22, 10, 45), "HDMI-Einbaubuchse mit Kabel, Winkel an M3 oben"),
    ("USB", "PC AUDIO IN", "rect", 61.4, -15.1, (12.5, 11.0, []), (16, 14, 40), "USB-B Einbaubuchse mit Kabel"),
    ("LAN", "LAN", "rect", 85.5, -11.5, (16.5, 14.0, []), (18, 16, 40), "RJ45-Kupplung Einbau → Pi 5 (an Stelle SFP)"),
    ("RCA_L", "UNBALANCED L", "rund", 113.1, RP_YC, (10.0,), (16, 16, 28), "Cinch Einbau isoliert"),
    ("XLR_L", "BALANCED L", "neutrik_d", 144.3, RP_YC, (), (26, 31, 35), "Neutrik NC3MD-L-1"),
]
if EXT_CLOCK:
    RP_CONN += [("CLK75", "EXT. CLOCK 75 Ω", "rund", 61.7, 9.7, (9.7,), (14, 14, 28), "BNC 75 Ω Einbau"),
                ("CLK50", "EXT. CLOCK 50 Ω", "rund", 85.6, 9.7, (9.7,), (14, 14, 28), "BNC 50 Ω Einbau")]

# Gravur (Laser nach Eloxal) wie Originaldruck: Rahmen (v0, v1, y0, y1), Linien ((v0, y0), (v1, y1)), Texte (txt, v, y, h, Winkel)
GY_T, GY_B, GY_HDR, GY_MID, GY_FTR = 23.1, -27.1, 19.2, 0.4, -23.1
RP_FRAMES = [(-201.6, -163.7, 3.4, GY_T), (-163.7, -145.6, 3.4, GY_T), (-201.6, -145.6, GY_B, 2.6),
             (-111.7, -49.4, GY_B, GY_T), (-48.8, -29.4, GY_B, GY_T), (-28.9, 0.4, GY_B, GY_T),
             (1.2, 25.1, GY_B, GY_T), (25.6, 49.1, GY_B, GY_T),
             (49.5, 97.3, GY_B, GY_T) if EXT_CLOCK else (49.5, 97.3, GY_B, GY_MID), (97.8, 159.8, GY_B, GY_T),
             (162.4, 202.3, -26.4, 19.6)]
RP_LINES = [((-194.9, 3.4), (-194.9, GY_T)), ((-163.7, GY_HDR), (-145.6, GY_HDR)), ((-201.6, GY_FTR), (-145.6, GY_FTR)),
            ((-111.7, GY_HDR), (-49.4, GY_HDR)), ((-80.3, 10.5), (-80.3, -18.5)),
            ((-48.8, GY_HDR), (-29.4, GY_HDR)), ((-48.8, -15.1), (-29.4, -15.1)), ((-48.8, GY_FTR), (-29.4, GY_FTR)),
            ((-28.9, GY_HDR), (0.4, GY_HDR)),
            ((1.2, GY_HDR), (97.3 if EXT_CLOCK else 49.1, GY_HDR)), ((1.2, GY_MID), (97.3 if EXT_CLOCK else 49.1, GY_MID)),
            ((1.2, GY_FTR), (97.3, GY_FTR)),
            ((73.2, GY_MID), (73.2, GY_B)), ((97.8, GY_HDR), (159.8, GY_HDR)), ((128.8, 10.5), (128.8, -18.5)),
            ((162.4, 12.0), (202.3, 12.0))]
TH, TS = 2.2, 2.0                      # Schrifthöhe Überschrift / Unterzeile
RP_TEXTS = [
    ("CIRCUIT", -199.2, 13.2, 1.8, 90), ("BREAKER", -196.9, 13.2, 1.8, 90), ("PRESS", -170.0, 16.3, TS, 0),
    ("TO", -170.0, 13.2, TS, 0), ("RESET", -170.0, 10.1, TS, 0), ("GND", -154.6, 21.2, TH, 0),
    ("POWER / AC INPUT~", -173.6, -25.1, TH, 0),
    ("ANALOG OUTPUT / RIGHT", -80.5, 21.2, TH, 0), ("BALANCED", -95.8, 15.0, TS, 0), ("UNBALANCED", -64.9, 15.0, TS, 0),
    ("R", -80.3, 15.0, TS, 0), ("R", -80.3, -23.1, TS, 180),
    ("TRIGGER", -39.1, 21.2, TH, 0), ("IN", -39.0, 15.5, TS, 0), ("OUT", -39.0, 0.3, TS, 0), ("SVC PORT", -39.1, -25.1, TH, 0),
    ("AES/EBU INPUT", -14.2, 21.2, TH, 0),
    ("COAX.1 IN", 13.2, 21.2, TH, 0), ("OPTICAL IN", 13.2, -25.1, TH, 0),
    ("COAX.2 IN", 37.3, 21.2, TH, 0), ("I2S INPUT", 37.3, -25.1, TH, 0),
    ("PC AUDIO IN", 61.4, -25.1, TH, 0), ("LAN", 85.3, -25.1, TH, 0),
    ("ANALOG OUTPUT / LEFT", 128.8, 21.2, TH, 0), ("UNBALANCED", 113.1, 15.0, TS, 0), ("BALANCED", 144.3, 15.0, TS, 0),
    ("L", 128.8, 15.0, TS, 0), ("L", 128.8, -23.1, TS, 180),
    ("RD160 DIY", 182.3, 15.8, 3.0, 0), ("Absolute True Fidelity DAC", 182.3, 7.0, 1.6, 0),
    ("Nachbau, Einzelstück", 182.3, 3.5, 1.6, 0), ("Netz: 230 V~ 50 Hz", 182.3, -2.5, 1.6, 0),
    ("Leistung: max. 50 W", 182.3, -6.0, 1.6, 0), ("Sicherung: T 1 A", 182.3, -9.5, 1.6, 0),
    ("H. Simon 2026", 182.3, -20.0, 1.6, 0),
]
if EXT_CLOCK:
    RP_TEXTS += [("EXT. CLOCK INPUT", 73.4, 21.2, TH, 0), ("75 Ω", 70.5, 17.0, 1.8, 0), ("50 Ω", 94.0, 17.0, 1.8, 0)]


def cover_screw_points():
    return [(sx * (W / 2 - COVER_SCREW_U), COVER_SCREW_Z) for sx in (1, -1)]


def ql_fix_points():
    """(x, z) Befestigung der Querleisten am Deckel (oben) bzw. Bodenblech (unten)."""
    return [(x, Z_REAR + RP_T + QL_D / 2) for x in QL_FIX_X]


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
    """Ziernut = Verlängerung der Fuge Deckel/Seitenwand der Front nach hinten: zwei gerade Linien in Flucht der
    Seitenwand-Innenkante (|x| = W/2 - END_W - JOINT .. W/2 - END_W), vom Ende der Frontzone bis hinten offen.
    Vorn und an den Ecken bildet die Fuge (JOINT = DECO_W) selbst die Linie. Rückgabe: x innen, x außen, z hinten, z vorn."""
    return (W / 2 - END_W - JOINT, W / 2 - END_W, Z_REAR, FL_Z0 - 0.3)


def make_deco_groove():
    """Ziernut DECO_W breit, DECO_D tief: nur die beiden Seitenlinien, hinten offen auslaufend."""
    xi, xa, zr, zv = deco_rect()
    g = None
    for sx in (1, -1):
        b = (cq.Workplane("XY").box(xa - xi, DECO_D + 0.01, zv - zr + 2.0, centered=(False, False, False))
             .translate((xi if sx > 0 else -xa, H / 2 - DECO_D, zr - 1.0)))
        g = b if g is None else g.union(b)
    return g


def make_cover():
    """Deckel komplett: ebene 5-mm-Platte ohne sichtbare Bohrungen. Vorn Feder in der Nut, Ziernut; hinten
    2x M3-Sackgewinde in der Unterseite: ISO 4762 M3x10 von unten durch die obere Wulst der Seitenteile."""
    c = _plate(True, FL_Z0 - 0.3 - Z_REAR, True)
    c = c.cut(make_deco_groove())
    for x, z in cover_screw_points() + ql_fix_points():
        c = c.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.25, COVER_THREAD, cq.Vector(x, H / 2 - COVER_T, z),
                                                               cq.Vector(0, 1, 0))))
    return c


BOT_FRONT_Z = FL_Z0 - TAB_L - 8.0      # vordere Bodenschrauben in der unteren Wulst, hinter der Laschentasche


def bot_front_points():
    return [(sx * (W / 2 - COVER_SCREW_U), BOT_FRONT_Z) for sx in (1, -1)]


def make_bottom():
    """Bodenblech 1 mm, Rechteck, unsichtbar eingesetzt: ringsum in Nuten (Front vorn, Seitenwände, Rückwand), darunter
    Steg BOT_LIP. Einschieben von hinten in Seiten- und Frontnut, dann Rückwand aufsetzen. ISO 7380 M3x6 von unten:
    2 vorn + 2 hinten in die Wulst, 3 in die Querleiste."""
    c = 0.2                                    # Spiel je Seite in den Nuten
    xs = W / 2 - SIDE_T + BOT_NUT_SIDE - c
    z0, z1 = Z_REAR + RP_T - BOT_NUT_REAR + c, FL_Z0 + BOT_NUT_FRONT - c
    b = cq.Workplane("XY").box(2 * xs, BOT_T, z1 - z0, centered=(True, False, False)).translate((0, -H / 2 + BOT_LIP, z0))
    for x, z in cover_screw_points() + ql_fix_points() + bot_front_points():   # Ø3,4 für ISO 7380 M3x6 (Linsenkopf)
        b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.7, BOT_T + 0.2, cq.Vector(x, -H / 2 + BOT_LIP - 0.1, z),
                                                               cq.Vector(0, 1, 0))))
    return b


RIB_N = 10                             # Rippen außen (Foto: ca. 10 über die Höhe)
RIB_GROOVE_W = 3.0                     # Nutbreite zwischen den Rippen
RIB_DEPTH = 2.5                        # Nuttiefe (Nutgrund halbrund R1,5); Restwand 2,5
RIB_CROWN = 0.6                        # Wölbung der Rippenoberfläche


def side_profile_face(sx):
    """Querschnitt Seitenteil (XY) als Face: C-Profil, außen geriffelt (RIB_N gewölbte Rippen, halbrunde Nuten).
    Wand bis zur Geräteunterkante, darunter Steg BOT_LIP, Bodennut BOT_NUT_SIDE tief in die Wand, untere Wulst darüber."""
    yT, yB = H / 2 - COVER_T, -H / 2
    yW = -H / 2 + BOT_IN                    # Unterkante untere Wulst
    yN0, yN1 = -H / 2 + BOT_LIP, -H / 2 + BOT_IN   # Bodennut
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
    for u, yy in ((SIDE_W, yT), (SIDE_W, yT - BEAD_H), (SIDE_T, yT - BEAD_H), (SIDE_T, yW + BEAD_H),
                  (SIDE_W, yW + BEAD_H), (SIDE_W, yN1), (SIDE_T - BOT_NUT_SIDE, yN1), (SIDE_T - BOT_NUT_SIDE, yN0),
                  (SIDE_T, yN0), (SIDE_T, yB)):
        wp = wp.lineTo(X(u), yy)
    wire = wp.close().wire().val()
    return cq.Face.makeFromWires(wire)


def make_side_panel(sx):
    """Seitenteil (C-Profil, Wand volle Höhe) volle Länge mit Absätzen für die Frontlaschen, Gewinden und Rückwandanschluss."""
    yT, yB = H / 2 - COVER_T, -H / 2 + BOT_IN   # yB: Unterkante untere Wulst
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
        else:        # Bodenblech: Gewinde M3 von unten, hinten und vorn
            for zz in (COVER_SCREW_Z, BOT_FRONT_Z):
                p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.25, 7.0, cq.Vector(xc, yf, zz), cq.Vector(0, 1, 0))))
    # Mittelblock hinten (Wulstbreite) für die seitliche Rückwandschraube, Gewinde M3 axial 7 tief
    xb = sx * (W / 2 - SIDE_T - BEAD_W / 2)
    p = p.union(cq.Workplane("XY").box(BEAD_W + 0.2, SIDE_BOSS_H, SIDE_BOSS_D, centered=(True, True, False))
                .translate((xb + sx * 0.1, RP_SIDE_Y, Z_REAR + RP_T)))
    p = p.cut(cq.Workplane("XY").add(cq.Solid.makeCylinder(1.25, 7.0, cq.Vector(sx * (W / 2 - REAR_SCREW_U), RP_SIDE_Y,
                                                                                Z_REAR + RP_T), cq.Vector(0, 0, 1))))
    return cq.Workplane("XY").add(p.val().Solids()[0])


def make_side_stub(sx, length=70.0):
    """Vorderer Ausschnitt des Seitenteils (Darstellung)."""
    p = make_side_panel(sx).intersect(cq.Workplane("XY").box(W, H + 2, length, centered=(True, True, False))
                                      .translate((0, 0, FL_Z0 - length)))
    return cq.Workplane("XY").add(p.val().Solids()[0])


def rp_holes(c):
    """2D-Löcher einer Anschlussposition: Liste von ('kreis', v, y, d) | ('dflat', v, y, d, flach) | ('rechteck', v, y, b, h)."""
    key, txt, typ, v, y, m, body, part = c
    if typ == "rund":
        return [("kreis", v, y, m[0])]
    if typ == "dflat":
        return [("dflat", v, y, m[0], m[1])]
    if typ == "neutrik_d":
        du, dy = D_SCR
        return [("kreis", v, y, D_HOLE), ("kreis", v + du, y + dy, 2.5), ("kreis", v - du, y - dy, 2.5)]  # M3 Gewinde
    if typ == "iec":
        b, h, a = m
        return [("rechteck", v, y, b, h), ("kreis", v - a / 2, y, 3.2), ("kreis", v + a / 2, y, 3.2)]
    if typ == "rect":
        b, h, scr = m
        return [("rechteck", v, y, b, h)] + [("kreis", v + dv, y + dy, 2.5) for dv, dy in scr]
    raise ValueError(typ)


def _hole_solid(h):
    z0, L = Z_REAR - 0.1, RP_T + 0.2
    x, y = -h[1], h[2]                                 # Rückansicht v → Geräte-x
    if h[0] == "kreis":
        return cq.Solid.makeCylinder(h[3] / 2, L, cq.Vector(x, y, z0), cq.Vector(0, 0, 1))
    if h[0] == "rechteck":
        return cq.Workplane("XY").workplane(offset=z0).center(x, y).rect(h[3], h[4]).extrude(L).edges("|Z").fillet(0.5).val()
    if h[0] == "dflat":                                 # Ø d mit einer Fläche (Abstand flach von der Gegenseite)
        d, fl = h[3], h[4]
        c = cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(d / 2).extrude(L)
        cut = cq.Workplane("XY").box(d, d, L + 1, centered=(True, False, False)).translate((x, y - d / 2 + fl, z0 - 0.5))
        return c.cut(cut).val()
    raise ValueError(h[0])


def make_rear_panel():
    """Rückwand 4 mm zwischen den Seitenteil-Wänden, hinter den Wulsten: 10 Senkbohrungen M3 + Anschlussausschnitte (RP_CONN)."""
    r = (cq.Workplane("XY").box(W - 2 * SIDE_T - 0.2, RP_YT - RP_YB, RP_T, centered=(True, True, False))
         .translate((0, (RP_YT + RP_YB) / 2, Z_REAR)))
    r = r.cut(cq.Workplane("XY").box(W, BOT_T + BOT_CLR, BOT_NUT_REAR + 1, centered=(True, False, False))   # Bodennut innen
              .translate((0, -H / 2 + BOT_LIP, Z_REAR + RP_T - BOT_NUT_REAR)))
    tools = []
    for v, y in rear_screw_points():
        tools.append(cq.Solid.makeCylinder(1.7, RP_T + 0.2, cq.Vector(-v, y, Z_REAR - 0.1), cq.Vector(0, 0, 1)))
        tools.append(cq.Solid.makeCone(3.3, 1.5, 1.8, cq.Vector(-v, y, Z_REAR - 0.01), cq.Vector(0, 0, 1)))
    tools += [_hole_solid(h) for c in RP_CONN for h in rp_holes(c)]
    r = r.cut(cq.Workplane("XY").add(cq.Compound.makeCompound(tools)))
    return cq.Workplane("XY").add(r.val().Solids()[0])


def make_crossbar(top):
    """Querleiste Alu 10x10 hinter der Rückwand zwischen den Wulsten: oben am Deckel (ISO 4762 M3x10 von unten, Senkung
    Ø6,5x3), unten Gewinde M3 für ISO 7380 durch das Bodenblech. Rückseite 4x Gewinde M3 7 tief für die Rückwand."""
    L = 2 * (W / 2 - SIDE_T - BEAD_W) - 0.2
    y0 = RP_YT - QL_H if top else -H / 2 + BOT_IN
    z0 = Z_REAR + RP_T + 0.05
    q = cq.Workplane("XY").box(L, QL_H, QL_D, centered=(True, False, False)).translate((0, y0, z0))
    tools = []
    for x, z in ql_fix_points():
        if top:
            tools.append(cq.Solid.makeCylinder(1.7, QL_H + 0.2, cq.Vector(x, y0 - 0.1, z), cq.Vector(0, 1, 0)))
            tools.append(cq.Solid.makeCylinder(3.25, 3.0, cq.Vector(x, y0 - 0.01, z), cq.Vector(0, 1, 0)))
        else:
            tools.append(cq.Solid.makeCylinder(1.25, 7.0, cq.Vector(x, y0 - 0.01, z), cq.Vector(0, 1, 0)))
    for v, y in rear_screw_points():
        if y0 < y < y0 + QL_H:
            tools.append(cq.Solid.makeCylinder(1.25, 7.0, cq.Vector(-v, y, z0 - 0.01), cq.Vector(0, 0, 1)))
    q = q.cut(cq.Workplane("XY").add(cq.Compound.makeCompound(tools)))
    return cq.Workplane("XY").add(q.val().Solids()[0])


def make_rear_connectors():
    """Platzhalter der Buchsenkörper hinter der Rückwand (für Kollisionsprüfung/Platzplan): {key: Workplane}."""
    out = {}
    for c in RP_CONN:
        key, v, y, (b, h, d) = c[0], c[3], c[4], c[6]
        out[key] = cq.Workplane("XY").box(b, h, d, centered=(True, True, False)).translate((-v, y, Z_REAR + RP_T + 0.05))
    return out


def tab_screw_points():
    """(x, y_Außenfläche, sy) je Laschenschraube."""
    return [(sx * (W / 2 - TAB_SCREW_U), sy * (H / 2 - (COVER_T if sy > 0 else BOT_IN)), sy) for sx in (1, -1) for sy in (1, -1)]


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
    shaft = (cq.Workplane("XY").workplane(offset=PWR_STEM + 1.5).circle(PWR_D / 2).extrude(CARRIER_T + PANEL_T - PWR_CB_DEPTH + 1.5)
             .faces(">Z").edges().fillet(1.5))
    return stem.union(collar).union(shaft)


# ---------------- Knopfplatine (Encoder + LED-Ring + Einschalttaster) ----------------
PCB_T = 1.6
PCB_OUTLINE = [(-34, -29.0), (34, -29.0), (34, 29.0), (-34, 29.0)]   # relativ zur Knopfachse; H = 78: zwischen den Flanschen (y ±30)
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
                                         .center(-12, -25.5).rect(15.9, 4.5).extrude(6.0))   # innerhalb Platinenkontur (H = 78)
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
    cq.exporters.export(make_bezel(), f"{out}/RD160_Front_Blende.step")
    cq.exporters.export(make_carrier(), f"{out}/RD160_Front_Traeger.step")
    cq.exporters.export(panel, f"{out}/RD160_Front_Plexiglas.step")
    cq.exporters.export(panel.section(PANEL_T / 2), f"{out}/RD160_Front_Plexiglas.dxf")
    cq.exporters.export(make_button_cap(), f"{out}/RD160_Tasterkappe.step")
    asm = (cq.Assembly()
           .add(make_bezel(), name="Blende", color=cq.Color(0.16, 0.16, 0.17))
           .add(make_carrier(), name="Traeger", color=cq.Color(0.45, 0.46, 0.48))
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
    chk = {"Blende": make_bezel(), "Traeger": make_carrier(), "Platte": panel.translate((0, 0, CARRIER_T)),
           "Seitenteil_r": make_side_panel(1), "Seitenteil_l": make_side_panel(-1),
           "Deckel": make_cover(), "Boden": make_bottom(), "Rueckwand": make_rear_panel(),
           "Schaum": make_foam(), "Schrauben": make_tab_screws()}
    chk["Knopfplatine"] = make_knob_pcb().translate((KNOB_X, 0, 0))
    chk["Querleiste_o"] = make_crossbar(True)
    chk["Querleiste_u"] = make_crossbar(False)
    _bu = list(make_rear_connectors().values())
    chk["Buchsen"] = cq.Workplane("XY").add(cq.Compound.makeCompound([b.val() for b in _bu]))
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
