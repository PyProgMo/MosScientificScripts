import tkinter as tk
from tkinter import Canvas
import numpy as np

class GetXPlotter:
    def __init__(self, master, tarray, array, var=None):
        self.master = master
        self.tarray = tarray
        self.array = array
        self.marker_position = 0
        self.inpvar = var

        self.canvas = Canvas(master, width=800, height=200)
        self.canvas.grid(row=0, column=0, columnspan=2)
        self.t0_entry = tk.Entry(master)
        self.t0_entry.grid(row=1, column=0, sticky="nsew")

        #self.t0_entry.insert(0, f"{self.marker_position:.2f}")  # Initialize with the marker position

    def initplot(self, plotsizx=800, plotsizy=200):

        self.marker = self.canvas.create_oval(0, 0, 10, 10, fill='red', tags='marker')
        self.canvas.bind('<B1-Motion>', self.move_marker)

        self.plotsizex = plotsizx
        self.plotsizy = plotsizy

        if self.inpvar is not None:
            self.var = self.inpvar
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

        print(f"min_t: {min_t}, max_t: {max_t}, min_a: {min_a}, max_a: {max_a}")

        for i in range(len(self.tarray) - 1):
            x = (self.tarray[i] - min_t) / (max_t - min_t) * self.plotsizex
            y = self.plotsizy / 2 if max_a == min_a else self.plotsizy - (self.array[i] - min_a) / (max_a - min_a) * self.plotsizy
            self.canvas.create_oval(x-1, y-1, x+1, y+1, fill='black')
            #self.canvas.create_line(x1, y1, x2, y2)

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
