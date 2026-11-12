import RPi.GPIO as GPIO
from env import Env
class Led_controller:
    def __init__(self,env:Env):
        super().__init__()
        if env.GPIO_MODE=='BOARD':  
            GPIO.setmode(GPIO.BOARD)
        else:
            GPIO.setmode(GPIO.BOARD)
        # redundancia
        self.RED_LED = env.RED_LED
        self.GREEN_LED = env.GREEN_LED
        GPIO.setup(self.RED_LED,GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.GREEN_LED,GPIO.OUT,initial=GPIO.LOW)

    def red(self):
        GPIO.output(self.RED_LED,GPIO.HIGH)
        GPIO.output(self.GREEN_LED,GPIO.LOW)

    def green(self):
        GPIO.output(self.GREEN_LED,GPIO.HIGH)
        GPIO.output(self.RED_LED,GPIO.LOW)

    def off(self):
        GPIO.output(self.RED_LED,GPIO.LOW)
        GPIO.output(self.GREEN_LED,GPIO.LOW)

    def clean(self): 
        GPIO.cleanup()
        

