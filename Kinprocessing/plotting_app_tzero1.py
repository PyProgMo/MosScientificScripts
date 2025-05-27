import tkinter as tk
from tkinter import Canvas
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.lines as lines

import Thorlabs_Pt_reader as Pt_reader
from matplotlib.backends._backend_tk import NavigationToolbar2Tk

class GetXPlotter:
    def __init__(self, master, tarray, array, framex, framey, var=None):
        self.master = master
        self.framex = framex
        self.framey = framey
        self.tarray = tarray
        self.array = array
        self.marker_position = 0
        self.inpvar = var
        self.dragging = False

        self.ret_array = self.array[:]
        self.ret_tarray = self.tarray[:]

    def initplot(self):
        # Initialize drag state
        self.dragging = False
        self.zoom_mode_active = False
        
        # Create container frame for plot and toolbar
        self.plot_frame = tk.Frame(self.master)
        self.plot_frame.grid(row=0, column=0, columnspan=2, sticky='nsew', rowspan=6)
        
        # Create matplotlib figure and canvas
        self.fig = Figure(figsize=(self.framex, self.framey), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar inside the same frame
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Store original zoom handler and override
        self.original_zoom_handler = self.toolbar.zoom
        def custom_zoom_handler(*args, **kwargs):
            self._custom_zoom_handler(*args, **kwargs)
        self.toolbar.zoom = custom_zoom_handler
        
        self.t0_entry = tk.Entry(self.master)
        
        # Connect mouse events for dragging the marker
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)
    
    def on_press(self, event):
        if event.inaxes == self.ax:
            self.dragging = True
    def _custom_zoom_handler(self, *args, **kwargs):
        """Custom zoom handler that tracks zoom state"""
        self.zoom_mode_active = not self.zoom_mode_active
        self.original_zoom_handler(*args, **kwargs)
        self.zoom_mode_active = not self.zoom_mode_active
        self.original_zoom_handler()
        
    def on_motion(self, event):
        if not self.zoom_mode_active and self.dragging and event.inaxes == self.ax:
            self.update_marker(event.xdata)

    def on_release(self, event):
        self.dragging = False

    def update_marker(self, xpos):
        # Calculate new marker position
        self.marker_position = np.clip(np.searchsorted(self.tarray, xpos), 0, len(self.tarray) - 1)
        # Update the entry field
        self.t0_entry.delete(0, tk.END)
        self.t0_entry.insert(0, str(self.tarray[self.marker_position]))
        
        # Redraw plot without resetting zoom
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        self.plot()
        
        # Restore zoom if not in zoom mode
        if not self.zoom_mode_active:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.canvas.draw()

    def plot(self):
        # Clear the current plot
        self.ax.clear()
        
        # Plot the data
        self.ax.plot(self.tarray, self.array, label='Power vs Time', color='blue')
        
        # Add a vertical line at the marker position
        self.marker_line = lines.Line2D([self.tarray[self.marker_position], self.tarray[self.marker_position]], 
                                         [self.ax.get_ylim()[0], self.ax.get_ylim()[1]], 
                                         color='red', linestyle='--')
        self.ax.add_line(self.marker_line)
        
        # Set labels and title
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Power (W)')

        # set left to 0.05 and right to 0.98
        self.fig.subplots_adjust(left=0.055, right=0.98)
        
        # Add grid and legend
        self.ax.grid(True)
        self.ax.legend()
        
        # Draw the canvas
        self.canvas.draw()
    
    def get_power_chroped(self):
        # make sure the marker position is within bounds, if marker is befor 0, return timearray[:

        if self.marker_position < 0:
            self.marker_position = 0
        
        if self.marker_position >= len(self.tarray):
            self.marker_position = 0
        
        # chrop the power data and time array from the marker position to the end and normalize it
        self.ret_array = np.divide(self.array[self.marker_position:], np.amax(self.array[self.marker_position:]))
        self.ret_tarray = np.asarray(self.tarray[self.marker_position:])-self.marker_position

        # Return the cropped power data starting from the marker position
        return self.ret_array, self.ret_tarray

    def destroy(self):
        # Destroy the plot frame and toolbar
        self.plot_frame.destroy()
        self.toolbar.destroy()
        self.canvas.get_tk_widget().destroy()

        # Reset the dragging state
        self.dragging = False

if __name__ == "__main__":
    root = tk.Tk()
    spec = Pt_reader.obtain_power_data('Sample.csv')
    tarray = spec['t'].to_numpy()
    array = spec['Power'].to_numpy()
    # testing with a sine wave
    #tarray = np.linspace(0, 10, 100)
    #array = np.sin(tarray)-0.5

    plotter = GetXPlotter(root, tarray, array, 10, 4)
    plotter.initplot()
    plotter.plot()
    root.mainloop()
