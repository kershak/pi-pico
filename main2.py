import time
import network
import socket
from machine import Pin, UART

# Initialize UART
try:
    uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
    # uart = UART(0, baudrate=9600, tx=Pin(16), rx=Pin(17))
    print ("UART Initialized successfully")
except Exception as e:
    print ("UART Initialization failed: " , e)

# Cmaera control commands
commands = {
    "up": bytearray([0x01, 0x81, 0x01, 0x70, 0x01, 0x21, 0xFF, 0xFF]),
    "down": bytearray([0x01, 0x81, 0x01, 0x70, 0x01, 0x22, 0xFF, 0xFF]),
    "left": bytearray([0x01, 0x81, 0x01, 0x70, 0x01, 0x23, 0xFF, 0xFF]),
    "right": bytearray([0x01, 0x81, 0x01, 0x70, 0x01, 0x24, 0xFF, 0xFF]),
    "tele": bytearray([0x01, 0x81, 0x01, 0x04, 0x07, 0x02, 0xFF, 0xFF]),
    "wide": bytearray([0x01, 0x81, 0x01, 0x04, 0x07, 0x03, 0xFF, 0xFF]),
    "menu": bytearray([0x01, 0x81, 0x01, 0x70, 0x01, 0x26, 0xFF, 0xFF]),
    "menu-off": bytearray([0x01, 0x81, 0x01, 0x70, 0x01, 0x27, 0xFF, 0xFF]),
    "zoom_speed_1": bytearray([0x01, 0x81, 0x01, 0x70, 0x51, 0x01, 0xFF, 0xFF]),
    "zoom_speed_2": bytearray([0x01, 0x81, 0x01, 0x70, 0x51, 0x02, 0xFF, 0xFF]),
    "zoom_speed_7": bytearray([0x01, 0x81, 0x01, 0x70, 0x51, 0x07, 0xFF, 0xFF]),
    "tele_low": bytearray([0x01, 0x81, 0x01, 0x04, 0x07, 0x21, 0xFF, 0xFF]),
    "wide_low": bytearray([0x01, 0x81, 0x01, 0x04, 0x07, 0x31, 0xFF, 0xFF]),
    "cam_intialize_reset": bytearray([0x01, 0x81, 0x01, 0x04, 0x19, 0x03, 0xFF, 0xFF]),
}

# Function to send UART command with error handling
def send_uart_command(command):
    try:
        if command not in commands:
            print(f"Invalid command: {command}")
            return
        uart.write(commands[command])
        print(f"Sent command: {command}")
        time.sleep(0.1)
    except Exception as e:
        print(f"UART Error when sending {command} command: ", e)

# HTML for control panel
html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        .button { padding: 10px 20px; font-size: 20px; margin: 5px; cursor: pointer; }
        .button-green { background-color: green; color: white; }
        .button-red { background-color: red; color: white; }
    </style>
</head>
<body>
    <h1>Camera Control Panel</h1>
    <form method="get">
        <button class="button button-green" name="led" value="up" type="submit">Up</button><br>
        <button class="button button-red" name="led" value="left" type="submit">Left</button>
        <button class="button button-red" name="led" value="right" type="submit">Right</button><br>
        <button class="button button-green" name="led" value="down" type="submit">Down</button><br>
        <button class="button button-red" name="led" value="menu" type="submit">Menu</button>
        <button class="button button-green" name="led" value="menu-off" type="submit">Menu off</button>
        <button class="button button-red" name="led" value="reset" type="submit">Reset</button>
    </form>
</body>
</html> """

# Wi-fi setup
ssid = "Ascent"
password = "Gr8ascent012920"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Connecting to Wi-Fi...")
wlan.connect(ssid, password)

# Wait until Wi-Fi is connected
while wlan.status() != 3:
    print("Retrying Wi-Fi connection...")
    time.sleep(5)
    wlan.connect(ssid, password)

print("Wi-Fi connected successfully")
print("IP Address: ", wlan.ifconfig()[0])

# Open socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print("Listening on ", wlan.ifconfig()[0], ":80", addr)

# Main loop
while True:
    try:
        print("Waiting for client...")
        cl, addr = s.accept()
        print("Client connected from: ", addr)
        request = cl.recv(1024).decode()
        print("Request received: ", request)
        print("Full request: ", request)

        # Process commands
        recevied_command = None
        for cmd in commands.keys():
            if f'led={cmd}' in request:
                recevied_command = cmd
                break
        if recevied_command:
            send_uart_command(recevied_command)
            print(f"Executing command: {recevied_command}")
                # print(f"Executing command: {cmd}")
                # send_uart_command(cmd)
        
        # Send HTML response

        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + html
        cl.send(response)
        cl.close()
    except Exception as e:
        print("Connection error: ", e)
        cl.close()

    #     conn, addr = s.accept()
    #     print("Got a connection from %s" % str(addr))
    #     request = conn.recv(1024)
    #     print("Content = %s" % str(request))
    #     conn.sendall("HTTP/1.1 200 OK\n")
    #     conn.sendall("Content-Type: text/html\n")
    #     conn.sendall("\n")
    #     conn.sendall("<h1>Hello from PI PICO</h1>")
    #     conn.close()
    # except Exception as e:
    #     print("Error in main loop: ", e)

    