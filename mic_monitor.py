import sounddevice as sd
import numpy as np
import tkinter as tk
from tkinter import ttk

# Constants
ALPHA = 1.0
WINDOW_SIZE = "100x30"


class Microphone:
    """Provider for microphone-related functionalities."""

    @staticmethod
    def get_device_names():
        return [device['name'] for device in sd.query_devices()]

    @staticmethod
    def get_input_stream(device_index, callback):
        return sd.InputStream(device=device_index, callback=callback)

    @staticmethod
    def calculate_normalized_volume(data):
        return np.linalg.norm(data) * 10


class MicrophoneMonitorGUI:
    """GUI for microphone monitoring."""

    def __init__(self, root):
        self.root = root
        self._setup_ui()

    def _setup_ui(self):
        # Basic UI properties
        self.root.overrideredirect(True)

        # UI Elements
        self.status_label = self._create_label(self.root)
        self.device_dropdown = self._create_device_dropdown(self.root)

        # Bindings for window drag
        self._bind_window_movements()
        self._setup_context_menu()

        start_button = tk.Button(self.root, text="Start Monitoring", command=self.start_monitoring)
        start_button.pack(pady=5, padx=5)

    def _create_label(self, master):
        label = tk.Label(master)
        label.pack(pady=0, padx=0, expand=True, fill="both")
        return label

    def _create_device_dropdown(self, master):
        devices = Microphone.get_device_names()
        dropdown = ttk.Combobox(master, values=devices)
        dropdown.pack(pady=0, padx=0)
        dropdown.set("Select a Microphone")
        return dropdown

    def _bind_window_movements(self):
        """Bind functions for moving the GUI window."""
        self.root.bind('<Button-1>', self._start_drag)
        self.root.bind('<ButtonRelease-1>', self._stop_drag)
        self.root.bind('<B1-Motion>', self._perform_drag)

    def _setup_context_menu(self):
        """Create context menu with exit option."""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Exit", command=self._exit_app)
        self.root.bind('<Button-3>', self._show_context_menu)

    def _show_context_menu(self, event):
        """Display the context menu on right click."""
        self.context_menu.post(event.x_root, event.y_root)

    def _exit_app(self):
        """Exit the application."""
        self.root.quit()
        self.root.destroy()


    def _start_drag(self, event):
        self.start_x, self.start_y = event.x, event.y

    def _stop_drag(self, event):
        self.start_x = self.start_y = None

    def _perform_drag(self, event):
        dx, dy = event.x - self.start_x, event.y - self.start_y
        new_pos_x, new_pos_y = self.root.winfo_x() + dx, self.root.winfo_y() + dy
        self.root.geometry(f"+{new_pos_x}+{new_pos_y}")

    def _update_ui(self, volume_norm):
        if volume_norm == 0.0:
            self._set_window_properties("green", WINDOW_SIZE)
            self._set_label_properties("OFF", 20, "green")
        else:
            self._set_window_properties("red", WINDOW_SIZE)
            self._set_label_properties("ON AIR", 20, "red")
        self.root.wm_attributes('-alpha', ALPHA)

    def _set_window_properties(self, bg_color, geometry):
        self.root.configure(background=bg_color)
        self.root.geometry(geometry)

    def _set_label_properties(self, text, font_size, bg_color, fg_color="white"):
        self.status_label.config(text=text, bg=bg_color, fg=fg_color, font=("Arial", font_size, "bold"))

    def _audio_data_callback(self, indata, frames, time, status):
        volume_norm = Microphone.calculate_normalized_volume(indata)
        self._update_ui(volume_norm)
        self.root.update()

    def start_monitoring(self):
        device_index = self.device_dropdown.current()
        with Microphone.get_input_stream(device_index, self._audio_data_callback):
            self.root.attributes('-topmost', True)
            self.root.mainloop()


if __name__ == "__main__":
    main_window = tk.Tk()
    app = MicrophoneMonitorGUI(main_window)
    main_window.wait_visibility(main_window)
    main_window.mainloop()
