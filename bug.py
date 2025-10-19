import RPi.GPIO as GPIO
import time
import random
from shifter import Shifter

PIN_START = 17
PIN_TOGGLE = 27
PIN_SPEED = 22
PIN_DATA = 23
PIN_LATCH = 24
PIN_CLOCK = 25

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

for switch in [PIN_START, PIN_TOGGLE, PIN_SPEED]:
    GPIO.setup(switch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


class Light:
    def __init__(self, delay=0.1, position=3, wrap=False):
        self.delay = delay
        self.position = position
        self.wrap = wrap
        self._driver = Shifter(PIN_DATA, PIN_LATCH, PIN_CLOCK)
        self.running = False

    def begin(self):
        self.running = True

    def freeze(self):
        self.running = False
        self._driver.shiftByte(0)

    def move_once(self, pause):
        if not self.running:
            return
        self._driver.shiftByte(1 << self.position)
        self.position += random.choice([-1, 1])
        if self.wrap:
            self.position %= 8
        else:
            if self.position < 0:
                self.position = 0
            elif self.position > 7:
                self.position = 7
        time.sleep(pause)


light = Light()

def handle_wrap(channel):
    light.wrap = not light.wrap
    print("Wrap mode:", light.wrap)

GPIO.add_event_detect(PIN_TOGGLE, GPIO.RISING, callback=handle_wrap, bouncetime=300)

try:
    while True:
        if GPIO.input(PIN_START):
            if not light.running:
                light.begin()
        else:
            if light.running:
                light.freeze()
        if GPIO.input(PIN_SPEED):
            wait_time = light.delay / 3
        else:
            wait_time = light.delay
        light.move_once(wait_time)
except KeyboardInterrupt:
    light.freeze()
    GPIO.cleanup()

