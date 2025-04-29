from machine import Pin
import time

class Light:
    def __init__(self,pin):
        self.light_pin = Pin(pin,Pin.OUT)
        self.state = False
        self.light_pin.value(self.state)
    def toggle(self):
        self.state = not self.state
        self.light_pin.value(self.state)
    def on(self):
        self.state = True
        self.light_pin.value(self.state)
    def off(self):
        self.state = False
        self.light_pin.value(self.state)
    def getstate(self):
        return self.state