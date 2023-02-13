import csv
import subprocess
import time
import datetime
from geopy.geocoders import Nominatim
import tkinter as tk
from tkinter import ttk


class WifiLogger:
    def __init__(self):
        self.is_running = False
        self.geolocator = Nominatim(user_agent='my-app')

        self.root = tk.Tk()
        self.root.title("WiFi Logger")

        self.start_button = ttk.Button(self.root, text="Start", command=self.start_logging)
        self.start_button.grid(column=0, row=0, padx=10, pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop", command=self.stop_logging, state=tk.DISABLED)
        self.stop_button.grid(column=1, row=0, padx=10, pady=10)

    def start_logging(self):
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        while self.is_running:
            interfaces = self.get_interfaces()
            latitude, longitude = self.get_location()
            self.write_interfaces_to_csv(interfaces, latitude, longitude)
            time.sleep(30)

    def stop_logging(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def get_interfaces(self):
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], universal_newlines=True)

        interfaces = []
        current_interface = {}

        for line in output.splitlines():
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                if key == 'Name':
                    if current_interface:
                        interfaces.append(current_interface)
                        current_interface = {}
                if key in ['Name', 'SSID', 'Radio type', 'Band', 'Receive rate (Mbps)', 'Transmit rate (Mbps)', 'Signal']:
                    current_interface[key] = value

        interfaces.append(current_interface)

        return interfaces

    def get_location(self):
        location = self.geolocator.geocode(query=None, exactly_one=True, timeout=10)
        return location.latitude, location.longitude

    def write_interfaces_to_csv(self, interfaces, latitude, longitude):
        with open('interfaces.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(
                    ['Timestamp', 'Name', 'SSID', 'Radio type', 'Band', 'Receive rate (Mbps)', 'Transmit rate (Mbps)',
                     'Signal', 'Latitude', 'Longitude'])
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for interface in interfaces:
                writer.writerow([
                    timestamp,
                    interface.get('Name', ''),
                    interface.get('SSID', ''),
                    interface.get('Radio type', ''),
                    interface.get('Band', ''),
                    interface.get('Receive rate (Mbps)', ''),
                    interface.get('Transmit rate (Mbps)', ''),
                    interface.get('Signal', ''),
                    str(latitude),
                    str(longitude),
                ])

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    logger = WifiLogger()
    logger.run()
