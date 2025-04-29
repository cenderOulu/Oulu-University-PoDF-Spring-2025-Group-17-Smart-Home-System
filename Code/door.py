from machine import Pin, PWM, ADC
import time


# servo_pin = Pin(1, Pin.OUT)
# ldr_pin = Pin(26)
# adc = ADC(ldr_pin)
class Door:
    def __init__(self,pin):
        self.servo_pin = Pin(pin, Pin.OUT)
        self.pwm_servo = PWM(self.servo_pin, freq=50)
        self.set_servo_angle(70)
        self.state = False
    def set_servo_angle(self,angle):
        if 0 <= angle <= 180:

            pulse_width_us = (angle * (2500 - 500) / 180) + 500


            duty_cycle = int(pulse_width_us * 65535 / 20000)
            self.pwm_servo.duty_u16(duty_cycle)
            time.sleep(1)
        else:
            return

    def door_toggle(self):
        if self.state:
            self.set_servo_angle(70)
            self.state = False
        else:
            self.set_servo_angle(0)
            self.state = True
    def getstate(self):
        return self.state
            
# Make the servo repeatedly go from 90 to 1 degrees
# if __name__ == "__main__":
#     print("Making servo repeatedly go from 90 to 1 degrees...")
# 
#     try:
#         while True:
#             # Move to 90 degrees
#             ldr_value = adc.read_u16()
#             if ldr_value>1000:
#                 print("Moving to 90 degrees...")
#                 set_servo_angle(180)
#                 time.sleep(0.5)  # Adjust the delay as needed
# 
#                 # Move to 1 degree
#                 print("Moving to 1 degree...")
#                 set_servo_angle(0)
#             time.sleep(0.5)  # Adjust the delay as needed
# 
#     except KeyboardInterrupt:
#         print("\nLoop stopped by user.")
#     finally:
#         pwm_servo.deinit()
#         print("PWM deinitialized.")
