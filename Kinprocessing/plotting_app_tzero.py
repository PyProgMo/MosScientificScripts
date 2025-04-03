import tkinter as tk
from tkinter import Canvas
import numpy as np

class GetXPlotter:
    def __init__(self, master, tarray, array, var=None):
        self.master = master
        self.tarray = tarray
        self.array = array
        self.marker_position = 0

        self.canvas = Canvas(master, width=800, height=400)
        self.canvas.pack(side=tk.LEFT)
        
        self.t0_entry = tk.Entry(master)
        self.t0_entry.pack(side=tk.LEFT)

        self.plot()
        self.marker = self.canvas.create_oval(0, 0, 10, 10, fill='red', tags='marker')
        self.canvas.bind('<B1-Motion>', self.move_marker)

        if var is not None:
            self.var = var
            self.var.set(self.marker_position)
        else:
            self.var = tk.DoubleVar()
            self.var.set(self.marker_position)

    def plot(self):
        self.canvas.delete("all")
        min_t = min(self.tarray)
        max_t = max(self.tarray)
        min_a = min(self.array)
        max_a = max(self.array)

        for i in range(len(self.tarray) - 1):
            x1 = (self.tarray[i] - min_t) / (max_t - min_t) * 800
            y1 = 400 - (self.array[i] - min_a) / (max_a - min_a) * 400
            x2 = (self.tarray[i + 1] - min_t) / (max_t - min_t) * 800
            y2 = 400 - (self.array[i + 1] - min_a) / (max_a - min_a) * 400
            x1 = (self.tarray[i] - min_t) / (max_t - min_t) * 800
            y1 = 400 - (self.array[i] - min_a) / (max_a - min_a) * 400
            x2 = (self.tarray[i + 1] - min_t) / (max_t - min_t) * 800
            y2 = 400 - (self.array[i + 1] - min_a) / (max_a - min_a) * 400
            self.canvas.create_line(x1, y1, x2, y2)

    def move_marker(self, event):
        x = event.x
        self.canvas.coords(self.marker, x - 5, 195, x + 5, 205)
        self.marker_position = (x / 800) * max(self.tarray)
        t_position = (x / 800) * (max(self.tarray) - min(self.tarray)) + min(self.tarray)
        self.t0_entry.delete(0, tk.END)  # Clear the entry
        self.t0_entry.insert(0, f"{t_position:.2f}")  # Update the entry with t position
        #print(f"Marker Position: {self.marker_position}, t position: {t_position:.2f}")
        self.var.set(t_position)


    def get_marker_position(self):
        return self.marker_position

if __name__ == "__main__":
    root = tk.Tk()
    tarray = np.linspace(0, 10, 100)
    array = np.sin(tarray)
    plotter = GetXPlotter(root, tarray, array)
    root.mainloop()
