import time
import RPi.GPIO as GPIO

class Shifter:
    def __init__(self, data_pin, latch_pin, clock_pin):
        self.data_pin = data_pin
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.data_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.latch_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.clock_pin, GPIO.OUT, initial=GPIO.LOW)

    def _pulse(self, pin):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.00001)

    def shiftByte(self, value):
        for bit in range(8):
            GPIO.output(self.data_pin, (value >> bit) & 1)
            self._pulse(self.clock_pin)
        self._pulse(self.latch_pin)

    def clear(self):
        self.shiftByte(0)
