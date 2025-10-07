import RPi.GPIO as GPIO
import math
import time
GPIO.setmode(GPIO.BCM)

list = [25, 5, 6, 13, 19, 26, 12, 16, 20, 21]    # GPIO pin number
list_objects = {}
#x1 = 25
#x2 = 5
#x3 = 6
#x4 = 13
#x5 = 19
#x6 = 26
#x7 = 12
#x8 = 16
#x9 = 20
#x10 = 21
f = 500    # frequency (Hz)

for x in list:
  GPIO.setup(x, GPIO.OUT)
  list_objects[x] = GPIO.PWM(x, f) # create PWM object




try:       # initiate PWM object
  while True:
    time = time.time()
    b = ((math.sin(2*math.pi*f*time))**2)*100
    pwm_objects[25].start(b)
    pwm_objects[5].start(b+(math.pi/9))
    pwm_objects[6].start(b+2*(math.pi/9))
    pwm_objects[13].start(b+3*(math.pi/9))
    pwm_objects[19].start(b+4*(math.pi/9))
    pwm_objects[26].start(b+5*(math.pi/9))
    pwm_objects[12].start(b+6*(math.pi/9)) 
    pwm_objects[16].start(b+7*(math.pi/9))
    pwm_objects[20].start(b+8*(math.pi/9))
    pwm_objects[21].start(b+9*(math.pi/9))   
    pass
except KeyboardInterrupt:   # stop gracefully on ctrl-C
  print('\nExiting')

pwm.stop()
GPIO.cleanup()
