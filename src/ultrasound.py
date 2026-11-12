import time
import RPi.GPIO as GPIO
from env import Env
class Ultrasound:
    def __init__(self,env:Env):
        super().__init__()
        self.PIN_ECHO = env.PIN_ECHO
        self.PIN_TRIGGER = env.PIN_TRIGGER
        # redundancia
        if env.GPIO_MODE=='BOARD':  
            GPIO.setmode(GPIO.BOARD)
        else:
            GPIO.setmode(GPIO.BOARD)
        # redundancia
        GPIO.setup(self.PIN_ECHO, GPIO.IN)
        GPIO.setup(self.PIN_TRIGGER, GPIO.OUT, initial=GPIO.LOW)
        
    def distance(self) -> float:
        pulse_start_time = 0.0
        try:
            GPIO.output(self.PIN_TRIGGER, GPIO.LOW)
            time.sleep(0.05)
            GPIO.output(self.PIN_TRIGGER, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(self.PIN_TRIGGER, GPIO.LOW)
            while GPIO.input(self.PIN_ECHO)==0:
                pulse_start_time = time.time()
            while GPIO.input(self.PIN_ECHO)==1:
                pulse_end_time = time.time()
            if pulse_start_time == 0.0:
                return(-1.0)
            else:
                pulse_duration = pulse_end_time - pulse_start_time

                distance = round(pulse_duration * 17150, 2)
                
                return(distance)
        except OSError as ex:
            if ex.args[0] == 110: # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex
        
    def clean(self): 
        GPIO.cleanup()
