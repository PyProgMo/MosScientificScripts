import pyautogui
import mouse
import threading
import time
import tkinter as tk
from tkinter import messagebox

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Autoclicker GUI")
        self.root.geometry("350x400")

        self.scouting = False
        self.running = False
        self.n = 0  # Counter for macro
        self.click_positions = [None, None, None]

        # Labels and Inputs
        tk.Label(root, text="Repeat Interval (sec):").pack()
        self.interval_entry = tk.Entry(root)
        self.interval_entry.pack()
        self.interval_entry.insert(0, "1")  # Default to 1 second

        tk.Label(root, text="Duration (sec):").pack()
        self.duration_entry = tk.Entry(root)
        self.duration_entry.pack()
        self.duration_entry.insert(0, "10")  # Default to 10 seconds

        # Buttons
        self.scout_button = tk.Button(root, text="Start Scouting Mode", command=self.toggle_scouting)
        self.scout_button.pack(pady=5)

        self.click_button1 = tk.Button(root, text="Set Click 1", command=lambda: self.set_click_position(0))
        self.click_button1.pack(pady=5)

        self.click_button2 = tk.Button(root, text="Set Click 2", command=lambda: self.set_click_position(1))
        self.click_button2.pack(pady=5)

        self.click_button3 = tk.Button(root, text="Set Click 3", command=lambda: self.set_click_position(2))
        self.click_button3.pack(pady=5)

        self.start_button = tk.Button(root, text="Start AutoClicker", command=self.toggle_autoclicker)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop AutoClicker", command=self.stop_autoclicker)
        self.stop_button.pack(pady=5)

        self.macro_button = tk.Button(root, text="Run Custom Macro", command=self.run_macro)
        self.macro_button.pack(pady=10)

        self.status_label = tk.Label(root, text="Status: Idle", fg="blue")
        self.status_label.pack(pady=5)

    def toggle_scouting(self):
        """Start/Stop scouting mode to detect left-clicks and print mouse coordinates."""
        if not self.scouting:
            self.scouting = True
            self.scout_button.config(text="Stop Scouting Mode", fg="red")
            mouse.on_click(self.print_mouse_position)  # Detect left-clicks
        else:
            self.scouting = False
            self.scout_button.config(text="Start Scouting Mode", fg="black")
            mouse.unhook_all()  # Stop listening for clicks

    def print_mouse_position(self):
        """Prints mouse position when left-clicked."""
        if self.scouting:  # Only print if scouting is active
            x, y = pyautogui.position()
            print(f"Left-click at: ({x}, {y})")

    def set_click_position(self, index):
        """Set the click position for a button."""
        x, y = pyautogui.position()
        self.click_positions[index] = (x, y)
        print(f"Click {index + 1} set to: {x}, {y}")
        messagebox.showinfo("Position Set", f"Click {index + 1} set to: {x}, {y}")

    def toggle_autoclicker(self):
        """Start/Stop autoclicking loop."""
        if not self.running:
            self.running = True
            self.start_button.config(text="Running...", fg="red")
            self.status_label.config(text="Status: Clicking...", fg="green")

            try:
                interval = float(self.interval_entry.get())
                duration = float(self.duration_entry.get())
                threading.Thread(target=self.autoclick_loop, args=(interval, duration), daemon=True).start()
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numbers for interval and duration.")
                self.stop_autoclicker()
        else:
            self.stop_autoclicker()

    def autoclick_loop(self, interval, duration):
        """Loop that continuously clicks at the set positions based on user input."""
        start_time = time.time()
        while self.running and (time.time() - start_time) < duration:
            for pos in self.click_positions:
                if pos:
                    pyautogui.click(pos)
            time.sleep(interval)  # Wait before next click

        self.stop_autoclicker()

    def stop_autoclicker(self):
        """Stops the autoclicker."""
        self.running = False
        self.start_button.config(text="Start AutoClicker", fg="black")
        self.status_label.config(text="Status: Idle", fg="blue")

    def run_macro(self):
        """Runs the custom macro with predefined actions."""
        print(f"Running macro with n = {self.n}...")

        # Click at (100, 100)
        pyautogui.click(933, 1029) # open word window on task bar
        time.sleep(0.1)  # Wait for 0.1 seconds
        pyautogui.click(1031, 918) # select window
        time.sleep(0.1)
        pyautogui.click(1201, 791) # click on the line
        
        # Type "_" followed by n (formatted as 5-digit number)
        formatted_n = f"{self.n:05d}"  # Formats n to 5 digits (e.g., 00001)
        pyautogui.write(f"_{formatted_n}")
        time.sleep(0.1)
        
        pyautogui.click(1556, 22) # minimize word
        self.n += 1  # Increment counter for next macro run

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
