import time
import random
import RPi.GPIO as GPIO
from shifter import Shifter

# LED driver pins (BCM)
DATA_PIN  = 23
LATCH_PIN = 24
CLOCK_PIN = 25

# Button pins (BCM)
BTN_START  = 17  # start/stop
BTN_TOGGLE = 27  # toggle wrap
BTN_SPEED  = 22  # 3x speed

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
for p in (BTN_START, BTN_TOGGLE, BTN_SPEED):
    GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


class GlowBug:
    def __init__(self, delay=0.1, start_at=3, wrap=False):
        # How long to wait between moves
        self.delay = float(delay)
        # Which LED is on (0..7)
        self.index = int(start_at) % 8
        # Wrap around ends or stop at edges
        self.wrap = bool(wrap)
        # Chip that controls the LEDs
        self._drv = Shifter(DATA_PIN, LATCH_PIN, CLOCK_PIN)
        # Is it moving right now?
        self.active = False

    def play(self):
        # Start moving
        self.active = True

    def pause(self):
        # Stop moving and turn off LEDs
        self.active = False
        self._drv.shiftByte(0)

    def tick(self, dt):
        # Do one move if we are running
        if not self.active:
            return

        # Light up only the current LED
        self._drv.shiftByte(1 << self.index)

        # Move left or right randomly
        self.index += -1 if random.random() < 0.5 else 1

        # Handle the ends
        if self.wrap:
            self.index %= 8
        else:
            if self.index < 0:
                self.index = 0
            elif self.index > 7:
                self.index = 7

        # Small pause so it doesn't go too fast
        time.sleep(dt)


bug = GlowBug()


def on_toggle_wrap(channel):
    # Flip wrap mode each time the button is pressed
    bug.wrap = not bug.wrap
    print(f"Wrap mode: {bug.wrap}")


# Watch only the toggle button (rising edge = press)
GPIO.add_event_detect(BTN_TOGGLE, GPIO.RISING, callback=on_toggle_wrap, bouncetime=300)

try:
    while True:
        # Start/stop: button HIGH = start, LOW = stop
        if GPIO.input(BTN_START):
            if not bug.active:
                bug.play()
        else:
            if bug.active:
                bug.pause()

        # Speed: button HIGH = 3x faster
        dt = bug.delay / 3 if GPIO.input(BTN_SPEED) else bug.delay

        # Advance one step
        bug.tick(dt)

except KeyboardInterrupt:
    pass
finally:
    # Clean up on exit
    bug.pause()
    GPIO.cleanup()
