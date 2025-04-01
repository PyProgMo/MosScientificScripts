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
        
        file_buttons_frame = tk.Frame(root)
        file_buttons_frame.pack()

        self.select_files_button = tk.Button(file_buttons_frame, text="Select Files", command=self.select_files)
        self.select_files_button.pack(side=tk.LEFT)

        self.clear_files_button = tk.Button(file_buttons_frame, text="Clear Files", command=self.clear_files)
        self.clear_files_button.pack(side=tk.LEFT)

        self.export_defaults_button = tk.Button(file_buttons_frame, text="Export Defaults", command=self.export_defaults)
        self.export_defaults_button.pack(side=tk.LEFT)

        self.load_defaults_button = tk.Button(file_buttons_frame, text="Load Defaults", command=self.load_defaults)
        self.load_defaults_button.pack(side=tk.LEFT)
        
        # Axis range inputs and tick range inputs in a single line
        axis_and_ticks_frame = tk.Frame(self.root)
        axis_and_ticks_frame.pack()

        self.x_min = tk.DoubleVar(value=490)
        self.x_max = tk.DoubleVar(value=1000.1)
        self.y_min = tk.DoubleVar(value=-0.05)
        self.y_max = tk.DoubleVar(value=1.1)

        self.create_labeled_entry_with_autoscale("X Min:", self.x_min, self.auto_scale_x_min, axis_and_ticks_frame)
        self.create_labeled_entry_with_autoscale("X Max:", self.x_max, self.auto_scale_x_max, axis_and_ticks_frame)
        self.create_labeled_entry_with_autoscale("Y Min:", self.y_min, self.auto_scale_y_min, axis_and_ticks_frame)
        self.create_labeled_entry_with_autoscale("Y Max:", self.y_max, self.auto_scale_y_max, axis_and_ticks_frame)

        self.x_tick = tk.DoubleVar(value=50)
        self.y_tick = tk.DoubleVar(value=0.2)
        
        self.create_labeled_entry_in_frame("X Tick:", self.x_tick, axis_and_ticks_frame)
        self.create_labeled_entry_in_frame("Y Tick:", self.y_tick, axis_and_ticks_frame)
        
        # Font settings and axis labels in a single line
        font_and_labels_frame = tk.Frame(self.root)
        font_and_labels_frame.pack()

        self.label_fontsize = tk.IntVar(value=24)
        self.tick_fontsize = tk.IntVar(value=22)
        self.legend_fontsize = tk.IntVar(value=22)

        self.create_labeled_entry_in_frame("Label Font Size:", self.label_fontsize, font_and_labels_frame)
        self.create_labeled_entry_in_frame("Tick Font Size:", self.tick_fontsize, font_and_labels_frame)
        self.create_labeled_entry_in_frame("Legend Font Size:", self.legend_fontsize, font_and_labels_frame)

        tk.Label(font_and_labels_frame, text="Select Font:").pack(side=tk.LEFT)
        self.font_options = ["Arial", "Times New Roman", "Courier New", "Comic Sans MS", "Verdana"]
        self.selected_font = tk.StringVar(value="Arial")
        self.font_dropdown = ttk.Combobox(font_and_labels_frame, textvariable=self.selected_font, values=self.font_options)
        self.font_dropdown.pack(side=tk.LEFT)

        self.x_label = tk.StringVar(value="Wavelength (nm)")
        self.y_label = tk.StringVar(value="norm. Intensity")
        
        self.create_labeled_entry_in_frame("X Axis Label:", self.x_label, font_and_labels_frame)
        self.create_labeled_entry_in_frame("Y Axis Label:", self.y_label, font_and_labels_frame)
        
        # Grid, Normalize data options
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

        # Fit options in a separate line
        fit_options_frame = tk.Frame(self.root)
        fit_options_frame.pack()

        self.fit_enabled = tk.BooleanVar(value=False)
        self.fit_check = tk.Checkbutton(fit_options_frame, text="Enable Fit", variable=self.fit_enabled, command=self.update_fit_options)
        self.fit_check.pack(side=tk.LEFT)

        self.fit_type = tk.StringVar(value="Linear")
        self.fit_dropdown = ttk.Combobox(fit_options_frame, textvariable=self.fit_type, 
                                         values=["Linear", "Polynomial (x^2)", "Polynomial (x^3)", 
                                                 "Polynomial (x^4)", "Polynomial (x^5)", "Polynomial (x^6)", 
                                                 "Exponential"], state="disabled")
        self.fit_dropdown.pack(side=tk.LEFT)

        self.fit_equation = tk.StringVar(value="Fit Equation: N/A")
        self.fit_equation_label = tk.Label(fit_options_frame, textvariable=self.fit_equation)
        self.fit_equation_label.pack(side=tk.LEFT)

        # Fit line style, color, and thickness
        self.fit_line_styles = {
            "Solid": "-", 
            "Dashed": "--", 
            "Dash-dot": "-.", 
            "Dotted": ":"
        }
        self.fit_line_style = tk.StringVar(value="Solid")
        self.fit_line_color = tk.StringVar(value="black")
        self.fit_line_thickness = tk.DoubleVar(value=1.5)

        tk.Label(fit_options_frame, text="Style:").pack(side=tk.LEFT)
        self.fit_style_dropdown = ttk.Combobox(fit_options_frame, textvariable=self.fit_line_style, values=list(self.fit_line_styles.keys()), state="readonly")
        self.fit_style_dropdown.pack(side=tk.LEFT)

        tk.Label(fit_options_frame, text="Color:").pack(side=tk.LEFT)
        tk.Entry(fit_options_frame, textvariable=self.fit_line_color).pack(side=tk.LEFT)

        tk.Label(fit_options_frame, text="Thickness:").pack(side=tk.LEFT)
        tk.Entry(fit_options_frame, textvariable=self.fit_line_thickness).pack(side=tk.LEFT)

        # Fit legend label
        self.fit_legend_label = tk.StringVar(value="Fit")
        tk.Label(fit_options_frame, text="Fit Legend Label:").pack(side=tk.LEFT)
        tk.Entry(fit_options_frame, textvariable=self.fit_legend_label).pack(side=tk.LEFT)
        
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

        # Remove the old Export and Load Defaults section
        # defaults_frame = tk.Frame(self.root)
        # defaults_frame.pack()

        # self.export_defaults_button = tk.Button(defaults_frame, text="Export Defaults", command=self.export_defaults)
        # self.export_defaults_button.pack(side=tk.LEFT)

        # self.load_defaults_button = tk.Button(defaults_frame, text="Load Defaults", command=self.load_defaults)
        # self.load_defaults_button.pack(side=tk.LEFT)
    
    def create_labeled_entry(self, label, variable):
        frame = tk.Frame(self.root)
        frame.pack()
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=variable).pack(side=tk.LEFT)
    
    def create_labeled_entry_in_frame(self, label, variable, frame):
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=variable).pack(side=tk.LEFT)

    def create_labeled_entry_with_autoscale(self, label, variable, command, frame):
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
            'plot_as_points': tk.BooleanVar(value=False),  # Option to plot as points
            'point_size': tk.DoubleVar(value=20),  # Default point size
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

        # Plot as Points Checkbox
        tk.Checkbutton(frame, text="Scatter Graph", variable=line_properties['plot_as_points']).pack(side=tk.LEFT)

        # Point Size Entry
        tk.Label(frame, text="Point Size:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['point_size']).pack(side=tk.LEFT)

    def detect_data_start(self, filename):
        """Detect the line number where numerical data starts."""
        with open(filename, 'r') as file:
            for i, line in enumerate(file):
                # Try to parse the line as numerical data
                try:
                    float(line.split()[0])  # Check if the first column is a number
                    return i  # Return the line number where data starts
                except (ValueError, IndexError):
                    continue
        raise ValueError(f"No numerical data found in file: {filename}")

    def auto_scale_x_min(self):
        if self.filenames:
            x_data = [
                np.loadtxt(file, unpack=True, skiprows=self.detect_data_start(file), usecols=0)
                for file in self.filenames
            ]
            self.x_min.set(np.floor(min([min(x) for x in x_data if len(x) > 0]) / self.x_tick.get()) * self.x_tick.get())
    
    def auto_scale_x_max(self):
        if self.filenames:
            x_data = [
                np.loadtxt(file, unpack=True, skiprows=self.detect_data_start(file), usecols=0)
                for file in self.filenames
            ]
            self.x_max.set(np.ceil(max([max(x) for x in x_data if len(x) > 0]) / self.x_tick.get()) * self.x_tick.get())
    
    def auto_scale_y_min(self):
        if self.filenames:
            y_data = [
                np.loadtxt(file, unpack=True, skiprows=self.detect_data_start(file), usecols=1)
                for file in self.filenames
            ]
            self.y_min.set(np.floor(min([min(y) for y in y_data if len(y) > 0]) / self.y_tick.get()) * self.y_tick.get())
    
    def auto_scale_y_max(self):
        if self.filenames:
            y_data = [
                np.loadtxt(file, unpack=True, skiprows=self.detect_data_start(file), usecols=1)
                for file in self.filenames
            ]
            self.y_max.set(np.ceil(max([max(y) for y in y_data if len(y) > 0]) / self.y_tick.get()) * self.y_tick.get())
    
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

    def clear_files(self):
        """Clear the selected files and reset related UI elements."""
        self.filenames = []
        self.file_label.config(text="Selected Files: None")
        self.line_properties.clear()
        for widget in self.line_properties_frame.winfo_children():
            widget.destroy()

    def change_path(self):
        new_path = filedialog.askdirectory()
        if new_path:
            self.save_path.set(new_path)
            self.path_label.config(text=f"Save Path: {self.save_path.get()}")
    
    def update_fit_options(self):
        """Enable or disable the fit dropdown based on the checkbox."""
        if self.fit_enabled.get():
            self.fit_dropdown.config(state="readonly")
        else:
            self.fit_dropdown.config(state="disabled")
            self.fit_equation.set("Fit Equation: N/A")

    def plot(self):
        if not self.filenames:
            print("No files selected.")
            return
        
        plt.figure(figsize=(10, 6))
        
        # Plot each selected file with corresponding line properties
        for i, filename in enumerate(self.filenames):
            data_start = self.detect_data_start(filename)
            data = np.loadtxt(filename, unpack=True, skiprows=data_start)
            if data.ndim < 2 or data.shape[0] < 2:
                print(f"Skipping file {filename}: insufficient data.")
                continue
            data_x, data_y = data[0], data[1]
            
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
            if line_props['plot_as_points'].get():
                # Plot as points
                plt.scatter(data_x, data_y, 
                            color=line_props['line_color'].get(), 
                            s=line_props['point_size'].get(), 
                            label=line_props['legend_label'].get())
            else:
                # Plot as a line
                plt.plot(data_x, data_y, 
                         color=line_props['line_color'].get(), 
                         linewidth=line_props['line_thickness'].get(), 
                         linestyle=line_props['style_map'][line_props['line_style'].get()],  # Map key to value
                         label=line_props['legend_label'].get())
                
            # Perform fitting if enabled
            if self.fit_enabled.get():
                fit_type = self.fit_type.get()
                if fit_type == "Linear":
                    coeffs = np.polyfit(data_x, data_y, 1)
                    fit_func = np.poly1d(coeffs)
                    self.fit_equation.set(f"Fit Equation: y = {coeffs[0]:.3f}x + {coeffs[1]:.3f}")
                elif fit_type.startswith("Polynomial"):
                    degree = int(fit_type.split("^")[1][0])  # Extract the degree from the dropdown text
                    coeffs = np.polyfit(data_x, data_y, degree)
                    fit_func = np.poly1d(coeffs)
                    equation_terms = [f"{coeff:.3f}x^{i}" for i, coeff in enumerate(reversed(coeffs))]
                    self.fit_equation.set(f"Fit Equation: y = {' + '.join(equation_terms)}")
                elif fit_type == "Exponential":
                    # Filter out invalid data_y values
                    valid_indices = data_y > 0
                    if not np.any(valid_indices):
                        print("Exponential fit failed: No valid data points.")
                        continue

                    filtered_x = data_x[valid_indices]
                    filtered_y = data_y[valid_indices]

                    # Perform logarithmic transformation and fit
                    log_y = np.log(filtered_y)
                    coeffs = np.polyfit(filtered_x, log_y, 1)
                    fit_func = lambda x: np.exp(coeffs[1]) * np.exp(coeffs[0] * x)
                    self.fit_equation.set(f"Fit Equation: y = {np.exp(coeffs[1]):.3f}e^({coeffs[0]:.3f}x)")

                # Plot the fit function with user-defined style, color, thickness, and legend label
                fit_x = np.linspace(self.x_min.get(), self.x_max.get(), 500)
                fit_y = fit_func(fit_x)
                plt.plot(fit_x, fit_y, 
                         linestyle=self.fit_line_styles[self.fit_line_style.get()], 
                         color=self.fit_line_color.get(), 
                         linewidth=self.fit_line_thickness.get(), 
                         label=self.fit_legend_label.get())

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

    def export_defaults(self):
        """Export current default values to a .txt file."""
        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if save_path:
            with open(save_path, 'w') as file:
                file.write(f"x_min={self.x_min.get()}\n")
                file.write(f"x_max={self.x_max.get()}\n")
                file.write(f"y_min={self.y_min.get()}\n")
                file.write(f"y_max={self.y_max.get()}\n")
                file.write(f"x_tick={self.x_tick.get()}\n")
                file.write(f"y_tick={self.y_tick.get()}\n")
                file.write(f"label_fontsize={self.label_fontsize.get()}\n")
                file.write(f"tick_fontsize={self.tick_fontsize.get()}\n")
                file.write(f"legend_fontsize={self.legend_fontsize.get()}\n")
                file.write(f"x_label={self.x_label.get()}\n")
                file.write(f"y_label={self.y_label.get()}\n")
                file.write(f"font={self.selected_font.get()}\n")
                file.write(f"show_grid={self.show_grid.get()}\n")
                file.write(f"normalize_data={self.normalize_data.get()}\n")
                file.write(f"normalize_max={self.normalize_max.get()}\n")
            print(f"Defaults exported to {save_path}")

    def load_defaults(self):
        """Load default values from a .txt file."""
        load_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if load_path:
            with open(load_path, 'r') as file:
                for line in file:
                    key, value = line.strip().split('=')
                    if key == "x_min":
                        self.x_min.set(float(value))
                    elif key == "x_max":
                        self.x_max.set(float(value))
                    elif key == "y_min":
                        self.y_min.set(float(value))
                    elif key == "y_max":
                        self.y_max.set(float(value))
                    elif key == "x_tick":
                        self.x_tick.set(float(value))
                    elif key == "y_tick":
                        self.y_tick.set(float(value))
                    elif key == "label_fontsize":
                        self.label_fontsize.set(int(value))
                    elif key == "tick_fontsize":
                        self.tick_fontsize.set(int(value))
                    elif key == "legend_fontsize":
                        self.legend_fontsize.set(int(value))
                    elif key == "x_label":
                        self.x_label.set(value)
                    elif key == "y_label":
                        self.y_label.set(value)
                    elif key == "font":
                        self.selected_font.set(value)
                    elif key == "show_grid":
                        self.show_grid.set(value == "True")
                    elif key == "normalize_data":
                        self.normalize_data.set(value == "True")
                    elif key == "normalize_max":
                        self.normalize_max.set(value == "True")
            print(f"Defaults loaded from {load_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlottingTool(root)
    root.mainloop()
