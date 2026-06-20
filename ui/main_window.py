import tkinter as tk
from tkinter import ttk
import threading

class JarvisMainWindow(tk.Tk):
    """
    Sleek, futuristic dark-themed main dashboard panel for Eric AI.
    Features drag capability, task list, console status logs, and manual text input entry.
    """
    def __init__(self, submit_command_callback):
        super().__init__()
        self.submit_command_callback = submit_command_callback
        
        # Configure window geometry and frameless styling
        self.title("Eric AI - Jarvis Control Panel")
        self.geometry("450x550+250+150")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg="#0a0f1d")
        
        # Header dragging variables
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.setup_ui()

    def setup_ui(self):
        # 1. Header Frame (Custom Draggable Titlebar)
        header = tk.Frame(self, bg="#111827", height=40)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        header.bind("<Button-1>", self.start_drag)
        header.bind("<B1-Motion>", self.on_drag)
        
        # Title text in header
        title_label = tk.Label(
            header, text="ERIC AI // JARVIS CONTROL PANEL", 
            fg="#00ffff", bg="#111827", font=("Courier New", 12, "bold")
        )
        title_label.pack(side="left", padx=15)
        title_label.bind("<Button-1>", self.start_drag)
        title_label.bind("<B1-Motion>", self.on_drag)
        
        # Close Button
        close_btn = tk.Button(
            header, text="✕", fg="#ffffff", bg="#ef4444", 
            activebackground="#b91c1c", activeforeground="#ffffff",
            bd=0, font=("Segoe UI", 10, "bold"), width=3, height=1,
            command=self.hide_panel
        )
        close_btn.pack(side="right", padx=10)

        # 2. Main Content Container
        content = tk.Frame(self, bg="#0a0f1d", padx=20, pady=15)
        content.pack(fill="both", expand=True)

        # Listening Status Indicators
        self.status_title = tk.Label(
            content, text="SYSTEM STATUS:", fg="#9ca3af", bg="#0a0f1d",
            font=("Courier New", 10, "bold")
        )
        self.status_title.pack(anchor="w")

        self.status_label = tk.Label(
            content, text="IDLE", fg="#3b82f6", bg="#0a0f1d",
            font=("Courier New", 14, "bold")
        )
        self.status_label.pack(anchor="w", pady=(2, 10))

        # Current Task Display Panel
        tk.Label(
            content, text="ACTIVE EXECUTION PLAN / TASK:", fg="#9ca3af", bg="#0a0f1d",
            font=("Courier New", 10, "bold")
        ).pack(anchor="w")
        
        self.task_text = tk.Text(
            content, height=3, bg="#111827", fg="#ffffff", bd=1,
            relief="solid", insertbackground="white", font=("Segoe UI", 10),
            padx=5, pady=5
        )
        self.task_text.pack(fill="x", pady=(2, 12))
        self.task_text.insert("1.0", "No active tasks planning...")
        self.task_text.config(state="disabled")

        # Execution Logs and Feedbacks
        tk.Label(
            content, text="SYSTEM CONSOLE LOGS:", fg="#9ca3af", bg="#0a0f1d",
            font=("Courier New", 10, "bold")
        ).pack(anchor="w")

        log_frame = tk.Frame(content, bg="#111827", bd=1, relief="solid")
        log_frame.pack(fill="both", expand=True, pady=(2, 12))

        self.log_area = tk.Text(
            log_frame, bg="#0f172a", fg="#10b981", bd=0,
            font=("Courier New", 9), padx=8, pady=8
        )
        self.log_area.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_area.yview)
        scrollbar.pack(fill="y", side="right")
        self.log_area.config(yscrollcommand=scrollbar.set)
        
        self.write_log("System initialization completed.")

        # 3. Manual Command Input Box
        input_frame = tk.Frame(content, bg="#0a0f1d")
        input_frame.pack(fill="x", side="bottom")

        tk.Label(
            input_frame, text="MANUAL INSTRUCTION INPUT:", fg="#00ffff", bg="#0a0f1d",
            font=("Courier New", 9, "bold")
        ).pack(anchor="w")

        self.input_entry = tk.Entry(
            input_frame, bg="#111827", fg="#ffffff", bd=1,
            relief="solid", insertbackground="white", font=("Segoe UI", 11)
        )
        self.input_entry.pack(fill="x", side="left", expand=True, ipady=4, pady=5)
        self.input_entry.bind("<Return>", self.submit_input)

        send_btn = tk.Button(
            input_frame, text="RUN", bg="#0088ff", fg="#ffffff",
            activebackground="#0055cc", activeforeground="#ffffff",
            bd=0, font=("Courier New", 10, "bold"), width=8,
            command=self.submit_input
        )
        send_btn.pack(side="right", padx=(8, 0), ipady=3, pady=5)

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        x = self.winfo_x() + (event.x - self.drag_start_x)
        y = self.winfo_y() + (event.y - self.drag_start_y)
        self.geometry(f"+{x}+{y}")

    def show_panel(self):
        self.deiconify()
        self.attributes("-topmost", True)

    def hide_panel(self):
        self.withdraw()

    def submit_input(self, event=None):
        text = self.input_entry.get().strip()
        if text:
            self.input_entry.delete(0, tk.END)
            # Submit instruction in a background thread to keep UI alive
            threading.Thread(target=self.submit_command_callback, args=(text,), daemon=True).start()

    def set_status(self, text, color="#3b82f6"):
        """Updates the system status banner text and colors."""
        self.status_label.config(text=text.upper(), fg=color)

    def set_task(self, task_name):
        """Updates the active task plan pane."""
        self.task_text.config(state="normal")
        self.task_text.delete("1.0", tk.END)
        self.task_text.insert("1.0", task_name)
        self.task_text.config(state="disabled")

    def write_log(self, text):
        """Appends a new line of text to the system console logs."""
        self.log_area.insert(tk.END, f">> {text}\n")
        self.log_area.see(tk.END)
