import time
import random
import RPi.GPIO as GPIO
from shifter import Shifter

# LED driver pins (BCM)
data  = 23
latch = 24
clock = 25

# Button pins (BCM)
start  = 17
toggle = 27
speed  = 22

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for p in (start, toggle, speed):
    GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


class GlowBug:
    def __init__(self, delay=0.1, start_at=3, wrap=False):
        self.delay = float(delay)
        self.index = int(start_at) % 8
        self.wrap = bool(wrap)
        self._drv = Shifter(data, latch, clock)
        self.active = False

    def play(self):
        self.active = True

    def pause(self):
        self.active = False
        self._drv.shiftByte(0)

    def tick(self, dt):
        if not self.active:
            return
        self._drv.shiftByte(1 << self.index)
        self.index += -1 if random.random() < 0.5 else 1
        if self.wrap:
            self.index %= 8
        else:
            if self.index < 0:
                self.index = 0
            elif self.index > 7:
                self.index = 7
        time.sleep(dt)


bug = GlowBug()


def on_toggle_wrap(channel):
    bug.wrap = not bug.wrap
    print(f"Wrap mode: {bug.wrap}")


GPIO.add_event_detect(toggle, GPIO.RISING, callback=on_toggle_wrap, bouncetime=300)

try:
    while True:
        if GPIO.input(start):
            if not bug.active:
                bug.play()
        else:
            if bug.active:
                bug.pause()
        dt = bug.delay / 3 if GPIO.input(speed) else bug.delay
        bug.tick(dt)
except KeyboardInterrupt:
    pass
finally:
    bug.pause()
    GPIO.cleanup()


