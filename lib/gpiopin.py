import RPi.GPIO as gpio
#gpio.setwarnings(False)

gpio.setwarnings(False)
gpio.setwarnings(False)

class Pin:

    def __init__(self, pin=0):
        self.pinnout = 0
        if pin < 1 or pin > 40:
            raise "Select valid Pinnout"
        else:
            self.pinnout = pin
            gpio.setmode(gpio.BCM)
            gpio.setup(pin, gpio.OUT)
            gpio.output(self.pinnout, gpio.LOW)

    def on(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.pinnout, gpio.OUT)
        gpio.output(self.pinnout, gpio.HIGH)

    def off(self):
        gpio.setmode(gpio.BCM)
        gpio.setup(self.pinnout, gpio.OUT)
        gpio.output(self.pinnout, gpio.LOW)



