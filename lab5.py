import RPi.GPIO as GPIO
import math
import time

GPIO.setmode(GPIO.BCM)

list = [25, 5, 6, 13, 19, 26, 12, 16, 20, 21]    # GPIO pin numbers
list_objects = {}
f = 500    # frequency (Hz)
phase = math.pi / 9    # phase shift (radians)

# set up all pins and create PWM objects
for x in list:
    GPIO.setup(x, GPIO.OUT)
    list_objects[x] = GPIO.PWM(x, f)
    list_objects[x].start(0)   # start at 0% duty cycle

try:       # initiate PWM object
    while True:
        t = time.time()
        for i, x in enumerate(list):
            # Apply phase shift INSIDE the sine function
            b = (math.sin(2 * math.pi * f * t + i * phase)) ** 2 * 100
            list_objects[x].ChangeDutyCycle(b)

except KeyboardInterrupt:   # stop gracefully on ctrl-C
    print('\nExiting')

finally:
    for pwm in list_objects.values():
        pwm.stop()
    GPIO.cleanup()
