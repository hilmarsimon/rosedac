"""Fertigungszeichnung (A3, PDF) + Vorschau aus den Parametern in frontplatte.py."""
import os, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import frontplatte as f

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
A3 = (16.54, 11.69)
LW = 0.7
MARK = {"Chassis": "A", "Taster-PCB": "B", "LED/Encoder-PCB": "C", "Display": "D"}
SPEC = {"Chassis": "M3 T4 von hinten in Flansch, Kernloch Ø2,5 T5", "Taster-PCB": "M3, T6, Kernloch Ø2,5 T7",
        "LED/Encoder-PCB": "M3, T6, Kernloch Ø2,5 T7", "Display": "Ø2,7 durch Flansch, Senkung 90° Ø5,2 von hinten"}


def all_holes():
    """Name -> Punkte (Vorderansicht): Träger-Rückseite + Flanschrückseite."""
    d = dict(f.M3_HOLES)
    d["Chassis"] = f.CHASSIS_PTS
    d["Display"] = f.DISP_SCREW_PTS
    return d


def rr(ax, cx, cy, w, h, r, **kw):
    kw.setdefault("lw", LW); kw.setdefault("fill", False)
    ax.add_patch(FancyBboxPatch((cx - w / 2 + r, cy - h / 2 + r), w - 2 * r, h - 2 * r,
                                boxstyle=f"round,pad={r}", **kw))


def dim_h(ax, x1, x2, y, txt):
    ax.annotate("", (x1, y), (x2, y), arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0))
    ax.text((x1 + x2) / 2, y + 1.2, txt, ha="center", va="bottom", fontsize=6.5)


def dim_v(ax, y1, y2, x, txt):
    ax.annotate("", (x, y1), (x, y2), arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0))
    ax.text(x - 1.2, (y1 + y2) / 2, txt, ha="right", va="center", fontsize=6.5, rotation=90)


def ext(ax, x, y1, y2):
    ax.plot([x, x], [y1, y2], lw=0.3, color="0.4")


def note(ax, xy, txy, txt):
    ax.annotate(txt, xy, txy, fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.4))


def setup(ax, xpad=30, ypad=30):
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-f.W / 2 - xpad, f.W / 2 + xpad)
    ax.set_ylim(-f.H / 2 - ypad - 10, f.H / 2 + ypad)


def front_view(ax):
    ax.add_patch(Rectangle((-f.W / 2, -f.H / 2), f.W, f.H, fill=False, lw=1.0))
    rr(ax, 0, 0, f.POCKET_W, f.POCKET_H, f.FRAME_R)
    # verdeckt hinter Platte
    ax.add_patch(Rectangle((f.DISP_X - f.PNL_W / 2, -f.PNL_H / 2), f.PNL_W, f.PNL_H, fill=False, lw=0.5, ls="--"))
    ax.add_patch(Circle((f.KNOB_X, 0), f.RING_OD / 2, fill=False, lw=0.5, ls="--"))
    ax.add_patch(Circle((f.KNOB_X, 0), f.RING_ID / 2, fill=False, lw=0.5, ls="--"))
    for x, y in f.btn_positions():
        ax.add_patch(Circle((x, y), f.BTN_HOLE_D / 2, fill=False, lw=LW))
    ax.add_patch(Circle((f.KNOB_X, 0), f.SHAFT_HOLE_D / 2, fill=False, lw=LW))
    ax.add_patch(Circle((f.PWR_X, f.PWR_Y), f.PWR_HOLE_D / 2, fill=False, lw=LW))
    ax.add_patch(Circle((f.KNOB_X, 0), f.KNOB_D / 2, fill=False, lw=0.4, ls=":", color="0.4"))
    note(ax, (f.PWR_X, f.PWR_Y + f.PWR_HOLE_D / 2), (185, 52), f"Einschalttaster Ø{f.PWR_HOLE_D} durch")
    for x in (f.DISP_X, f.KNOB_X, f.BTN_X0 + 2 * f.BTN_PITCH_X):
        ax.plot([x, x], [-f.H / 2 - 4, f.H / 2 + 4], lw=0.3, ls="-.", color="0.3")
    ax.plot([-f.W / 2 - 4, f.W / 2 + 4], [0, 0], lw=0.3, ls="-.", color="0.3")

    yb = -f.H / 2 - 10
    dim_h(ax, -f.W / 2, f.W / 2, yb - 12, f"{f.W:.0f}")
    dim_h(ax, -f.W / 2, f.BTN_X0, yb, f"{f.BTN_X0 + f.W / 2:.0f}")
    dim_h(ax, f.BTN_X0, f.BTN_X0 + 4 * f.BTN_PITCH_X, yb, f"4 × {f.BTN_PITCH_X:.0f}")
    dim_h(ax, f.DISP_X - f.PNL_W / 2, f.DISP_X + f.PNL_W / 2, yb, f"{f.PNL_W:.0f} (Display, verdeckt)")
    dim_h(ax, f.KNOB_X, f.W / 2, yb, f"{f.W / 2 - f.KNOB_X:.0f}")
    for x in (f.BTN_X0, f.BTN_X0 + 4 * f.BTN_PITCH_X, f.DISP_X - f.PNL_W / 2, f.DISP_X + f.PNL_W / 2, f.KNOB_X):
        ext(ax, x, -5, yb - 1)
    for x in (-f.W / 2, f.W / 2):
        ext(ax, x, -f.H / 2, yb - 13)
    dim_v(ax, -f.H / 2, f.H / 2, -f.W / 2 - 8, f"{f.H:.0f}")
    dim_v(ax, -f.POCKET_H / 2, f.POCKET_H / 2, -f.W / 2 + 14, f"{f.POCKET_H:.0f}")
    dim_v(ax, f.BTN_ROWS_Y[1], f.BTN_ROWS_Y[0], f.BTN_X0 - 7, f"{f.BTN_ROWS_Y[0] - f.BTN_ROWS_Y[1]:.0f}")

    note(ax, (-120, f.POCKET_H / 2), (-150, 62),
         f"Fenster Blende {f.POCKET_W:.0f}×{f.POCKET_H:.0f}, R{f.FRAME_R:.0f}, Lippe {f.LIP_T}, Fase {f.LIP_CH} "
         f"(Rand {f.FRAME_B:.0f} mm)")
    note(ax, (f.BTN_X0 + 4 * f.BTN_PITCH_X, f.BTN_ROWS_Y[0]), (-215, 52), f"10× Ø{f.BTN_HOLE_D} H9 durch")
    note(ax, (f.KNOB_X - f.RING_OD / 2 * 0.7, f.RING_OD / 2 * 0.7), (110, 62),
         f"Lichtkanal Ø{f.RING_ID:.0f}/Ø{f.RING_OD:.0f}, T {f.RING_FRONT_DEPTH:.0f} ab Taschenboden")
    note(ax, (f.KNOB_X, -f.SHAFT_HOLE_D / 2), (175, -62), f"Ø{f.SHAFT_HOLE_D:.0f} durch")
    ax.set_title("ALU-RAHMEN – VORDERANSICHT (gestrichelt: hinter der Plexiglasplatte)", fontsize=9, loc="left")


def rear_view(ax):
    m = -1
    ax.add_patch(Rectangle((-f.W / 2, -f.H / 2), f.W, f.H, fill=False, lw=1.0))
    ax.add_patch(Rectangle((m * f.DISP_X - f.PNL_W / 2, -f.PNL_H / 2), f.PNL_W, f.PNL_H, fill=False, lw=LW))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ax.add_patch(Circle((m * (f.DISP_X + sx * (f.PNL_W / 2 - 0.6)), sy * (f.PNL_H / 2 - 0.6)),
                                2.0, fill=False, lw=LW))
    ax.plot([0, 0], [-f.PNL_H / 2, f.PNL_H / 2], lw=0.4, ls="--", color="0.3")
    ax.text(1.5, -f.PNL_H / 2 + 2, "Stoß Panel 1 | 2", fontsize=6)
    for x, y in f.btn_positions():
        ax.add_patch(Circle((m * x, y), f.BTN_CB_D / 2, fill=False, lw=LW))
        ax.add_patch(Circle((m * x, y), f.BTN_HOLE_D / 2, fill=False, lw=0.4))
    ax.add_patch(Circle((m * f.PWR_X, f.PWR_Y), f.PWR_CB_D / 2, fill=False, lw=LW))
    ax.add_patch(Circle((m * f.PWR_X, f.PWR_Y), f.PWR_HOLE_D / 2, fill=False, lw=0.4))
    kx = m * f.KNOB_X
    for d in (f.LIGHT_OD, f.LIGHT_ID, f.BEARING_D, f.SHAFT_HOLE_D):
        ax.add_patch(Circle((kx, 0), d / 2, fill=False, lw=LW))
    for a in (45, 135, 225, 315):
        r1, r2 = f.LIGHT_ID / 2, f.LIGHT_OD / 2
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        for o in (-f.BRIDGE_W / 2, f.BRIDGE_W / 2):
            ax.plot([kx + r1 * c - o * s, kx + r2 * c - o * s], [r1 * s + o * c, r2 * s + o * c], lw=LW, color="k")
    for k, pts in all_holes().items():
        for x, y in pts:
            ax.add_patch(Circle((m * x, y), 1.5, fill=False, lw=LW))
            ax.plot([m * x - 2.2, m * x + 2.2], [y, y], lw=0.3, color="0.3")
            ax.plot([m * x, m * x], [y - 2.2, y + 2.2], lw=0.3, color="0.3")
            ax.text(m * x + 2, y + 2, MARK[k], fontsize=5.5)
    note(ax, (-40, f.PNL_H / 2), (-60, 62),
         f"Displaytasche {f.PNL_W:.0f}×{f.PNL_H:.0f}, T {f.PNL_DEPTH:.0f} (durch Träger bis Fronttasche)\n4× Eckfreistich Ø4")
    note(ax, (m * f.BTN_X0, -f.BTN_ROWS_Y[0]), (150, -64), f"10× Senkung Ø{f.BTN_CB_D:.0f}, T {f.BTN_CB_DEPTH:.0f}")
    note(ax, (kx, f.BEARING_D / 2), (-215, 62),
         f"Lagersitz Ø{f.BEARING_D:.0f} H7, T {f.BEARING_DEPTH:.0f} (6805-2RS)\n"
         f"Lichttasche Ø{f.LIGHT_ID:.0f}/Ø{f.LIGHT_OD:.0f}, T {f.LIGHT_DEPTH:.0f}, 4 Stege {f.BRIDGE_W:.0f} mm")
    ax.text(-f.W / 2, -f.H / 2 - 22,
            "A–C: M3 Sackloch, D: Displaybefestigung M2,5 (Tabelle Blatt 2)", fontsize=6.5)
    ax.set_title("ALU-RAHMEN – RÜCKANSICHT (Blick von hinten, gespiegelt)", fontsize=9, loc="left")


def titleblock(fig, sheet):
    fig.text(0.02, 0.02,
             f"RD160-Nachbau · Front · Blatt {sheet}/2 · Maße mm · A3 · Allgemeintoleranz ISO 2768-m · "
             "Quelle: frontplatte.py (STEP maßgebend)", fontsize=7)


def sheet1(pdf):
    fig = plt.figure(figsize=A3)
    ax1 = fig.add_axes([0.03, 0.52, 0.94, 0.44]); setup(ax1); front_view(ax1)
    ax2 = fig.add_axes([0.03, 0.06, 0.94, 0.44]); setup(ax2); rear_view(ax2)
    titleblock(fig, 1); pdf.savefig(fig); plt.close(fig)


def sheet2(pdf):
    fig = plt.figure(figsize=A3)
    rows = [[MARK[k], k, f"{x:+.1f}", f"{y:+.1f}", SPEC[k]]
            for k, pts in all_holes().items() for x, y in pts]
    ax = fig.add_axes([0.03, 0.40, 0.45, 0.55]); ax.axis("off")
    tb = ax.table(cellText=rows, colLabels=["Pos", "Zweck", "X (Front)", "Y", "Gewinde"], loc="upper left",
                  cellLoc="left", colWidths=[0.07, 0.30, 0.15, 0.12, 0.36])
    tb.auto_set_font_size(False); tb.set_fontsize(7); tb.scale(1, 1.25)
    ax.set_title("GEWINDETABELLE (Ursprung Plattenmitte, X rechts in Vorderansicht)", fontsize=9, loc="left")

    notes = [
        "FRONT ZWEITEILIG: BLENDE + TRÄGER (Alu) – FERTIGUNG",
        f"1. EN AW-6061-T6, Rohteil {f.W:.0f} × {f.H:.0f} × {f.DEPTH + f.TAB_L:.0f} mm. Glasperlstrahlen fein (alle Flächen inkl. Taschenböden),",
        "   danach Eloxal Typ II schwarz matt, verdichtet. Schichtdicke 10–15 µm.",
        f"   ABDECKEN (nicht eloxieren): Lagersitz Ø{f.BEARING_D:.0f} H7 + Bohrung Ø{f.SHAFT_HOLE_D:.0f}; Ringfläche Ø8 um die 6 Bohrungen A",
        "   auf der Flanschrückseite (Masseverbindung zum Chassis). Gewinde M3 dürfen eloxiert sein.",
        f"2. Außenkanten vorn Fase {f.EDGE_CHAMFER}×45°, sonst gratfrei.",
        f"3. BLENDE: Fenster {f.POCKET_W:.0f}×{f.POCKET_H:.0f} R{f.FRAME_R:.0f} in Lippe {f.LIP_T}, Fase {f.LIP_CH}×45° vorn; Falz von hinten "
        f"{2 * f.RAB_X:.1f}×{2 * f.RAB_Y:.1f} R{f.RAB_R:.1f}\n   durch bis hinten (Wand {f.W / 2 - f.RAB_X:.1f}); Ecken oben/unten hinter dem Band bleiben stehen. "
        f"{len(f.BZ_SCREW_X)}× Ø2,8 + Senkung 90° Ø5,5 von unten (M2,5).",
        f"4. TRÄGER: Außenmaß {2 * (f.RAB_X - f.BZ_CLR):.1f}×{2 * (f.RAB_Y - f.BZ_CLR):.1f}, Vorderseite {f.SEAT_GAP} hinter der Platte; "
        f"Displaytasche durch; {len(f.BZ_SCREW_X)}× M2,5 von unten.",
        f"5. Lagersitz Ø{f.BEARING_D:.0f} H7 T{f.BEARING_DEPTH:.0f} von hinten (6805-2RS), Laufbohrung Ø{f.SHAFT_HOLE_D:.0f} H8 vorn.",
        "6. Lichtkanal + Lichttasche ergeben einen Ring mit 4 Stegen (Insel bleibt verbunden).",
        "7. Gewinde M3 nach Tabelle, alle von hinten, nicht durchgehend.",
        f"8. Ober-/Unterkante: Flansch nach hinten, Gesamttiefe {f.DEPTH:.0f}, Höhe {f.FL_H:.0f}; Band {f.BAND:.0f} voll hoch;",
        f"   Seitenwände {f.END_W:.0f} breit, volle Höhe und Tiefe. Laschen waagerecht oben/unten {f.TAB_W:.0f} × {f.TAB_T:.0f} × {f.TAB_L:.0f},",
        f"   {f.TAB_U0:.0f}..{f.TAB_U0 + f.TAB_W:.0f} vom Außenrand; Ø3,4 + Senkung 90° Ø6,6 von außen, Achse {f.T - f.TAB_SCREW_Z:.0f} hinter Front (ISO 10642 M3×{f.SCREW_LEN}).",
        f"   Innenecken Auflage/Seitenwand senkrecht R{f.SEAT_R:.0f} (oben und unten).\n   OBEN: Nut {f.GROOVE_H}×{f.GROOVE_D:.0f} in Bandrückseite, Steg {f.GROOVE_TOP:.0f} darüber (Scheibenfräser Ø{2*f.CUTTER_R:.0f}, Auslauf R{f.CUTTER_R:.0f});\n   Auflage {f.SEAT_L:.0f} tief, {f.SEAT_D} unter Oberkante (Deckel {f.COVER_T:.0f} + Schaum {f.FOAM_C}).",
        f"   UNTEN: Absatz {f.BOT_ABS_FRONT:.0f} × {f.BOT_T:.0f} an der Rückseite für das Bodenblech, 3× M3 T6 von unten (x {', '.join(f'{x:.0f}' for x in f.BOT_FL_X)}).",
        "",
        "PLEXIGLASPLATTE (Laserzuschnitt, DXF)",
        f"• {f.PANEL_W:.1f}×{f.PANEL_H:.1f}×{f.PANEL_T:.0f}, R{f.PANEL_R:.1f}, "
        f"10× Ø{f.BTN_PANEL_D}, 1× Ø{f.SHAFT_PANEL_D}.",
        "• PLEXIGLAS LED Black & White 9H04 SC (matt) oder 7H25 GT (glänzend).",
        f"• Von hinten in die Blende, {f.PANEL_OVL} mm unter der Lippe, {f.PANEL_GAP} mm Dehnspalt je Seite (PMMA ~3× Alu).",
        "  Nicht kleben: Träger drückt über Poron-Streifen 0,8 mm (außerhalb Display/Ring) gegen die Lippe.",
        "• Rückseite außerhalb Display und Ring nicht hell lackieren – Alu dahinter ist schwarz.",
        "",
        "ÜBRIGE TEILE",
        f"• Display: 2× Waveshare 5,5\" HDMI AMOLED, quer, Stoß in X={f.DISP_X}, Deckglas je {f.DISP_GW}×{f.DISP_GH} R{f.DISP_GR:.0f}, Glas an der Platte.",
        "  Je 3 Bolzen (D) mit ISO 10642 M2,5×8 von hinten durch die Flansche, Silikonscheibe 0,5 im Spalt 0,3 (Vorspannung).",
        f"  Unterer Flansch je Display ausgespart (x' {f.DISP_NOTCH_X[0]:.0f}..{f.DISP_NOTCH_X[1]:.0f}) für Winkelstecker HDMI/USB.",
        f"• Tasterkappe 10× Alu: Stößel Ø3×4,2, Bund Ø8,6×1,5, Schaft Ø6×{f.CARRIER_T + f.PANEL_T - f.BTN_CB_DEPTH + 1.5:.1f}.",
        "  Omron B3F-1000 auf PCB, Abstandsbolzen M3×5 an Pos. B.",
        "• Drehknopf: Becher mit Nabe Ø25 k6 in 6805-2RS, Haltescheibe hinten; O-Ring 26×2 + Nyogel = Dämpfung.",
        "  Knopfplatine an Pos. C (4-mm-Bolzen): AS5600 unter Diametralmagnet + 12 LEDs, wie RD160.",
        f"• LED-Ring: 12 weiße SMD-LEDs auf PCB C, Teilkreis Ø{f.WIN_PCD:.1f}, PWM-gedimmt. Licht geht durch",
        "  Plexiglas + Lichtfenster im Knopfboden in das PMMA-Rohr und leuchtet an der Knopfvorderkante.",
        f"• Einschalttaster: Kappe Ø{f.PWR_D:.0f}, Bund Ø{f.PWR_CB_D - 0.4:.1f}, Senkung Ø{f.PWR_CB_D:.0f} T{f.PWR_CB_DEPTH:.0f}; B3F-1000.",
    ]
    fig.text(0.52, 0.95, "\n".join(notes), fontsize=7.5, va="top")

    ax3 = fig.add_axes([0.05, 0.06, 0.40, 0.28]); ax3.set_aspect("equal"); ax3.axis("off")
    sl = f.T - f.BTN_CB_DEPTH + 1.5
    ax3.add_patch(Rectangle((-1.5, 0), 3, 4.2, fill=False, lw=LW))
    ax3.add_patch(Rectangle((-4.3, 4.2), 8.6, 1.5, fill=False, lw=LW))
    ax3.add_patch(Rectangle((-3.0, 5.7), 6.0, sl, fill=False, lw=LW))
    ax3.set_xlim(-14, 14); ax3.set_ylim(-2, 17)
    ax3.text(5, 9, f"Ø6 × {sl:.1f} (1,5 Überstand)", fontsize=6.5)
    ax3.text(5, 4.6, "Bund Ø8,6 × 1,5", fontsize=6.5)
    ax3.text(2, 1.5, "Stößel Ø3 × 4,2", fontsize=6.5)
    ax3.set_title("Tasterkappe (Seitenansicht, Front oben)", fontsize=8, loc="left")
    titleblock(fig, 2); pdf.savefig(fig); plt.close(fig)


def preview(path):
    fig = plt.figure(figsize=(14, 3.4), facecolor="white")
    ax = fig.add_axes([0.01, 0.02, 0.98, 0.96]); setup(ax, 8, 4); ax.set_ylim(-f.H / 2 - 4, f.H / 2 + 4)
    ax.add_patch(Rectangle((-f.W / 2, -f.H / 2), f.W, f.H, color="#3a3b3e"))
    rr(ax, 0, 0, f.PANEL_W, f.PANEL_H, f.FRAME_R, fill=True, color="#131415", lw=0)
    for x, y in f.btn_positions():
        ax.add_patch(Circle((x, y), 3.0, color="#8a8c90"))
    # Hohlknopf: schwarzer Becher, leuchtende Lippe, Konus, Mittelscheibe
    ax.add_patch(Circle((f.KNOB_X + 1.2, -1.2), f.KNOB_D / 2, color="#08090a"))
    ax.add_patch(Circle((f.KNOB_X, 0), f.KNOB_D / 2, color="#1c1d1f"))
    ax.add_patch(Circle((f.KNOB_X, 0), f.TUBE_OD / 2, color="#f4f6f8"))
    ax.add_patch(Circle((f.KNOB_X, 0), f.TUBE_ID / 2, color="#2e2f33"))
    for i, r in enumerate(range(int(f.INS_OD / 2), int(f.CONE_FLOOR_D / 2), -1)):
        ax.add_patch(Circle((f.KNOB_X, 0), r, color=str(0.16 + 0.012 * i)))
    ax.add_patch(Circle((f.KNOB_X, 0), f.CONE_FLOOR_D / 2 - 1, color="#3a3b3f"))
    ax.add_patch(Circle((f.PWR_X, f.PWR_Y), f.PWR_D / 2, color="#8a8c90"))
    ax.add_patch(Circle((f.PWR_X, f.PWR_Y), 2.6, fill=False, ec="#2a2b2d", lw=1.0)); ax.plot([f.PWR_X, f.PWR_X], [f.PWR_Y, f.PWR_Y + 3.2], color="#2a2b2d", lw=1.2)
    for i, lab in enumerate(["USB", "AK4199", "AK4399", "OUT"]):
        x = -92 + i * 61
        ax.add_patch(Rectangle((x - 15, -7), 30, 14, fill=False, ec="#e8e8e2", lw=1.2))
        ax.text(x, 0, lab, color="#e8e8e2", ha="center", va="center", fontsize=8, weight="bold")
        if i < 3:
            ax.annotate("", (x + 46, 0), (x + 15, 0), arrowprops=dict(arrowstyle="->", color="#e8e8e2", lw=1.2))
    ax.text(-61, 19, "44.1 kHz · FIR SHARP", color="#e8e8e2", ha="center", fontsize=8)
    ax.text(61, 19, "VOL −20 dB", color="#e8e8e2", ha="center", fontsize=8)
    fig.savefig(path, dpi=160); plt.close(fig)


if __name__ == "__main__":
    with PdfPages(os.path.join(OUTDIR, "RD160_Front_Zeichnung.pdf")) as pdf:
        sheet1(pdf); sheet2(pdf)
    preview(os.path.join(OUTDIR, "RD160_Front_Vorschau.png"))
    print("ok")
