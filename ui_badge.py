import tkinter as tk


class RecordingBadge:
    def __init__(self, root, size=48, margin=16, on_stop=None, on_exit=None):
        self.size = size
        self.margin = margin
        self.window = tk.Toplevel(root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        self.canvas = tk.Canvas(
            self.window,
            width=size,
            height=size,
            bg="white",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()

        menu = tk.Menu(self.window, tearoff=0)
        menu.add_command(label="Stop Monitoring", command=on_stop)
        menu.add_command(label="Exit", command=on_exit)
        self.canvas.bind("<Button-3>", lambda e: menu.post(e.x_root, e.y_root))

        self.window.withdraw()

    def show(self):
        x = max(0, self.window.winfo_screenwidth() - self.size - self.margin)
        y = max(0, self.window.winfo_screenheight() - self.size - self.margin)
        self.canvas.delete("all")
        self.canvas.create_oval(8, 8, self.size - 8, self.size - 8, fill="#d61f1f", outline="")
        self.canvas.create_oval(14, 14, self.size - 14, self.size - 14, outline="white", width=2)
        self.window.geometry(f"{self.size}x{self.size}+{x}+{y}")
        self.window.deiconify()
        self.window.lift()

    def hide(self):
        self.window.withdraw()
