import sys
import threading
import time

try:
    import tkinter as tk
except Exception:
    tk = None

from audio_devices import BLOCK, discover_devices, level_value, open_recorder, resolve_microphone, startup_errors
from ui_badge import RecordingBadge

POLL_MS = 50
THRESHOLD = 1e-6
HOLD_SECONDS = 10.0

ROW_IDLE = "#f4f4f4"
ROW_SELECTED = "#eef5ff"
ROW_ACTIVE = "#ffdede"
ROW_ERROR = "#ffe8c7"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Recording Light")
        self.root.resizable(False, False)

        self.rows = {}
        self.levels = {}
        self.errors = set()
        self.threads = []
        self.stop_event = threading.Event()
        self.session = 0
        self.hold_until = 0.0
        self.running = False
        self.toggle_var = tk.BooleanVar(value=False)
        self.badge = RecordingBadge(root, on_stop=self.stop, on_exit=self.close)

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def build_ui(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        errors = startup_errors()
        devices = discover_devices() if not errors else []
        if errors or not devices:
            message = "\n\n".join(errors) if errors else (
                "No microphones found.\n"
                "Check mic permissions and make sure an input device is connected."
            )
            tk.Label(
                frame,
                text=message,
                fg="red",
                justify="left",
                anchor="w",
                wraplength=520,
            ).pack(fill="x")
            return

        tk.Label(frame, text="Microphones", anchor="w").pack(fill="x", pady=(0, 6))
        list_frame = tk.Frame(frame)
        list_frame.pack(fill="both", expand=True)

        for device in devices:
            row = tk.Frame(list_frame, bg=ROW_IDLE, padx=6, pady=4)
            row.pack(fill="x", pady=2)

            selected = tk.BooleanVar()
            check = tk.Checkbutton(
                row,
                text=device.name,
                variable=selected,
                command=self.on_selection_change,
                anchor="w",
                bg=ROW_IDLE,
                activebackground=ROW_IDLE,
                highlightthickness=0,
            )
            check.pack(side="left", fill="x", expand=True)

            status = tk.Label(row, text="idle", width=9, anchor="e", bg=ROW_IDLE)
            status.pack(side="right", padx=(8, 0))
            level = tk.Label(row, text="-", width=7, anchor="e", bg=ROW_IDLE)
            level.pack(side="right")

            self.rows[device.key] = {
                "device": device,
                "selected": selected,
                "row": row,
                "check": check,
                "status": status,
                "level": level,
            }

        self.toggle = tk.Checkbutton(
            frame,
            text="Start Monitoring",
            variable=self.toggle_var,
            indicatoron=False,
            command=self.on_toggle,
            padx=12,
            pady=8,
        )
        self.toggle.pack(fill="x", pady=(10, 0))
        self.paint()

    def selected_devices(self):
        return [
            row["device"]
            for row in self.rows.values()
            if row["selected"].get()
        ]

    def on_selection_change(self):
        if self.running:
            if self.selected_devices():
                self.start()
            else:
                self.stop()
        self.paint()

    def on_toggle(self):
        if self.toggle_var.get():
            self.start()
        else:
            self.stop()

    def worker(self, device, session):
        try:
            mic = resolve_microphone(device)
            if mic is None:
                raise RuntimeError
            with open_recorder(mic) as recorder:
                while session == self.session and not self.stop_event.is_set():
                    data = recorder.record(numframes=BLOCK)
                    self.levels[device.key] = level_value(data)
        except Exception:
            self.errors.add(device.key)
            self.levels[device.key] = 0.0

    def start(self):
        devices = self.selected_devices()
        if not devices:
            self.running = False
            self.toggle_var.set(False)
            self.badge.hide()
            self.paint()
            return

        self.session += 1
        self.stop_event.set()
        self.threads.clear()

        self.running = True
        self.errors.clear()
        self.levels = {device.key: 0.0 for device in devices}
        self.hold_until = 0.0
        self.stop_event = threading.Event()

        for device in devices:
            thread = threading.Thread(
                target=self.worker,
                args=(device, self.session),
                daemon=True,
            )
            thread.start()
            self.threads.append(thread)

        self.toggle_var.set(True)
        self.paint()
        self.poll(self.session)

    def stop(self):
        self.running = False
        self.toggle_var.set(False)
        self.session += 1
        self.stop_event.set()
        self.threads.clear()
        self.levels.clear()
        self.errors.clear()
        self.hold_until = 0.0
        self.badge.hide()
        self.paint()

    def poll(self, session):
        if session != self.session:
            return

        now = time.monotonic()
        if any(
                row["selected"].get() and self.levels.get(key, 0.0) >= THRESHOLD
                for key, row in self.rows.items()
        ):
            self.hold_until = now + HOLD_SECONDS

        if self.running and now < self.hold_until:
            self.badge.show()
        else:
            self.badge.hide()

        self.paint()
        self.root.after(POLL_MS, lambda: self.poll(session))

    def paint(self):
        if hasattr(self, "toggle"):
            active = self.running
            self.toggle.config(
                text="Stop Monitoring" if active else "Start Monitoring",
                bg="#ffdede" if active else "#e7f1e7",
                activebackground="#ffdede" if active else "#e7f1e7",
            )

        for key, row in self.rows.items():
            selected = row["selected"].get()
            level = self.levels.get(key, 0.0) if self.running and selected else 0.0
            errored = self.running and key in self.errors
            active = self.running and selected and level >= THRESHOLD and not errored

            if errored:
                bg, state = ROW_ERROR, "error"
            elif active:
                bg, state = ROW_ACTIVE, "active"
            elif selected:
                bg, state = ROW_SELECTED, "armed" if self.running else "selected"
            else:
                bg, state = ROW_IDLE, "idle"

            row["row"].config(bg=bg)
            row["check"].config(bg=bg, activebackground=bg, selectcolor=bg)
            row["status"].config(bg=bg, text=state)
            row["level"].config(bg=bg, text=f"{level:.3f}" if self.running and selected else "-")

    def close(self):
        self.stop()
        self.root.destroy()


def main():
    if tk is None:
        print("No `tkinter` module. On Ubuntu/Debian install `python3-tk`.", file=sys.stderr)
        raise SystemExit(1)
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
