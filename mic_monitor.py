import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import ttk

ALPHA = 1.0


class MicrophoneDeviceProvider:
    @staticmethod
    def get_devices():
        return [device['name'] for device in sd.query_devices()]


class AudioAnalyzer:
    @staticmethod
    def get_normalized_volume(indata):
        return np.linalg.norm(indata) * 10


class MicrophoneMonitorUI:
    def __init__(self, master):
        self.master = master
        self.master.overrideredirect(True)
        self.label = tk.Label(self.master)
        self.label.pack(pady=0, padx=0, expand=True, fill="both")

        self.devices_combobox = ttk.Combobox(self.master, values=MicrophoneDeviceProvider.get_devices())
        self.devices_combobox.pack(pady=0, padx=0)
        self.devices_combobox.set("Select a Microphone")

        start_button = tk.Button(self.master, text="Start Monitoring", command=self.start_monitoring)
        start_button.pack(pady=5, padx=5)

    def configure_window(self, bg_color, geometry_size):
        self.master.configure(background=bg_color)
        self.master.geometry(geometry_size)

    def configure_label(self, text, font_size, bg_color, fg_color="white"):
        self.label.config(text=text, bg=bg_color, fg=fg_color, font=("Arial", font_size, "bold"))

    def audio_callback(self, indata, frames, time, status):
        volume_norm = AudioAnalyzer.get_normalized_volume(indata)
        if volume_norm == 0.0:
            self.configure_window("green", "30x15")
            self.configure_label("OFF", 10, "green")
            self.master.wm_attributes('-alpha', ALPHA)  # Make the window solid
        else:
            self.configure_window("red", "100x30")
            self.configure_label("ON AIR", 20, "red")
            self.master.wm_attributes('-alpha', ALPHA)  # Make the window 50% transparent
        self.master.update()

    def start_monitoring(self):
        device_index = self.devices_combobox.current()
        with sd.InputStream(device=device_index, callback=self.audio_callback):
            self.master.attributes('-topmost', True)
            self.master.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = MicrophoneMonitorUI(root)
    root.wait_visibility(root)
    root.mainloop()
