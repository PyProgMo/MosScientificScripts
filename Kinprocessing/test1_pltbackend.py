import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotManager:
    """Manages individual plots so they can be updated separately."""
    
    def __init__(self, master, data):
        self.master = master
        self.data = data  # Store the initial data array
        self.figure, self.ax = plt.subplots()  # Create a figure
        self.image = self.ax.imshow(self.data, cmap="viridis")  # Initial plot
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()  # Pack the canvas into the Tkinter window
    
    def update_plot(self, new_data):
        """Update the plot with new data."""
        self.data = new_data
        self.image.set_data(self.data)  # Update imshow data
        self.ax.set_title("Updated Plot")  # Change the title
        self.canvas.draw()  # Redraw the canvas

def plot_2x2():
    """Plots a 2x2 array."""
    data = np.array([[1, 2], [3, 4]])  # Example 2x2 array
    global plot1
    plot1 = PlotManager(root, data)  # Create an instance of the plot manager

def plot_3x3():
    """Plots a 3x3 array."""
    data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])  # Example 3x3 array
    global plot2
    plot2 = PlotManager(root, data)  # Create another instance of the plot manager

def modify_plot1():
    """Modify Plot 1 separately."""
    if plot1:
        new_data = np.random.rand(2, 2) * 10  # Generate new random 2x2 data
        plot1.update_plot(new_data)

def modify_plot2():
    """Modify Plot 2 separately."""
    if plot2:
        new_data = np.random.rand(3, 3) * 10  # Generate new random 3x3 data
        plot2.update_plot(new_data)

# Tkinter setup
root = tk.Tk()
root.geometry("600x600")
root.title("Tkinter Imshow Plot Manager")

# Buttons to plot
btn1 = tk.Button(root, text="Plot 2x2", command=plot_2x2)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="Plot 3x3", command=plot_3x3)
btn2.pack(pady=10)

# Buttons to modify plots separately
btn3 = tk.Button(root, text="Modify Plot 1", command=modify_plot1)
btn3.pack(pady=10)

btn4 = tk.Button(root, text="Modify Plot 2", command=modify_plot2)
btn4.pack(pady=10)

plot1 = None  # Initialize variables for the plots
plot2 = None

root.mainloop()
