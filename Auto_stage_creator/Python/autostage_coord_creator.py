
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog
class AutoStageCoordcreator:
    def __init__(self, xmin=0, xmax=300, ymin=0, ymax=300, zmin=0, zmax=300):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        self.makecoordinates = []
        self.roundx = 2
        self.roundy = 2
        self.roundz = 2

    def set_rounding(self, x_round=2, y_round=2, z_round=2):
        self.roundx = x_round
        self.roundy = y_round
        self.roundz = z_round
    
    def create_coordinates(self, arr):
        # arr consits of (x-start, y-start, z-start, x-end, y-end, z-end, N-x-steps, N-y-steps, N-z-steps)
        x_start, y_start, z_start, x_end, y_end, z_end, nx, ny, nz = arr

        if x_start > self.xmin:
            x_start = self.xmin
        if x_end < self.xmax:
            x_end = self.xmax
        if y_start > self.ymin:
            y_start = self.ymin
        if y_end < self.ymax:
            y_end = self.ymax
        if z_start > self.zmin:
            z_start = self.zmin
        elif z_end < self.zmax:
            z_end = self.zmax

        x_coords = np.linspace(x_start, x_end, nx)
        if len(x_coords) == 0:
            x_coords = [x_start]
        y_coords = np.linspace(y_start, y_end, ny)
        if len(y_coords) == 0:
            y_coords = [y_start]
        z_coords = np.linspace(z_start, z_end, nz)
        if len(z_coords) == 0:
            z_coords = [z_start]
        print(f"length of x_coords: {len(x_coords)}, y_coords: {len(y_coords)}, z_coords: {len(z_coords)}")
        print(f"will create {len(x_coords)} * {len(y_coords)} * {len(z_coords)} = {len(x_coords) * len(y_coords) * len(z_coords)} coordinates")

        for x in x_coords:
            for y in y_coords:
                for z in z_coords:
                    self.makecoordinates.append((f"{round(x, int(self.roundx)):.{self.roundx}f}", 
                                                 f"{round(y, int(self.roundy)):.{self.roundy}f}", 
                                                 f"{round(z, int(self.roundz)):.{self.roundz}f}"))
    
    def write_coordinates(self, filename):
        with open(filename, 'w') as f:
            f.write(f"{self.makecoordinates[0][0]},{self.makecoordinates[0][1]},{self.makecoordinates[0][2]}")
            for i in range(len(self.makecoordinates)-1):
                f.write(f"\n{self.makecoordinates[i+1][0]},{self.makecoordinates[i+1][1]},{self.makecoordinates[i+1][2]}")


class AutoStageGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AutoStage Coordinate Creator")
        self.asc = AutoStageCoordcreator()
        
        # Input fields
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="X Start:").grid(row=0, column=0)
        self.x_start = ttk.Entry(frame)
        self.x_start.grid(row=0, column=1)
        
        ttk.Label(frame, text="Y Start:").grid(row=1, column=0)
        self.y_start = ttk.Entry(frame)
        self.y_start.grid(row=1, column=1)
        
        ttk.Label(frame, text="Z Start:").grid(row=2, column=0)
        self.z_start = ttk.Entry(frame)
        self.z_start.grid(row=2, column=1)
        
        ttk.Label(frame, text="X End:").grid(row=0, column=2)
        self.x_end = ttk.Entry(frame)
        self.x_end.grid(row=0, column=3)
        
        ttk.Label(frame, text="Y End:").grid(row=1, column=2)
        self.y_end = ttk.Entry(frame)
        self.y_end.grid(row=1, column=3)
        
        ttk.Label(frame, text="Z End:").grid(row=2, column=2)
        self.z_end = ttk.Entry(frame)
        self.z_end.grid(row=2, column=3)
        
        ttk.Label(frame, text="X Steps:").grid(row=3, column=0)
        self.nx = ttk.Entry(frame)
        self.nx.grid(row=3, column=1)
        
        ttk.Label(frame, text="Y Steps:").grid(row=3, column=2)
        self.ny = ttk.Entry(frame)
        self.ny.grid(row=3, column=3)
        
        ttk.Label(frame, text="Z Steps:").grid(row=4, column=0)
        self.nz = ttk.Entry(frame)
        self.nz.grid(row=4, column=1)
        
        ttk.Button(frame, text="Create Coordinates", command=self.create_coords).grid(row=5, column=1)
        ttk.Button(frame, text="Save to File", command=self.save_file).grid(row=5, column=2)

    def create_coords(self):
        try:
            coords = [
                float(self.x_start.get()), float(self.y_start.get()),
                float(self.z_start.get()), float(self.x_end.get()),
                float(self.y_end.get()), float(self.z_end.get()),
                int(self.nx.get()), int(self.ny.get()), int(self.nz.get())
            ]
            self.asc.create_coordinates(coords)
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid input values")

    def save_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            self.asc.write_coordinates(filename)

    def run(self):
        self.root.mainloop()

def asctest():
    ASC = AutoStageCoordcreator()
    ASC.set_rounding(2, 2, 2)
    ASC.create_coordinates([121, 101.3, 150, 126.32, 132.23, 150, 43, 86, 0])
    textfile = 'c2.txt'
    ASC.write_coordinates(textfile)
    print(f"Coordinates created and written to {textfile}.")

def rungui():
    gui = AutoStageGUI()
    gui.run()

# example usage
if __name__ == "__main__":
    rungui()
    # asctest()  # Uncomment to run the test function instead of the GUI
