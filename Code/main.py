import time
from machine import ADC
import _thread
import door
import light

# Initialize devices
ldr_pin = ADC(26)
door_device = door.Door(1)  # GPIO 1 for door
light_devices = {pin: light.Light(pin) for pin in range(10, 16)}  # GPIO 10-15
command_queue = []
running = True
def dark():
    ldr_value = ldr_pin.read_u16()
    return ldr_value < 10000
    
def get_status():
    return {
        'door': door_device.getstate(),
        'lights': {pin: light_devices[pin].getstate() for pin in light_devices}
    }

def send_command(command):
    command_queue.append(command)

def process_commands():
    global running
    darked = True
    while running:
        if dark() and not darked:
            for pin in light_devices:
                light_devices[pin].on()
            darked = True
        elif not dark() and darked:
            for pin in light_devices:
                light_devices[pin].off()
            darked = False    
        if command_queue:
            cmd = command_queue.pop(0)
            print("Processing command:", cmd)  # Debug log
            if cmd.startswith("light"):
                try:
                    _, pin, action = cmd.split()
                    pin = int(pin)
                    if pin in light_devices and action == "toggle":
                        light_devices[pin].toggle()
                        print(f"Toggled light {pin}")  # Debug log
                except Exception as e:
                    print("Error processing light command:", e)
            elif cmd == "door toggle":
                door_device.door_toggle()
        time.sleep(0.1)

# Start command processing thread
_thread.start_new_thread(process_commands, ())

# Import server after initializing everything
from server import start_server
start_server(get_status, send_command)