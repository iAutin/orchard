import tkinter as tk
from time import time
import json
import os
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import sys

class StopwatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker")
        self.root.configure(bg="#D3D3D3")  # Light gray background
        self.root.geometry("300x400")  # Larger window
        
        # Stopwatch states
        self.active_timer = None
        self.start_time = 0
        self.timers = self.load_times()  # Load saved times or initialize
        self.timer_labels = {}  # Dictionary to store labels for dynamic access
        
        # Container for timer UIs
        self.timer_container = tk.Frame(root, bg="#D3D3D3")
        self.timer_container.pack()
        
        # Create UI for each existing timer
        for timer_name in self.timers:
            self.create_timer_ui(timer_name, self.timer_container)
        
        # Add Timer button
        self.add_timer_btn = tk.Button(root, text="Add Timer", command=self.add_timer, width=10, bg="#A9A9A9", fg="white")
        self.add_timer_btn.pack(pady=10)
        
        # Key bindings for initial timers (if they exist)
        if "Work" in self.timers:
            self.root.bind("i", lambda event: self.toggle_timer("Work"))
        if "App" in self.timers:
            self.root.bind("o", lambda event: self.toggle_timer("App"))
        if "Other" in self.timers:
            self.root.bind("p", lambda event: self.toggle_timer("Other"))
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start updating display
        self.update_display()

    def create_timer_ui(self, timer_name, container):
        """Create a frame with a label and button for a timer."""
        frame = tk.Frame(container, bg="#D3D3D3")
        frame.pack(pady=5)
        
        label = tk.Label(frame, text=f"{timer_name}: 0s", font=("Arial", 14), bg="#D3D3D3")
        label.pack(side="left", padx=5)
        
        # Assign button color based on timer name
        if timer_name == "Work":
            btn_color = "#0000FF"  # Blue
        elif timer_name == "App":
            btn_color = "#00CED1"  # Blue-green
        elif timer_name == "Other":
            btn_color = "#008000"  # Green
        else:
            btn_color = "#808080"  # Gray for new timers
        
        button = tk.Button(frame, text=timer_name, command=lambda: self.toggle_timer(timer_name), width=10, bg=btn_color, fg="white")
        button.pack(side="left", padx=5)
        
        # Store the label for later access
        self.timer_labels[timer_name] = label

    def add_timer(self):
        """Prompt user to add a new timer."""
        new_name = simpledialog.askstring("Add Timer", "Enter new timer name:")
        if new_name and new_name not in self.timers:
            self.timers[new_name] = 0
            self.create_timer_ui(new_name, self.timer_container)
        elif new_name in self.timers:
            messagebox.showerror("Error", "Timer name already exists.")
        # If new_name is empty or None, do nothing

    def load_times(self):
        """Load timers from JSON file or initialize defaults."""
        if os.path.exists("timers.json"):
            with open("timers.json", "r") as f:
                return json.load(f)
        return {"Work": 0, "App": 0, "Other": 0}

    def save_times(self):
        """Save all timers to JSON file."""
        with open("timers.json", "w") as f:
            json.dump(self.timers, f)

    def on_closing(self):
        """Save elapsed time and close the app."""
        if self.active_timer:
            elapsed = time() - self.start_time
            self.timers[self.active_timer] += elapsed
        self.save_times()
        self.root.destroy()

    def toggle_timer(self, timer_name):
        """Start, stop, or switch timers."""
        if self.active_timer:
            # Stop current timer and add elapsed time
            elapsed = time() - self.start_time
            self.timers[self.active_timer] += elapsed
            if self.active_timer == timer_name:
                self.active_timer = None  # Stop if same timer clicked
            else:
                self.active_timer = timer_name  # Switch to new timer
                self.start_time = time()
        else:
            # Start new timer
            self.active_timer = timer_name
            self.start_time = time()
        
        # Update visual indication
        self.update_label_backgrounds()

    def update_label_backgrounds(self):
        """Set label backgrounds to indicate active timer."""
        for label in self.timer_labels.values():
            label.config(bg="#D3D3D3")  # Default background
        if self.active_timer:
            self.timer_labels[self.active_timer].config(bg="#FFFF00")  # Yellow for active

    def format_time(self, seconds):
        """Format time as seconds, minutes, or hours+minutes."""
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    def update_display(self):
        """Update all timer labels with current times."""
        for timer_name, label in self.timer_labels.items():
            total_time = self.timers[timer_name]
            if self.active_timer == timer_name and self.start_time:
                total_time += time() - self.start_time
            label.config(text=f"{timer_name}: {self.format_time(total_time)}")
        self.root.after(100, self.update_display)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = StopwatchApp(root)
    root.mainloop()