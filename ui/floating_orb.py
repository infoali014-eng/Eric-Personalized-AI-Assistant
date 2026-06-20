import tkinter as tk
from ui.animations import OrbAnimator

class FloatingOrb(tk.Toplevel):
    """
    Frameless, transparent, draggable circular widget.
    Allows user to see the state of the assistant and double click/click to wake it.
    """
    def __init__(self, parent, wake_callback):
        super().__init__(parent)
        self.wake_callback = wake_callback
        
        # Make the window frameless, topmost, and size it
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("100x100+100+100")
        
        # Configure transparency on Windows
        self.config(bg="black")
        self.attributes("-transparentcolor", "black")
        
        # Create canvas to draw the animatable orb geometries
        self.canvas = tk.Canvas(self, width=100, height=100, bg="black", highlightthickness=0)
        self.canvas.pack()
        
        self.animator = OrbAnimator(self.canvas, 100, 100)
        
        # Mouse dragging bindings
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.moved = False
        
        # Begin animation loop
        self.animate()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.moved = False

    def on_drag(self, event):
        x = self.winfo_x() + (event.x - self.drag_start_x)
        y = self.winfo_y() + (event.y - self.drag_start_y)
        self.geometry(f"+{x}+{y}")
        self.moved = True

    def on_release(self, event):
        # If it was a single click without moving, act as wake callback
        if not self.moved:
            self.wake_callback()

    def on_double_click(self, event):
        self.wake_callback()

    def set_state(self, state):
        """Sets the state: 'IDLE', 'LISTENING', or 'PROCESSING'."""
        self.animator.state = state

    def animate(self):
        self.animator.update()
        self.after(30, self.animate)
