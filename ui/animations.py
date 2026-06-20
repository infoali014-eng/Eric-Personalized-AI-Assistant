import math
import time

class OrbAnimator:
    """
    Manages canvas-based animations for the Jarvis floating orb and panel.
    Supports IDLE (pulsing orb), LISTENING (expanding audio waves), and PROCESSING (rotating arcs).
    """
    def __init__(self, canvas, width=100, height=100):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.cx = width // 2
        self.cy = height // 2
        
        self.state = "IDLE"  # IDLE, LISTENING, PROCESSING
        self.angle = 0
        self.scale = 1.0
        self.glow_dir = 1
        
    def draw_idle(self):
        """Draws a pulsing glowing cyan/blue orb."""
        self.canvas.delete("all")
        
        # Calculate radius pulsing
        t = time.time()
        pulse = math.sin(t * 4) * 5  # pulse width
        r_base = 30
        r = r_base + pulse
        
        # Outer glow ring
        self.canvas.create_oval(
            self.cx - r - 8, self.cy - r - 8,
            self.cx + r + 8, self.cy + r + 8,
            outline="#0033aa", width=2
        )
        
        # Middle glow ring
        self.canvas.create_oval(
            self.cx - r - 3, self.cy - r - 3,
            self.cx + r + 3, self.cy + r + 3,
            outline="#0066ff", width=3
        )
        
        # Inner core
        self.canvas.create_oval(
            self.cx - 20, self.cy - 20,
            self.cx + 20, self.cy + 20,
            fill="#00f0ff", outline="#ffffff", width=2
        )

    def draw_listening(self):
        """Draws concentric expanding audio wave rings."""
        self.canvas.delete("all")
        
        t = time.time()
        # Draw multiple expanding rings based on phase
        for i in range(3):
            phase = (t * 2 + i * 0.4) % 1.2
            r = 15 + phase * 35
            opacity_color = self.get_cyan_shade(1.0 - (phase / 1.2))
            
            self.canvas.create_oval(
                self.cx - r, self.cy - r,
                self.cx + r, self.cy + r,
                outline=opacity_color, width=2
            )
            
        # Draw inner active mic core
        self.canvas.create_oval(
            self.cx - 18, self.cy - 18,
            self.cx + 18, self.cy + 18,
            fill="#ff0077", outline="#ffffff", width=2
        )

    def draw_processing(self):
        """Draws rotating futuristic arcs."""
        self.canvas.delete("all")
        
        self.angle = (self.angle + 8) % 360
        
        # Draw outer rotating arc 1
        self.canvas.create_arc(
            self.cx - 38, self.cy - 38,
            self.cx + 38, self.cy + 38,
            start=self.angle, extent=90,
            style="arc", outline="#00ffff", width=3
        )
        
        # Draw outer rotating arc 2 (opposite direction/offset)
        self.canvas.create_arc(
            self.cx - 38, self.cy - 38,
            self.cx + 38, self.cy + 38,
            start=(self.angle + 180) % 360, extent=90,
            style="arc", outline="#00ffff", width=3
        )
        
        # Inner reverse rotating arc
        self.canvas.create_arc(
            self.cx - 26, self.cy - 26,
            self.cx + 26, self.cy + 26,
            start=(360 - self.angle) % 360, extent=120,
            style="arc", outline="#0066ff", width=2
        )
        
        # Center core
        self.canvas.create_oval(
            self.cx - 12, self.cy - 12,
            self.cx + 12, self.cy + 12,
            fill="#0055ff", outline="#ffffff", width=1
        )

    def get_cyan_shade(self, ratio):
        """Helper to get hex color representing faded cyan based on ratio."""
        if ratio < 0: ratio = 0
        if ratio > 1: ratio = 1
        val = int(255 * ratio)
        return f"#00{val:02x}{val:02x}"

    def update(self):
        """Triggers the next frame of animation based on the current state."""
        if self.state == "IDLE":
            self.draw_idle()
        elif self.state == "LISTENING":
            self.draw_listening()
        elif self.state == "PROCESSING":
            self.draw_processing()
