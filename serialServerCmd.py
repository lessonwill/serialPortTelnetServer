import asyncio
import serial_asyncio
from asyncio import StreamReader, StreamWriter
import psutil
import socket
import argparse
import os
import platform

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
#    if platform.system() == 'Linux':
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
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

def run_event_loop(app):
    app.loop.run_forever()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start a Telnet server.')
    # ... (其它的命令行参数，如 --com, --baud, --port)
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode without GUI')
    parser.add_argument('--com', type=str, help='COM port (e.g., COM1)')
    parser.add_argument('--baud', type=int, help='Baud rate (e.g., 9600)')
    parser.add_argument('--port', type=int, help='Telnet port (e.g., 9001)')
    args = parser.parse_args()

    if args.cli:
        # CLI模式下的代码
        if args.com and args.baud and args.port:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(start_telnet_server(args.com, args.baud, args.port))
            loop.run_forever()
        else:
            print("In CLI mode, you must specify --com, --baud, and --port.")
    else:
        import tkinter as tk
        import threading
        import serialServerGui
        root = tk.Tk()
        app = serialServerGui.TelnetServerApp(root)
        thread = threading.Thread(target=run_event_loop, args=(app,))
        thread.start()
        root.mainloop()
