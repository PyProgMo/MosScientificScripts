import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, ttk
import os

class PlottingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Plotting Tool")
        
        # File selection for multiple files
        self.file_label = tk.Label(root, text="Selected Files: None")
        self.file_label.pack()
        self.select_files_button = tk.Button(root, text="Select Files", command=self.select_files)
        self.select_files_button.pack()
        
        # Axis range inputs
        axis_frame = tk.Frame(self.root)
        axis_frame.pack()

        self.x_min = tk.DoubleVar(value=490)
        self.x_max = tk.DoubleVar(value=1000.1)
        self.y_min = tk.DoubleVar(value=-0.05)
        self.y_max = tk.DoubleVar(value=1.1)

        self.create_labeled_entry_in_frame("X Min:", self.x_min, axis_frame)
        self.create_labeled_entry_in_frame("X Max:", self.x_max, axis_frame)
        self.create_labeled_entry_in_frame("Y Min:", self.y_min, axis_frame)
        self.create_labeled_entry_in_frame("Y Max:", self.y_max, axis_frame)
        
    
        
        # Tick range inputs
        tick_frame = tk.Frame(self.root)
        tick_frame.pack()

        self.x_tick = tk.DoubleVar(value=50)
        self.y_tick = tk.DoubleVar(value=0.2)
        
        self.create_labeled_entry_in_frame("X Tick:", self.x_tick, tick_frame)
        self.create_labeled_entry_in_frame("Y Tick:", self.y_tick, tick_frame)
        
        # Font settings
        self.label_fontsize = tk.IntVar(value=24)
        self.tick_fontsize = tk.IntVar(value=22)
        self.legend_fontsize = tk.IntVar(value=22)
        
        # Create a frame for font size selection to pack widgets horizontally
        font_frame = tk.Frame(self.root)
        font_frame.pack()

        self.create_labeled_entry_in_frame("Label Font Size:", self.label_fontsize, font_frame)
        self.create_labeled_entry_in_frame("Tick Font Size:", self.tick_fontsize, font_frame)
        self.create_labeled_entry_in_frame("Legend Font Size:", self.legend_fontsize, font_frame)
        
        # Font selection dropdown
        font_select_frame = tk.Frame(self.root)
        font_select_frame.pack()
        tk.Label(font_select_frame, text="Select Font:").pack(side=tk.LEFT)
        self.font_options = ["Arial", "Times New Roman", "Courier New", "Comic Sans MS", "Verdana"]
        self.selected_font = tk.StringVar(value="Arial")
        self.font_dropdown = ttk.Combobox(font_select_frame, textvariable=self.selected_font, values=self.font_options)
        self.font_dropdown.pack(side=tk.LEFT)
        
        # Axis labels
        label_frame = tk.Frame(self.root)
        label_frame.pack()

        self.x_label = tk.StringVar(value="Wavelength (nm)")
        self.y_label = tk.StringVar(value="norm. Intensity")
        
        self.create_labeled_entry_in_frame("X Axis Label:", self.x_label, label_frame)
        self.create_labeled_entry_in_frame("Y Axis Label:", self.y_label, label_frame)
        
        # Grid and Normalize data options
        options_frame = tk.Frame(self.root)
        options_frame.pack()

        self.show_grid = tk.BooleanVar(value=False)
        self.grid_check = tk.Checkbutton(options_frame, text="Show Grid", variable=self.show_grid)
        self.grid_check.pack(side=tk.LEFT)

        self.normalize_data = tk.BooleanVar(value=False)
        self.normalize_check = tk.Checkbutton(options_frame, text="Normalize by Point", variable=self.normalize_data)
        self.normalize_check.pack(side=tk.LEFT)

        self.normalize_max = tk.BooleanVar(value=True)
        self.normalize_max_check = tk.Checkbutton(options_frame, text="Normalize by Max", variable=self.normalize_max)
        self.normalize_max_check.pack(side=tk.LEFT)

        # Save path
        self.save_path = tk.StringVar(value=os.getcwd())
        self.path_label = tk.Label(self.root, text=f"Save Path: {self.save_path.get()}")
        self.path_label.pack()
        self.change_path_button = tk.Button(self.root, text="Change Path", command=self.change_path)
        self.change_path_button.pack()
        
        # File name entry
        self.file_name = tk.StringVar(value="plot.png")
        
        # Plot, File Name Entry, and Save Buttons in a single frame
        action_frame = tk.Frame(self.root)
        action_frame.pack()

        self.plot_button = tk.Button(action_frame, text="Plot", command=self.plot)
        self.plot_button.pack(side=tk.LEFT)
        
        self.create_labeled_entry_in_frame("File Name:", self.file_name, action_frame)
        
        self.save_button = tk.Button(action_frame, text="Save Plot", command=self.save_plot)
        self.save_button.pack(side=tk.LEFT)
        
        # Initialize line properties list
        self.line_properties = []  # List to store properties for each graph

        # Frame to hold line property sets for each file
        self.line_properties_frame = tk.Frame(self.root)
        self.line_properties_frame.pack(anchor="w", pady=10)

        self.filenames = []  # List to hold multiple filenames
        self.fig = None
    
    def create_labeled_entry(self, label, variable):
        frame = tk.Frame(self.root)
        frame.pack()
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=variable).pack(side=tk.LEFT)
    
    def create_labeled_entry_in_frame(self, label, variable, frame):
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=variable).pack(side=tk.LEFT)

    def create_labeled_entry_with_autoscale(self, label, variable, command):
        frame = tk.Frame(self.root)
        frame.pack()
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=variable).pack(side=tk.LEFT)
        tk.Button(frame, text="Auto", command=command).pack(side=tk.LEFT)
    

    def add_line_property_set(self, filename=None):
        # Dictionary mapping readable names to Matplotlib linestyles
        line_styles = {
            "Solid": "-", 
            "Dotted": ":", 
            "Dashed": "--", 
            "Dash-dot": "-.", 
            "None": "None"
        }

        line_properties = {
            'line_thickness': tk.DoubleVar(value=1.5),
            'line_color': tk.StringVar(value="black"),
            'legend_label': tk.StringVar(value=os.path.basename(filename) if filename else "Graph"),
            'line_style': tk.StringVar(value="Solid"),  # Default as a key, not value
            'normalize_point': tk.DoubleVar(value=1.0),  # Default normalization point for this file
            'style_map': line_styles  # Add the style_map to the line_properties dictionary
        }

        self.line_properties.append(line_properties)

        # Create and display the line property frame for this file
        self.create_line_property_frame(len(self.line_properties) - 1, line_properties)

    def create_line_property_frame(self, index, line_properties):
        frame = tk.Frame(self.line_properties_frame)
        frame.pack(anchor="w", pady=2)

        tk.Label(frame, text=f"File {index + 1}: {os.path.basename(self.filenames[index])}").pack(side=tk.TOP, anchor="w")

        tk.Label(frame, text="Line Thickness:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['line_thickness']).pack(side=tk.LEFT)

        tk.Label(frame, text="Line Color:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['line_color']).pack(side=tk.LEFT)

        tk.Label(frame, text="Legend Label:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['legend_label']).pack(side=tk.LEFT)

        # Line Style Dropdown
        tk.Label(frame, text="Line Style:").pack(side=tk.LEFT)
        style_menu = tk.OptionMenu(frame, line_properties['line_style'], *line_properties['style_map'].keys())
        style_menu.pack(side=tk.LEFT)

        # Normalization Point Entry
        tk.Label(frame, text="Normalize Point:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['normalize_point']).pack(side=tk.LEFT)

    def auto_scale_x_min(self):
        if self.filenames:
            x_data = [np.loadtxt(file, unpack=True)[0] for file in self.filenames]
            self.x_min.set(np.floor(min([min(x) for x in x_data]) / self.x_tick.get()) * self.x_tick.get())
    
    def auto_scale_x_max(self):
        if self.filenames:
            x_data = [np.loadtxt(file, unpack=True)[0] for file in self.filenames]
            self.x_max.set(np.ceil(max([max(x) for x in x_data]) / self.x_tick.get()) * self.x_tick.get())
    
    def auto_scale_y_min(self):
        if self.filenames:
            y_data = [np.loadtxt(file, unpack=True)[1] for file in self.filenames]
            self.y_min.set(np.floor(min([min(y) for y in y_data]) / self.y_tick.get()) * self.y_tick.get())
    
    def auto_scale_y_max(self):
        if self.filenames:
            y_data = [np.loadtxt(file, unpack=True)[1] for file in self.filenames]
            self.y_max.set(np.ceil(max([max(y) for y in y_data]) / self.y_tick.get()) * self.y_tick.get())
    
    def select_files(self):
        self.filenames = filedialog.askopenfilenames()
        self.file_label.config(text=f"Selected Files: {', '.join(self.filenames)}")
        
        # Set default file name as the first selected file's name (without extension)
        if self.filenames:
            default_file_name = os.path.splitext(os.path.basename(self.filenames[0]))[0]
            self.file_name.set(default_file_name)
        
        # Ensure the number of line property sets matches the number of files selected
        while len(self.line_properties) < len(self.filenames):
            # Pass the filename to set legend_label automatically
            self.add_line_property_set(self.filenames[len(self.line_properties)])
        
        # Remove extra line property sets if files are deselected
        while len(self.line_properties) > len(self.filenames):
            self.line_properties.pop()
        
        # Clear and recreate the line property frames
        for widget in self.line_properties_frame.winfo_children():
            widget.destroy()
        
        for i, line_props in enumerate(self.line_properties):
            self.create_line_property_frame(i, line_props)

    def change_path(self):
        new_path = filedialog.askdirectory()
        if new_path:
            self.save_path.set(new_path)
            self.path_label.config(text=f"Save Path: {self.save_path.get()}")
    
    def plot(self):
        if not self.filenames:
            print("No files selected.")
            return
        
        plt.figure(figsize=(10, 6))
        
        # Plot each selected file with corresponding line properties
        for i, filename in enumerate(self.filenames):
            data_x, data_y = np.loadtxt(filename, unpack=True)
            
            # Normalize data by point if checkbox is selected
            if self.normalize_data.get():
                normalize_point = self.line_properties[i]['normalize_point'].get()
                closest_index = (np.abs(data_x - normalize_point)).argmin()
                data_y = data_y / data_y[closest_index]
            
            # Normalize data by maximum if checkbox is selected
            if self.normalize_max.get():
                data_y = data_y / np.max(data_y)
            
            # Get line properties for the current graph
            line_props = self.line_properties[i]
            plt.plot(data_x, data_y, 
                 color=line_props['line_color'].get(), 
                 linewidth=line_props['line_thickness'].get(), 
                 linestyle=line_props['style_map'][line_props['line_style'].get()],  # Map key to value
                 label=line_props['legend_label'].get())
                
        font = self.selected_font.get()
        legend_font = {'family': font, 'weight': 'normal', 'size': self.legend_fontsize.get()}
        label_font = {'family': font, 'size': self.label_fontsize.get()}
        tick_font = {'family': font, 'size': self.tick_fontsize.get()}
        
        # Set labels with the selected fonts
        plt.xlabel(self.x_label.get(), fontdict=label_font)
        plt.ylabel(self.y_label.get(), fontdict=label_font)
        
        # Set tick intervals and font
        x_ticks = np.arange(0, np.ceil(self.x_max.get() / self.x_tick.get()) * self.x_tick.get(), self.x_tick.get())
        y_ticks = np.arange(0, np.ceil(self.y_max.get() / self.y_tick.get()) * self.y_tick.get(), self.y_tick.get())

        # Set tick positions for the x and y axes
        plt.xticks(x_ticks, fontsize=self.tick_fontsize.get(), fontname=font)
        plt.yticks(y_ticks, fontsize=self.tick_fontsize.get(), fontname=font)
        
        # Set legend with the selected font
        plt.legend(fontsize=self.legend_fontsize.get(), prop=legend_font)
        
        # Set grid and axis limits
        plt.grid(self.show_grid.get())
        plt.xlim(self.x_min.get(), self.x_max.get())
        plt.ylim(self.y_min.get(), self.y_max.get())
        
        # Adjust layout to make sure everything fits
        plt.tight_layout()

        # Show the plot
        self.fig = plt.gcf()
        plt.show()
    
    def save_plot(self):
        if self.fig:
            save_filepath = os.path.join(self.save_path.get(), self.file_name.get() + ".png")
            self.fig.savefig(save_filepath, dpi=1200)
            print(f"Plot saved as {save_filepath}")
        else:
            print("No plot available to save.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlottingTool(root)
    root.mainloop()
