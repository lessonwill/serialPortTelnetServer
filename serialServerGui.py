import tkinter as tk
from tkinter import ttk
import asyncio
import serial
import serial.tools.list_ports
import threading
import serialServerCmd

class TelnetServerApp:
    def __init__(self, master):
        self.server = None
        self.read_serial_task = None
        self.serial_transport = None

        self.master = master
        self.master.title("Telnet Server")

        frame = ttk.Frame(self.master, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # COM port dropdown
        ttk.Label(frame, text="COM Port:").grid(row=0, column=0, sticky=tk.W)
        self.com_port_dropdown = ttk.Combobox(frame)
        self.com_port_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.populate_com_ports()

        # Baud rate entry
        ttk.Label(frame, text="Baud Rate:").grid(row=1, column=0, sticky=tk.W)
        self.baud_rate_entry = ttk.Entry(frame)
        self.baud_rate_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        self.baud_rate_entry.insert(0, "9600")

        # Telnet port entry
        ttk.Label(frame, text="Telnet Port:").grid(row=2, column=0, sticky=tk.W)
        self.port_entry = ttk.Entry(frame)
        self.port_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))
        self.port_entry.insert(0, "9001")

        # Connect button
        self.connect_button = ttk.Button(frame, text="Connect", command=self.on_connect_disconnect)
        self.connect_button.grid(row=3, columnspan=2)

        self.bConnected = False
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    # Function to populate the COM port dropdown
    def populate_com_ports(self):
        com_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_port_dropdown['values'] = com_ports
        if com_ports:
            self.com_port_dropdown.current(0)

    # Function to update the global baud rate and Telnet port
    def update_baud_rate_and_port(self):
        try:
            self.baud_rate = int(self.baud_rate_entry.get())
            self.telnet_port = int(self.port_entry.get())
        except ValueError:
            print("Invalid input. Using default values for baud rate (9600) and Telnet port (9001).")

    def on_connect_disconnect(self):
        if not self.bConnected:
            self.update_baud_rate_and_port()
            selected_port = self.com_port_dropdown.get()
            if not selected_port:
                print("No COM port selected.")
                return
            asyncio.run_coroutine_threadsafe(serialServerCmd.start_telnet_server(selected_port, self.baud_rate, self.telnet_port), self.loop)
            self.connect_button.config(text="Disconnect")
            self.bConnected = True
        else:
            asyncio.run_coroutine_threadsafe(serialServerCmd.stop_telnet_server(), self.loop)
            self.connect_button.config(text="Connect")
            self.bConnected = False