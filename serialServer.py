import asyncio
import serial_asyncio
from asyncio import StreamReader, StreamWriter
import psutil
import socket

# Telnet commands
IAC = b'\xff'
DONT = b'\xfe'
DO = b'\xfd'
WONT = b'\xfc'
WILL = b'\xfb'
ECHO = b'\x01'
SGA = b'\x03'
BINARY = b'\x00'

telnet_handshake =  IAC + WILL + SGA + IAC + WILL + ECHO + IAC + WILL + BINARY 
clients = []  # List to keep track of connected clients

def find_first_ip():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                return addr.address
    return None

class SerialToTelnetProtocol(asyncio.Protocol):
    def __init__(self):
        pass

    def data_received(self, data):
        for writer in clients:
            writer.write(data)
            asyncio.create_task(writer.drain())

async def read_serial(serial_transport):
    while True:
        if serial_transport._serial.in_waiting > 0:
            data = serial_transport._serial.read(serial_transport._serial.in_waiting)
            for writer in clients:
                writer.write(data)
                await writer.drain()
        await asyncio.sleep(0.1)

async def handle_telnet(reader: StreamReader, writer: StreamWriter,serial_transport):
    clients.append(writer)
    addr = writer.get_extra_info('peername')
    print(f"Telnet connection from {addr}")

    writer.write(telnet_handshake)
    await writer.drain()

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            serial_transport.write(data)

    except asyncio.CancelledError:
        pass

    finally:
        print(f"Closing connection from {addr}")
        clients.remove(writer)
        writer.close()
        await writer.wait_closed()

server = None  # Global variable to hold the server object
read_serial_task = None  # Global variable to hold the read_serial task object
serial_transport = None

async def start_telnet_server(port, baudrate, port_number):
    global server, read_serial_task, serial_transport  # Declare global variables

    # Close any existing server and tasks
    await stop_telnet_server()

    myip = find_first_ip()
    loop = asyncio.get_event_loop()
    serial_transport, _ = await serial_asyncio.create_serial_connection(
        loop, lambda: SerialToTelnetProtocol(), port, baudrate)

    read_serial_task = asyncio.create_task(read_serial(serial_transport))

    server = await asyncio.start_server(lambda r, w: handle_telnet(r, w, serial_transport), myip, port_number)


async def stop_telnet_server():
    global server, read_serial_task, serial_transport
    if server:
        server.close()
        await server.wait_closed()
        print("Telnet server stopped.")
    if read_serial_task:
        read_serial_task.cancel()
        try:
            await read_serial_task
        except asyncio.CancelledError:
            print("Read serial task cancelled.")
    if serial_transport:
        serial_transport.close()
        print("Serial port closed.")        
    for writer in list(clients):
        writer.close()
        await writer.wait_closed()
    clients.clear()

import tkinter as tk
from tkinter import ttk
import asyncio
import serial
import serial.tools.list_ports
import threading

# Initialize the global variables
com_ports = []
baud_rate = 9600
telnet_port = 9001
loop = None

# Function to populate the COM port dropdown
def populate_com_ports():
    global com_ports
    com_ports = [port.device for port in serial.tools.list_ports.comports()]
    com_port_dropdown['values'] = com_ports
    if com_ports:
        com_port_dropdown.current(0)

# Function to update the global baud rate and Telnet port
def update_baud_rate_and_port():
    global baud_rate, telnet_port
    try:
        baud_rate = int(baud_rate_entry.get())
        telnet_port = int(port_entry.get())
    except ValueError:
        print("Invalid input. Using default values for baud rate (9600) and Telnet port (9001).")

bConnected = False
# Function called when the "Connect" or "Disconnect" button is clicked
def on_connect_disconnect():
    global bConnected
    if not bConnected:
        update_baud_rate_and_port()
        selected_port = com_port_dropdown.get()
        if not selected_port:
            print("No COM port selected.")
            return
        asyncio.run_coroutine_threadsafe(start_telnet_server(selected_port, baud_rate, telnet_port), loop)
        connect_button.config(text="Disconnect")
        bConnected = True
    else:
        asyncio.run_coroutine_threadsafe(stop_telnet_server(), loop)
        connect_button.config(text="Connect")
        bConnected = False

# Create and configure the Tkinter window
root = tk.Tk()
root.title("Telnet Server")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# COM port dropdown
ttk.Label(frame, text="COM Port:").grid(row=0, column=0, sticky=tk.W)
com_port_dropdown = ttk.Combobox(frame)
com_port_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E))
populate_com_ports()

# Baud rate entry
ttk.Label(frame, text="Baud Rate:").grid(row=1, column=0, sticky=tk.W)
baud_rate_entry = ttk.Entry(frame)
baud_rate_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
baud_rate_entry.insert(0, "9600")

# Telnet port entry
ttk.Label(frame, text="Telnet Port:").grid(row=2, column=0, sticky=tk.W)
port_entry = ttk.Entry(frame)
port_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))
port_entry.insert(0, "9001")

# Connect button
connect_button = ttk.Button(frame, text="Connect", command=on_connect_disconnect)
connect_button.grid(row=3, columnspan=2)

# Create a new event loop and run it in a separate thread
def run_event_loop():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

thread = threading.Thread(target=run_event_loop)
thread.start()

root.mainloop()
