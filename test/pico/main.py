# RD160-Nachbau – Test-Firmware RP2040 (Raspberry Pi Pico, MicroPython)
# Drehknopf AS5600 (I2C), 10 Taster + Einschalttaster, LED-Ring per PWM über MOSFET (AO3400A).
# Ereignisse als JSON-Zeilen über USB-Seriell an den Pi:   {"ev":"enc","d":+1}   {"ev":"btn","id":"MUTE"}
# Befehle vom Pi:                                           {"cmd":"led","v":0..255}
# Später ersetzt durch die C-Firmware der Steuerplatine (gleiches Protokoll, dann über UART + ISO7721).
import sys, json, select, time
from machine import I2C, Pin, PWM

# ---------------- Pinbelegung (Pico) ----------------
I2C_SDA, I2C_SCL = 4, 5                # AS5600 (Breakout mit 3,3 V versorgen, DIR an GND)
LED_PWM_PIN = 22                       # Gate AO3400A (100 Ω in Reihe, 100 kΩ nach GND)
BUTTONS = {                            # GPIO -> Name, Taster gegen GND, interner Pull-up
    10: "INPUT_UP", 11: "INPUT_DN", 12: "SAMPLING_UP", 13: "SAMPLING_DN", 14: "FILTER_UP",
    15: "FILTER_DN", 16: "DIMMING", 17: "MUTE", 18: "CLOCK_INPUT", 19: "SOUND_WAVE", 20: "PWR",
}
COUNTS_PER_STEP = 4096 // 48           # 48 Rastschritte je Umdrehung (7,5°) – im Test anpassen
DEBOUNCE_MS = 25

AS5600_ADDR, RAW_ANGLE = 0x36, 0x0C
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)
led = PWM(Pin(LED_PWM_PIN)); led.freq(25_000); led.duty_u16(0)   # ≥ 25 kHz: kein Flimmern/Pfeifen
pins = {g: Pin(g, Pin.IN, Pin.PULL_UP) for g in BUTTONS}
state = {g: 1 for g in BUTTONS}
changed_at = {g: 0 for g in BUTTONS}
poll = select.poll(); poll.register(sys.stdin, select.POLLIN)


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")


def angle():
    try:
        b = i2c.readfrom_mem(AS5600_ADDR, RAW_ANGLE, 2)
        return ((b[0] << 8) | b[1]) & 0x0FFF
    except OSError:
        return None


def set_led(v):
    v = max(0, min(255, int(v)))
    led.duty_u16((v * v * 65535) // (255 * 255))   # quadratisch: gleichmäßiger empfundene Helligkeit


def main():
    if AS5600_ADDR not in i2c.scan():
        send({"ev": "err", "msg": "AS5600 nicht gefunden (Verdrahtung/3,3 V prüfen)"})
    last, acc = angle(), 0
    set_led(255)
    line = ""
    while True:
        a = angle()
        if a is not None and last is not None:
            d = a - last
            if d > 2048: d -= 4096          # Überlauf 0/4095
            if d < -2048: d += 4096
            acc += d
            last = a
            steps = int(acc / COUNTS_PER_STEP)
            if steps:
                acc -= steps * COUNTS_PER_STEP
                send({"ev": "enc", "d": steps})
        elif a is not None:
            last = a
        now = time.ticks_ms()
        for g, p in pins.items():
            v = p.value()
            if v != state[g] and time.ticks_diff(now, changed_at[g]) > DEBOUNCE_MS:
                state[g], changed_at[g] = v, now
                if v == 0:
                    send({"ev": "btn", "id": BUTTONS[g]})
        while poll.poll(0):
            ch = sys.stdin.read(1)
            if ch == "\n":
                try:
                    cmd = json.loads(line)
                    if cmd.get("cmd") == "led":
                        set_led(cmd.get("v", 0))
                except ValueError:
                    pass
                line = ""
            else:
                line += ch
        time.sleep_ms(2)


main()
