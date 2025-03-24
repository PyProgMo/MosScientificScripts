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
        self.x_min = tk.DoubleVar(value=490)
        self.x_max = tk.DoubleVar(value=1000.1)
        self.y_min = tk.DoubleVar(value=-0.05)
        self.y_max = tk.DoubleVar(value=1.1)
        
        self.create_labeled_entry_with_autoscale("X Min:", self.x_min, self.auto_scale_x_min)
        self.create_labeled_entry_with_autoscale("X Max:", self.x_max, self.auto_scale_x_max)
        self.create_labeled_entry_with_autoscale("Y Min:", self.y_min, self.auto_scale_y_min)
        self.create_labeled_entry_with_autoscale("Y Max:", self.y_max, self.auto_scale_y_max)
        
        # Tick range inputs
        self.x_tick = tk.DoubleVar(value=50)
        self.y_tick = tk.DoubleVar(value=0.2)
        
        self.create_labeled_entry("X Tick:", self.x_tick)
        self.create_labeled_entry("Y Tick:", self.y_tick)
        
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
        self.font_options = ["Arial", "Times New Roman", "Courier New", "Comic Sans MS", "Verdana"]
        self.selected_font = tk.StringVar(value="Arial")
        tk.Label(self.root, text="Select Font:").pack()
        self.font_dropdown = ttk.Combobox(self.root, textvariable=self.selected_font, values=self.font_options)
        self.font_dropdown.pack()
        
        # Axis labels
        self.x_label = tk.StringVar(value="Wavelength (nm)")
        self.y_label = tk.StringVar(value="norm. Intensity")
        
        self.create_labeled_entry("X Axis Label:", self.x_label)
        self.create_labeled_entry("Y Axis Label:", self.y_label)
        
        # Line properties (per graph)
        self.line_properties = []  # List to store properties for each graph
        
        # Add one set of properties by default
        self.add_line_property_set()
        
        # Grid option
        self.show_grid = tk.BooleanVar(value=False)
        self.grid_check = tk.Checkbutton(self.root, text="Show Grid", variable=self.show_grid)
        self.grid_check.pack()
        
        # Normalize data checkbox
        self.normalize_data = tk.BooleanVar(value=True)
        self.normalize_check = tk.Checkbutton(self.root, text="Normalize Data by 1", variable=self.normalize_data)
        self.normalize_check.pack()

        # Save path
        self.save_path = tk.StringVar(value=os.getcwd())
        self.path_label = tk.Label(self.root, text=f"Save Path: {self.save_path.get()}")
        self.path_label.pack()
        self.change_path_button = tk.Button(self.root, text="Change Path", command=self.change_path)
        self.change_path_button.pack()
        
        # File name entry
        self.file_name = tk.StringVar(value="plot.png")
        self.create_labeled_entry("File Name:", self.file_name)
        
        # Plot and Save Buttons
        self.plot_button = tk.Button(self.root, text="Plot", command=self.plot)
        self.plot_button.pack()
        self.save_button = tk.Button(self.root, text="Save Plot", command=self.save_plot)
        self.save_button.pack()
        
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
            'line_style': tk.StringVar(value="Solid")  # Default as a key, not value
        }

        self.line_properties.append(line_properties)

        frame = tk.Frame(self.root)
        frame.pack()

        tk.Label(frame, text="Line Thickness:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['line_thickness']).pack(side=tk.LEFT)

        tk.Label(frame, text="Line Color:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['line_color']).pack(side=tk.LEFT)

        tk.Label(frame, text="Legend Label:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['legend_label']).pack(side=tk.LEFT)

        # Line Style Dropdown
        tk.Label(frame, text="Line Style:").pack(side=tk.LEFT)
        style_menu = tk.OptionMenu(frame, line_properties['line_style'], *line_styles.keys())
        style_menu.pack(side=tk.LEFT)

        # Store the mapping for later use
        line_properties['style_map'] = line_styles  # Store the dictionary for easy access later


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
            
            # Normalize data if checkbox is selected
            if self.normalize_data.get():
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
