#!/usr/bin/env python3
"""RD160-Nachbau – Test-UI für 2× Waveshare 5,5" HDMI AMOLED am Raspberry Pi 5.

Zeigt die Bedienoberfläche im Stil des Originals (weiße Linien auf Schwarz) auf zwei Displays
und Testbilder für den Plexiglas-Test. Eingaben kommen vom RP2040 (Drehknopf AS5600, Taster)
als JSON-Zeilen über USB-Seriell oder ersatzweise von der Tastatur.

Start (Pi OS Lite, ohne Desktop):  SDL_VIDEODRIVER=kmsdrm python3 rd160_ui.py
Entwicklung am PC (ein Fenster):   python3 rd160_ui.py --windowed
Optionen: --port /dev/ttyACM0  --rotate 0|90|180|270  --swap (Displays tauschen)

Tastatur: ←/→ Lautstärke · I/K Eingang · F/V Filter · S/X Abtastrate · D Dimmen · M Mute · W Wellenform
          P Standby · 1 Schwarz · 2 Weiß · 3 Graukeil · 4 UI · 5 Rahmen · 6 Schrift · Esc Ende
"""
import argparse, json, math, os, queue, random, sys, threading, time

import pygame
from pygame._sdl2.video import Window, Renderer, Texture

W, H = 1920, 1080                      # logische Auflösung je Display (quer)
WHITE = (255, 255, 255)
INPUTS = ["USB", "Coaxial 1", "Coaxial 2", "Optical", "AES/EBU", "HDMI I²S", "Network"]
RATES = ["44.1 kHz", "48 kHz", "88.2 kHz", "96 kHz", "176.4 kHz", "192 kHz", "384 kHz", "768 kHz", "DSD64", "DSD256", "DSD512"]
FILTERS = ["Sharp", "Slow", "Short Sharp", "Short Slow", "Super Slow"]
DIM = [1.0, 0.6, 0.3]
SDL_WINDOWPOS_CENTERED_DISPLAY = 0x2FFF0000


class State:
    def __init__(self):
        self.vol, self.mute, self.inp, self.rate, self.filt = 36, False, 0, 3, 0
        self.dim, self.wave_on, self.standby, self.pattern = 0, True, False, "ui"
        self.last_input_t = 0.0

    def handle(self, ev):
        """ev: dict wie vom RP2040: {"ev":"enc","d":n} | {"ev":"btn","id":"..."}"""
        self.last_input_t = time.monotonic()
        if ev.get("ev") == "enc":
            if not self.standby:
                self.vol = max(0, min(100, self.vol + int(ev.get("d", 0))))
                self.mute = False
            return None
        b = ev.get("id")
        if b == "PWR":
            self.standby = not self.standby
        elif self.standby:
            return None
        elif b == "INPUT_UP":
            self.inp = (self.inp - 1) % len(INPUTS)
        elif b == "INPUT_DN":
            self.inp = (self.inp + 1) % len(INPUTS)
        elif b == "SAMPLING_UP":
            self.rate = (self.rate - 1) % len(RATES)
        elif b == "SAMPLING_DN":
            self.rate = (self.rate + 1) % len(RATES)
        elif b == "FILTER_UP":
            self.filt = (self.filt - 1) % len(FILTERS)
        elif b == "FILTER_DN":
            self.filt = (self.filt + 1) % len(FILTERS)
        elif b == "DIMMING":
            self.dim = (self.dim + 1) % len(DIM)
        elif b == "MUTE":
            self.mute = not self.mute
        elif b == "SOUND_WAVE":
            self.wave_on = not self.wave_on
        elif b == "CLOCK_INPUT":
            pass
        return self.led_level()

    def led_level(self):
        return 0 if self.standby else int(255 * DIM[self.dim])


def serial_reader(port, q, outq):
    try:
        import serial
    except ImportError:
        print("pyserial fehlt: pip install pyserial – weiter nur mit Tastatur", file=sys.stderr)
        return
    while True:
        try:
            with serial.Serial(port, 115200, timeout=0.05) as s:
                print("RP2040 verbunden:", port, file=sys.stderr)
                buf = b""
                while True:
                    try:
                        while True:
                            s.write((json.dumps(outq.get_nowait()) + "\n").encode())
                    except queue.Empty:
                        pass
                    buf += s.read(256)
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        try:
                            q.put(json.loads(line.decode().strip()))
                        except (ValueError, UnicodeDecodeError):
                            pass
        except Exception as e:                       # Port fehlt / getrennt -> erneut versuchen
            time.sleep(1.0)


# ---------------------------------------------------------------- Zeichnen
class Painter:
    def __init__(self):
        pygame.font.init()
        name = pygame.font.match_font("dejavusans,liberationsans,arial")
        self.f = {s: pygame.font.Font(name, s) for s in (34, 40, 48, 56, 180)}

    def text(self, surf, s, size, pos, col, anchor="center"):
        img = self.f[size].render(s, True, col)
        r = img.get_rect(**{anchor: pos})
        surf.blit(img, r)
        return r

    def label(self, surf, s, cx, y, w, col):
        """Beschriftung mit Linie darunter wie beim Original (z. B. „INPUT“)."""
        pygame.draw.line(surf, col, (cx - w // 2, y), (cx + w // 2, y), 3)
        self.text(surf, s, 40, (cx, y + 36), col)

    def listbox(self, surf, items, sel, cx, y0, w, col, sub=None):
        """Liste wie beim Original; der gewählte Eintrag ist hervorgehoben, ggf. mit Zusatzzeile im Kasten."""
        gap, y = 18, y0
        for i, it in enumerate(items):
            h = 110 if (i == sel and sub) else 72
            r = pygame.Rect(cx - w // 2, y, w, h)
            pygame.draw.rect(surf, col, r, 5 if i == sel else 2, border_radius=6)
            if i == sel and sub:
                self.text(surf, it, 40, (cx, y + 34), col)
                self.text(surf, sub, 34, (cx, y + 80), col)
            else:
                self.text(surf, it, 40 if i == sel else 34, r.center, col)
            y += h + gap


def draw_left(p, s, st, col):
    s.fill((0, 0, 0))
    # INPUT: 5 Einträge um den gewählten herum
    n = len(INPUTS)
    win = [(st.inp + k) % n for k in range(-2, 3)]
    p.listbox(s, [INPUTS[i] for i in win], 2, 330, 150, 400, col, sub=RATES[st.rate])
    p.label(s, "INPUT  /  PCM DS", 330, 820, 460, col)
    # CLOCK + FILTER
    p.text(s, "CLOCK  Int.", 48, (960, 120), col)
    pts = [(1110 + k * 14, 120 + (22 if (k // 3) % 2 else -22)) for k in range(12)]
    pygame.draw.lines(s, col, False, pts, 3)
    p.listbox(s, FILTERS, st.filt, 960, 204, 380, col)
    p.label(s, "PCM FILTER", 960, 820, 420, col)
    # DAC-Block
    r = pygame.Rect(0, 0, 400, 300); r.center = (1590, 400)
    pygame.draw.rect(s, col, r, 3, border_radius=8)
    p.text(s, "Analog", 48, (1590, 330), col)
    p.text(s, "Converter", 48, (1590, 390), col)
    p.text(s, "DELTA  Σ", 48, (1590, 480), col)
    p.label(s, "D  A  C", 1590, 820, 380, col)


def draw_right(p, s, st, col, t):
    s.fill((0, 0, 0))
    # SOUND WAVE
    if st.wave_on and not st.mute:
        a = 0.15 + 0.85 * (st.vol / 100)
        pts = []
        for x in range(80, 900, 4):
            env = math.exp(-((x - 490) / 210) ** 2)
            y = 420 + env * a * 260 * math.sin(x * 0.07 + t * 9) * (0.6 + 0.4 * math.sin(x * 0.013 + t * 2))
            pts.append((x, y + random.uniform(-3, 3) * env))
        pygame.draw.lines(s, col, False, pts, 3)
    else:
        pygame.draw.line(s, col, (80, 420), (900, 420), 3)
    p.label(s, "SOUND WAVE", 490, 820, 520, col)
    # VOLUME: Kurve + Punkt + Zahl
    x0, y0, x1, y1 = 1060, 680, 1600, 160
    pygame.draw.line(s, col, (x0, y0), (x1 + 40, y0), 3)
    pygame.draw.line(s, col, (x0, y0), (x0, y1 - 20), 3)
    curve = [(x0 + (x1 - x0) * k / 100, y0 - (y0 - y1) * (k / 100) ** 2.2) for k in range(101)]
    pygame.draw.lines(s, col, False, curve, 3)
    cx, cy = curve[st.vol]
    pygame.draw.circle(s, col, (int(cx), int(cy)), 16, 3)
    pygame.draw.circle(s, col, (int(cx), int(cy)), 6)
    p.text(s, "MUTE" if st.mute else str(st.vol), 180 if not st.mute else 56, (1740, 520), col)
    p.label(s, "VOLUME", 1330, 820, 560, col)


def draw_pattern(p, s, name, which):
    if name == "black":
        s.fill((0, 0, 0))
    elif name == "white":
        s.fill(WHITE)
    elif name == "ramp":
        for i in range(16):
            v = int(255 * i / 15)
            pygame.draw.rect(s, (v, v, v), (i * W // 16, 0, W // 16 + 1, H))
    elif name == "frame":
        s.fill((0, 0, 0))
        pygame.draw.rect(s, WHITE, (0, 0, W, H), 4)
        pygame.draw.rect(s, WHITE, (40, 40, W - 80, H - 80), 1)
        pygame.draw.line(s, WHITE, (W // 2, 0), (W // 2, H), 1)
        pygame.draw.line(s, WHITE, (0, H // 2), (W, H // 2), 1)
        p.text(s, f"Display {which}: Außenrahmen = aktive Fläche, Innenrahmen 40 px", 40, (W // 2, H // 2 - 60), WHITE)
    elif name == "text":
        s.fill((0, 0, 0))
        for i, sz in enumerate((34, 40, 48, 56)):
            p.text(s, f"Schriftgröße {sz} px – Lesbarkeit durch Plexiglas (9H04 SC / 7H25 GT)", sz, (80, 120 + i * 140), WHITE, "midleft")
        for i, g in enumerate((255, 180, 120, 60, 30)):
            p.text(s, f"Grau {g}", 48, (200 + i * 340, 860), (g, g, g))


# ---------------------------------------------------------------- Hauptprogramm
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/ttyACM0")
    ap.add_argument("--rotate", type=int, default=0, choices=(0, 90, 180, 270))
    ap.add_argument("--swap", action="store_true")
    ap.add_argument("--windowed", action="store_true")
    ap.add_argument("--screenshot", metavar="DIR", help="je ein Bild beider Displays speichern und beenden")
    a = ap.parse_args()

    pygame.init()
    p = Painter()
    surfs = [pygame.Surface((W, H)), pygame.Surface((W, H))]
    if a.screenshot:
        st = State()
        for name in ("ui", "frame", "text"):
            st.pattern = name
            for i, s in enumerate(surfs):
                if name != "ui":
                    draw_pattern(p, s, name, i + 1)
                elif i == 0:
                    draw_left(p, s, st, WHITE)
                else:
                    draw_right(p, s, st, WHITE, 0.4)
                pygame.image.save(s, os.path.join(a.screenshot, f"display{i + 1}_{name}.png"))
        return
    wins = []
    if a.windowed:
        win = Window("RD160 Test-UI (beide Displays)", size=(1600, 450))
        wins = [(win, Renderer(win))]
    else:
        n = pygame.display.get_num_displays()
        if n < 2:
            print(f"Nur {n} Display gefunden – mit --windowed testen oder zweites HDMI prüfen.", file=sys.stderr)
        for i in range(min(2, n)):
            d = (1 - i) if a.swap else i
            w = Window(f"RD160 Display {i + 1}", size=(W, H) if a.rotate in (0, 180) else (H, W),
                       position=(SDL_WINDOWPOS_CENTERED_DISPLAY | d, SDL_WINDOWPOS_CENTERED_DISPLAY | d), fullscreen=True)
            wins.append((w, Renderer(w)))
        pygame.mouse.set_visible(False)

    st = State()
    q, outq = queue.Queue(), queue.Queue()
    threading.Thread(target=serial_reader, args=(a.port, q, outq), daemon=True).start()
    outq.put({"cmd": "led", "v": st.led_level()})
    keymap = {pygame.K_i: "INPUT_UP", pygame.K_k: "INPUT_DN", pygame.K_f: "FILTER_UP", pygame.K_v: "FILTER_DN",
              pygame.K_s: "SAMPLING_UP", pygame.K_x: "SAMPLING_DN", pygame.K_d: "DIMMING", pygame.K_m: "MUTE",
              pygame.K_w: "SOUND_WAVE", pygame.K_c: "CLOCK_INPUT", pygame.K_p: "PWR"}
    patterns = {pygame.K_1: "black", pygame.K_2: "white", pygame.K_3: "ramp", pygame.K_4: "ui", pygame.K_5: "frame", pygame.K_6: "text"}
    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    q.put({"ev": "enc", "d": -1 if e.key == pygame.K_LEFT else 1})
                elif e.key in keymap:
                    q.put({"ev": "btn", "id": keymap[e.key]})
                elif e.key in patterns:
                    st.pattern = patterns[e.key]
        while not q.empty():
            ev = q.get()
            lvl = st.handle(ev)
            if lvl is not None:
                outq.put({"cmd": "led", "v": lvl})
        t = time.monotonic()
        dimf = DIM[st.dim]
        col = tuple(int(255 * dimf) for _ in range(3))
        for i, s in enumerate(surfs):
            if st.standby:
                s.fill((0, 0, 0))
            elif st.pattern != "ui":
                draw_pattern(p, s, st.pattern, i + 1)
            elif i == 0:
                draw_left(p, s, st, col)
            else:
                draw_right(p, s, st, col, t)
        if a.windowed:
            win, ren = wins[0]
            both = pygame.Surface((W * 2 + 40, H))
            both.blit(surfs[0], (0, 0)); both.blit(surfs[1], (W + 40, 0))
            tex = Texture.from_surface(ren, pygame.transform.smoothscale(both, win.size))
            ren.clear(); tex.draw(); ren.present()
        else:
            for (win, ren), s in zip(wins, surfs):
                img = pygame.transform.rotate(s, -a.rotate) if a.rotate else s
                tex = Texture.from_surface(ren, img)
                ren.clear(); tex.draw(); ren.present()
        clock.tick(30)


if __name__ == "__main__":
    main()
