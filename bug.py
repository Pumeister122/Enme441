import time
import random
import RPi.GPIO as GPIO
from shifter import SR595

# Pins (BCM)
LED_SER  = 23
LED_RCLK = 24
LED_SRCK = 25

BTN_WRAP = 27  # only button we use

class Firefly:
    def __init__(self, step_time: float = 0.1, pos: int = 3, wrap_enabled: bool = False):
        # How fast the light moves
        self.step_time = float(step_time)
        self._base_time = float(step_time)

        # Which LED is on (0..7)
        self.pos = int(pos) % 8

        # If True, go around at the ends; else stop at edges
        self.wrap_enabled = bool(wrap_enabled)

        # Talks to the 74HC595 chip
        self._driver = SR595(LED_SER, LED_RCLK, LED_SRCK)

        # Always running in this version
        self._active = True

    def set_speed_multiplier(self, k: float):
        # Bigger k = faster (smaller delay)
        k = max(1.0, float(k))
        self.step_time = max(0.001, self._base_time / k)

    def _render(self):
        # Turn on only the LED at "pos"
        self._driver.write_byte(1 << self.pos, lsb_first=True)

    def _advance_once(self):
        # Move one step left or right randomly
        delta = -1 if random.random() < 0.5 else 1
        nxt = self.pos + delta

        if self.wrap_enabled:
            # Go around if we pass the ends
            self.pos = nxt % 8
        else:
            # Stay inside 0..7
            if nxt < 0:
                self.pos = 0
            elif nxt > 7:
                self.pos = 7
            else:
                self.pos = nxt

    def tick(self):
        # Do one move, then wait a bit
        if not self._active:
            return
        self._render()
        self._advance_once()
        time.sleep(self.step_time)


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Button 2 as input with pull-up (pressed = LOW)
    GPIO.setup(BTN_WRAP, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    bug = Firefly()

    # When Button 2 changes, flip wrap mode
    def on_wrap_edge(channel: int):
        bug.wrap_enabled = not bug.wrap_enabled

    # Watch Button 2 for changes (small debounce)
    GPIO.add_event_detect(BTN_WRAP, GPIO.BOTH, callback=on_wrap_edge, bouncetime=50)

    try:
        while True:
            # Keep the bug moving
            bug.tick()
            time.sleep(0.005)
    except KeyboardInterrupt:
        pass
    finally:
        # Clean up
        try:
            GPIO.remove_event_detect(BTN_WRAP)
        except Exception:
            pass
        bug._driver.clear()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
