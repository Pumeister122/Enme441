import time
import RPi.GPIO as GPIO

class Shifter:
    def __init__(self, data_pin, latch_pin, clock_pin):
        # Save the pin numbers
        self.data_pin = data_pin
        self.latch_pin = latch_pin
        self.clock_pin = clock_pin

        # Set up the pins for output
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.data_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.latch_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.clock_pin, GPIO.OUT, initial=GPIO.LOW)

    def _pulse(self, pin):
        # Make a quick HIGH then LOW pulse
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.00001)

    def write_byte(self, value):
        # Send one byte (8 bits) to the shift register
        for bit in range(8):
            bit_value = (value >> bit) & 1
            GPIO.output(self.data_pin, bit_value)
            self._pulse(self.clock_pin)
        # Update outputs
        self._pulse(self.latch_pin)

    def clear(self):
        # Turn all LEDs off
        self.write_byte(0)
