import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt

class PlotManager:
    """Manages individual plots in separate Matplotlib windows."""

    def __init__(self, data, title):
        self.data = data  # Store initial data
        self.title = title
        self.figure, self.ax = plt.subplots()  # Create a new figure
        self.image = self.ax.imshow(self.data, cmap="viridis")  # Plot imshow
        self.ax.set_title(self.title)  # Set title
        self.figure.canvas.manager.set_window_title(self.title)  # Set window title
        plt.show(block=False)  # Show non-blocking window

    def update_plot(self, new_data):
        """Update the plot with new data."""
        self.data = new_data
        self.image.set_data(self.data)  # Update imshow data
        self.ax.set_title("Updated " + self.title)  # Change title
        self.figure.canvas.draw()  # Redraw figure

def plot_2x2():
    """Creates a new 2x2 plot window."""
    global plot1
    data = np.array([[1, 2], [3, 4]])  # Example 2x2 array
    plot1 = PlotManager(data, "Plot 2x2")  # Store instance

def plot_3x3():
    """Creates a new 3x3 plot window."""
    global plot2
    data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])  # Example 3x3 array
    plot2 = PlotManager(data, "Plot 3x3")  # Store instance

def modify_plot1():
    """Modify Plot 1 separately."""
    if plot1:
        new_data = np.random.rand(2, 2) * 10  # New random 2x2 data
        plot1.update_plot(new_data)

def modify_plot2():
    """Modify Plot 2 separately."""
    if plot2:
        new_data = np.random.rand(3, 3) * 10  # New random 3x3 data
        plot2.update_plot(new_data)

# Tkinter setup
root = tk.Tk()
root.geometry("300x300")
root.title("Tkinter Plot Manager")

# Buttons to create new plot windows
btn1 = tk.Button(root, text="Open Plot 2x2", command=plot_2x2)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="Open Plot 3x3", command=plot_3x3)
btn2.pack(pady=10)

# Buttons to modify separate plots
btn3 = tk.Button(root, text="Modify Plot 1", command=modify_plot1)
btn3.pack(pady=10)

btn4 = tk.Button(root, text="Modify Plot 2", command=modify_plot2)
btn4.pack(pady=10)

plot1 = None  # Store plot instances globally
plot2 = None

root.mainloop()
