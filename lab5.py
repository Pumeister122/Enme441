import RPi.GPIO as GPIO
import math
import time

GPIO.setmode(GPIO.BCM)

button = 4

list = [25, 5, 6, 13, 19, 26, 12, 16, 20, 21]    # GPIO pin numbers
list_objects = {}
f = 0.2    # frequency (Hz)
phase = math.pi / 9 * direction
direction = 1
# set up all pins and create PWM objects
for x in list:
    GPIO.setup(x, GPIO.OUT)
    list_objects[x] = GPIO.PWM(x, 500)
    list_objects[x].start(0)   # start at 0% duty cycle

def myCallback(pin):
    global direction
    direction *= -1

GPIO.add_event_detect(button,gpio.RISING,callback=myCallback,bouncetime = 100)


try:       # initiate PWM object
    while True:
        t = time.time()
        for i, x in enumerate(list):
            b = (math.sin(2 * math.pi * f * t + i * phase)) ** 2 * 100
            list_objects[x].ChangeDutyCycle(b)

except KeyboardInterrupt:   # stop gracefully on ctrl-C
    print('\nExiting')

finally:
    for pwm in list_objects.values():
        pwm.stop()
    GPIO.cleanup()

