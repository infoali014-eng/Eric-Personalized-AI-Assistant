import os
import sys
import threading
import queue
import time
import tkinter as tk
from ui.main_window import JarvisMainWindow
from ui.floating_orb import FloatingOrb
from voice.text_to_speech import speak

class BackgroundAgent:
    """
    Main background daemon process managing the assistant life cycle,
    UI event bindings, hotword triggers, and async execution threads.
    """
    def __init__(self):
        # Create standard Tk root but hide it (we only deiconify sub-windows)
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Initialize UI components
        self.window = JarvisMainWindow(self.on_manual_command)
        self.orb = FloatingOrb(self.root, self.on_wake_trigger)
        
        # Position UI components nicely on screen
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        # Floating orb at bottom-right corner
        self.orb.geometry(f"+{screen_w - 120}+{screen_h - 180}")
        # Main dashboard panel next to it
        self.window.geometry(f"+{screen_w - 580}+{screen_h - 750}")
        
        # Start hotword background streaming listener
        self.hotword_engine = None
        self.start_hotword_thread()

    def start_hotword_thread(self):
        """Attempts to start the continuous hotword listener stream."""
        try:
            from core.hotword_engine import HotwordEngine
            self.hotword_engine = HotwordEngine(self.on_wake_trigger)
            success = self.hotword_engine.start()
            if success:
                self.window.write_log("Streaming hotword engine is online. Say 'Hey Eric' to wake me.")
            else:
                self.window.write_log("Warning: Microphone not initialized. Using click-to-wake.")
        except ImportError as e:
            self.window.write_log("Warning: PyAudio not detected. Wake-word detection offline.")
            self.window.write_log("You can still use click-to-wake or text command box.")
        except Exception as e:
            self.window.write_log(f"Error starting wake-word engine: {e}")

    def on_wake_trigger(self):
        """Triggered when hotword 'Hey Eric' matches or orb is clicked."""
        # Active wake flow in main thread context
        self.root.after(0, self._wake_flow)

    def _wake_flow(self):
        self.window.show_panel()
        self.window.set_status("LISTENING", "#ef4444")
        self.orb.set_state("LISTENING")
        speak("Yes?")
        
        # Start listening for command in a background thread to prevent UI lag
        threading.Thread(target=self.voice_capture_thread, daemon=True).start()

    def voice_capture_thread(self):
        """Background thread to capture the spoken voice instruction."""
        try:
            from voice.speech_to_text import listen_for_speech
            user_speech = listen_for_speech(timeout=5, phrase_time_limit=8)
            if user_speech:
                self.root.after(0, self.on_command_received, user_speech)
            else:
                self.root.after(0, self.on_no_input)
        except Exception as e:
            self.root.after(0, self.on_error, f"Voice capture error: {e}")

    def on_command_received(self, text):
        """Invoked when voice command is successfully transcribed."""
        self.window.write_log(f"Voice Command: '{text}'")
        # Run execution pipeline asynchronously
        threading.Thread(target=self.run_command_async, args=(text,), daemon=True).start()

    def on_manual_command(self, text):
        """Invoked when manual text command is run from the dashboard box."""
        self.window.write_log(f"Text Command: '{text}'")
        self.run_command_async(text)

    def on_no_input(self):
        speak("I didn't hear anything.")
        self.reset_to_idle()

    def on_error(self, err_msg):
        self.window.write_log(f"Error: {err_msg}")
        self.reset_to_idle()

    def reset_to_idle(self):
        self.orb.set_state("IDLE")
        self.window.set_status("IDLE", "#3b82f6")

    def run_command_async(self, text):
        """
        Runs the command execution pipeline (Gemini, Memory, Vision, Router)
        in a background worker thread. Updates UI and animations in real-time.
        """
        self.root.after(0, lambda: self.orb.set_state("PROCESSING"))
        self.root.after(0, lambda: self.window.set_status("PROCESSING", "#f59e0b"))
        self.root.after(0, lambda: self.window.set_task(text))
        
        text_clean = text.lower().strip()
        
        # 1. Route through Global Interceptor (Interceptors/Workflows/Memory/Vision)
        from core.command_interceptor import intercept_input
        intercepted, result = intercept_input(text)
        
        if intercepted:
            self.root.after(0, lambda: self.window.write_log(f"Interceptor output: {result}"))
            speak(result)
            self.root.after(0, self.reset_to_idle)
            return

        # Use normalized input for planning
        normalized_input = result

        # 2. Planning & Executor loop
        try:
            # Overwrite task_planner printing to write directly to window log
            # We can capture logs by importing modules
            from core.task_planner import generate_plan, execute_plan
            
            self.root.after(0, lambda: self.window.write_log("Generating execution plan..."))
            plan = generate_plan(normalized_input)
            steps_count = len(plan.get("steps", []))
            self.root.after(0, lambda: self.window.write_log(f"Plan generated with {steps_count} steps."))
            
            # Execute steps
            success = execute_plan(plan)
            if success:
                self.root.after(0, lambda: self.window.write_log("Task plan executed successfully."))
            else:
                self.root.after(0, lambda: self.window.write_log("Task execution failed/halted."))
                
        except Exception as e:
            err = f"Execution failed: {e}"
            self.root.after(0, lambda: self.window.write_log(err))
            speak(f"Could not execute task: {e}")
            
        self.root.after(0, self.reset_to_idle)

    def run(self):
        """Starts the Tkinter main loop."""
        try:
            self.root.mainloop()
        finally:
            if self.hotword_engine:
                self.hotword_engine.stop()

if __name__ == "__main__":
    agent = BackgroundAgent()
    agent.run()
