import network
import socket
import time
from machine import Pin, reset
import json

class SmartHomeServer:
    def __init__(self, get_status_cb, send_command_cb):
        self.get_status = get_status_cb
        self.send_command = send_command_cb
        self.wifi_ssid = 'Redmi Note 13 Pro+ 5G'
        self.wifi_pass = '123456789'
        self.led = Pin("LED", Pin.OUT)
        
    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.config(pm=0xa11140)
        
        if wlan.isconnected():
            wlan.disconnect()
            time.sleep(1)
            
        print(f"Connecting to {self.wifi_ssid}...")
        wlan.connect(self.wifi_ssid, self.wifi_pass)
        
        max_wait = 20
        while max_wait > 0:
            status = wlan.status()
            if status == network.STAT_GOT_IP:
                self.led.on()
                print(f"Connected! IP: {wlan.ifconfig()[0]}")
                return True
            elif status < 0:
                print(f"Connection failed with status: {status}")
                break
                
            self.led.toggle()
            print(f"Status: {status}, waiting...")
            max_wait -= 1
            time.sleep(1)
            
        self.led.off()
        return False
    
    def handle_request(self, conn):
        try:
            request = conn.recv(1024).decode('utf-8')
            if not request:
                conn.close()
                return
                
            request_line = request.split('\r\n')[0]
            method, path, _ = request_line.split(' ')
            
            if path == '/status':
                status = self.get_status()
                response = json.dumps(status)
                content_type = "application/json"
                
            elif path.startswith('/light/') and path.endswith('/toggle'):
                try:
                    pin = int(path.split('/')[2])
                    if 10 <= pin <= 15:
                        self.send_command(f"light {pin} toggle")
                        response = json.dumps({'status': 'success', 'pin': pin})
                        content_type = "application/json"
                    else:
                        response = "HTTP/1.1 400 Bad Request\r\n\r\nInvalid pin number"
                        conn.send(response.encode())
                        conn.close()
                        return
                except (IndexError, ValueError):
                    response = "HTTP/1.1 400 Bad Request\r\n\r\nInvalid request"
                    conn.send(response.encode())
                    conn.close()
                    return
                    
            elif path == '/door/toggle':
                self.send_command("door toggle")
                response = json.dumps({'status': 'success'})
                content_type = "application/json"
                
            elif path == '/':
                response = self.generate_html()
                content_type = "text/html"
                
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                conn.send(response.encode())
                conn.close()
                return
                
            headers = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                "Connection: close\r\n\r\n"
            )
            
            conn.send(headers.encode())
            conn.send(response.encode() if isinstance(response, str) else response)
            
        except Exception as e:
            print("Request error:", e)
            response = "HTTP/1.1 500 Internal Server Error\r\n\r\n"
            conn.send(response.encode())
        finally:
            conn.close()

    def generate_html(self):
        status = self.get_status()
        
        light_buttons = "\n".join(
            f"""<div class="light-device">
                <button onclick="toggleLight({pin})" class="{'on' if status['lights'][pin] else 'off'}">
                    GPIO {pin}: {'ON' if status['lights'][pin] else 'OFF'}
                </button>
            </div>"""
            for pin in range(10, 16)
        )
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Smart Home Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .device {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .light-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
        button {{ padding: 10px; border: none; border-radius: 4px; width: 100%; cursor: pointer; }}
        .on {{ background: #28a745; color: white; }}
        .off {{ background: #dc3545; color: white; }}
    </style>
</head>
<body>
    <h1>Smart Home Control Panel</h1>
    
    <div class="device">
        <h2>Garage Door</h2>
        <button onclick="toggleDoor()" class="{'on' if status['door'] else 'off'}">
            {'OPEN' if status['door'] else 'CLOSED'}
        </button>
    </div>
    
    <div class="device">
        <h2>Light Controls</h2>
        <div class="light-grid">
            {light_buttons}
        </div>
    </div>
    
    <script>
    function toggleDevice(url) {{
        fetch(url)
            .then(r => r.json())
            .then(updateStatus)
            .catch(e => console.error('Error:', e));
    }}
    function toggleDoor() {{ toggleDevice('/door/toggle'); }}
    function toggleLight(pin) {{ toggleDevice(`/light/${{pin}}/toggle`); }}
    
    function updateStatus() {{
        fetch('/status')
            .then(r => r.json())
            .then(data => {{
                // Update door
                const doorBtn = document.querySelector('[onclick="toggleDoor()"]');
                if(doorBtn) {{
                    doorBtn.className = data.door ? 'on' : 'off';
                    doorBtn.textContent = data.door ? 'OPEN' : 'CLOSED';
                }}
                
                // Update lights
                for(let pin = 10; pin <= 15; pin++) {{
                    const btn = document.querySelector(`[onclick="toggleLight(${{pin}})"]`);
                    if(btn) {{
                        btn.className = data.lights[pin] ? 'on' : 'off';
                        btn.textContent = `GPIO ${{pin}}: ${{data.lights[pin] ? 'ON' : 'OFF'}}`;
                    }}
                }}
            }});
    }}
    
    updateStatus();
    setInterval(updateStatus, 500);
    </script>
</body>
</html>"""

    def run_server(self):
        if not self.connect_wifi():
            print("WiFi connection failed, resetting...")
            time.sleep(5)
            reset()
            
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(1)
        print("Server running on:", addr)

        while True:
            conn = None
            try:
                conn, addr = s.accept()
                self.handle_request(conn)
            except Exception as e:
                print("Server error:", e)
                if conn:
                    conn.close()
            time.sleep(0.1)

def start_server(get_status, send_command):
    server = SmartHomeServer(get_status, send_command)
    server.run_server()