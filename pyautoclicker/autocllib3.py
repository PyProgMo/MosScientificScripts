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
        tk.Label(root, text="N Repetitions:").pack()
        self.repetitions_entry = tk.Entry(root)
        self.repetitions_entry.pack()
        self.repetitions_entry.insert(0, "5")  # Default to 5 repetitions

        tk.Label(root, text="Duration per Run (sec):").pack()
        self.duration_entry = tk.Entry(root)
        self.duration_entry.pack()
        self.duration_entry.insert(0, "1")  # Default to 1 second per run

        # Buttons
        self.scout_button = tk.Button(root, text="Start Scouting Mode", command=self.toggle_scouting)
        self.scout_button.pack(pady=1)

        self.click_button1 = tk.Button(root, text="Set Click 1", command=lambda: self.set_click_position(0))
        self.click_button1.pack(pady=1)

        self.click_button2 = tk.Button(root, text="Set Click 2", command=lambda: self.set_click_position(1))
        self.click_button2.pack(pady=1)

        self.click_button3 = tk.Button(root, text="Set Click 3", command=lambda: self.set_click_position(2))
        self.click_button3.pack(pady=1)

        # add space 
        self.space_label = tk.Label(root, text=" ")
        self.space_label.pack(pady=1)

        self.macro_button = tk.Button(root, text="Run Custom Macro", command=self.run_macro)
        self.macro_button.pack(pady=1)

        self.clara_macro_button = tk.Button(root, text="Run Clara Kinetic Macro", command=lambda: self.macro_clara_kinetic(5, 1))
        self.clara_macro_button.pack(pady=1)

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

    def run_macro(self):
        """Runs the custom macro N times, each with a set duration."""
        try:
            repetitions = int(self.repetitions_entry.get())
            duration = float(self.duration_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for repetitions and duration.")
            return

        threading.Thread(target=self.macro_loop, args=(repetitions, duration), daemon=True).start()

    def macro_loop(self, repetitions, duration):
        self.n = 0  # Reset counter for macro
        self.status_label.config(text="Status: Running Macro...", fg="green")
        """Executes the macro N times with the specified duration per run."""
        self.dt = 0.01  # Time interval for each action
        for i in range(repetitions):
            print(f"Running macro {i + 1}/{repetitions} with n = {self.n}...")
            # Click at (100, 100)
            pyautogui.click(973, 1029) # open word window on task bar
            time.sleep(self.dt)  # Wait for dt
            pyautogui.click(1031, 918) # select window
            time.sleep(self.dt)
            pyautogui.click(1201, 791) # click on the line
            
            # Type "_" followed by n (formatted as 5-digit number)
            formatted_n = f"{self.n:05d}"  # Formats n to 5 digits (e.g., 00001)
            pyautogui.write(f"clara_kinetic_{formatted_n}")
            time.sleep(self.dt)
            
            pyautogui.click(1556, 22) # minimize word
            self.n += 1  # Increment counter for next macro run

            # Wait for the specified duration before the next macro run
            time.sleep(duration)

        print("Macro execution completed.")
        self.status_label.config(text="Status: Idle", fg="blue")

    def macro_clara_kinetic(self, repetitions, duration):
        self.n = 0
        self.status_label.config(text="Status: Running Macro...", fg="green")
        """Executes the macro N times with the specified duration per run."""
        self.dt = 0.01  # Time interval for each action
        for i in range(repetitions):
            print(f"Running macro {i + 1}/{repetitions} with n = {self.n}...")
            pyautogui.click(983, 1029) # open word window on task bar
            time.sleep(self.dt)  # Wait for dt
            pyautogui.click(1071, 918) # select window
            time.sleep(self.dt)
            pyautogui.click(1201, 791) # click on the line
            
            # Type "_" followed by n (formatted as 5-digit number)
            formatted_n = f"{self.n:05d}"  # Formats n to 5 digits (e.g., 00001)
            pyautogui.write(f"_{formatted_n}")
            time.sleep(self.dt)
            
            pyautogui.click(1556, 22) # minimize word
            self.n += 1  # Increment counter for next macro run

            # Wait for the specified duration before the next macro run
            time.sleep(duration)

        print("Macro execution completed.")
        self.status_label.config(text="Status: Idle", fg="blue")


if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.mainloop()
