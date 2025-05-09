# Smart Home Control System

This project implements a basic smart home control system using a Raspberry Pi Pico to manage lights and a garage door. The system includes a web server that allows users to control devices via a local network and incorporates a light sensor (LDR) for automated lighting.

## Files Description

* **`main.py`**:  The main application logic. It initializes the devices (lights and door), manages commands, and handles automatic light control based on the LDR sensor. It also starts the web server in a separate thread.
* **`server.py`**:  Contains the web server implementation. It handles client connections, processes requests to control devices or get the current status, and serves the HTML interface.
* **`light.py`**:  Defines the `Light` class, which encapsulates the functionality to control individual lights (turn on, turn off, toggle).
* **`door.py`**:  Defines the `Door` class, which manages the servo motor for the garage door, allowing it to be opened or closed.

## Functionality

* **Web-based Control:** A simple HTML interface allows users on the local network to:
    * Toggle individual lights on/off.
    * Open/close the garage door.
    * View the current status of the door and lights.
* **Automatic Lighting:** The system uses an LDR to automatically turn the lights on when it gets dark and off when it's bright.
* **Device Management:** The `main.py` script manages light and door devices, processing commands received from the web interface.
* **WiFi Connectivity:** The `server.py` script handles connecting the Raspberry Pi Pico to a WiFi network.

## Hardware Requirements

* Raspberry Pi Pico
* Servo motor for the garage door
* LEDs for lights
* LDR (Light Dependent Resistor)
* Resistors (as needed for LEDs)
* Wiring and breadboard

## Setup and Usage

1.  **Hardware Setup:** Connect the LEDs, servo motor, and LDR to the Raspberry Pi Pico according to the circuit diagram.
2.  **WiFi Configuration:** Modify the `server.py` file to include your WiFi SSID and password:

    ```python
    self.wifi_ssid = 'YOUR_WIFI_SSID'
    self.wifi_pass = 'YOUR_WIFI_PASSWORD'
    ```
3.  **Upload Code:** Upload all the Python files (`main.py`, `server.py`, `light.py`, `door.py`) to your Raspberry Pi Pico.
4.  **Run the Application:** Execute `main.py` on the Raspberry Pi Pico. The Pico will connect to your WiFi network, and the server will start.
5.  **Access the Web Interface:** Find the IP address of the Raspberry Pi Pico (it will be printed to the console) and open it in a web browser on a device connected to the same network.
6.  **Control Devices:** Use the buttons on the web interface to control the lights and garage door.