import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, ttk
import os

class PlottingTool:
    """
    PlottingTool is a graphical user interface (GUI) application for visualizing and customizing plots 
    from multiple data files. It provides a variety of options for configuring plot appearance, 
    normalization, fitting, and exporting.
    Attributes:
        root (tk.Tk): The root window of the Tkinter application.
        filenames (list): List of selected file paths for plotting.
        line_properties (list): List of dictionaries containing properties for each line/graph.
        fig (matplotlib.figure.Figure): The current matplotlib figure object.
        save_path (tk.StringVar): The directory path where plots will be saved.
        file_name (tk.StringVar): The name of the file to save the plot as.
    Methods:
        __init__(root):
            Initializes the PlottingTool GUI and sets up all widgets and default values.
        create_labeled_entry(label, variable):
            Creates a labeled entry widget in the root window.
        create_labeled_entry_in_frame(label, variable, frame):
            Creates a labeled entry widget inside a specified frame.
        create_labeled_entry_with_autoscale(label, variable, command, frame):
            Creates a labeled entry widget with an "Auto" button for automatic scaling.
        add_line_property_set(filename=None):
            Adds a new set of line properties for a selected file.
        create_line_property_frame(index, line_properties):
            Creates a frame to display and configure line properties for a specific file.
        detect_data_start(filename):
            Detects the line number where numerical data starts in a file.
        auto_scale_x_min():
            Automatically calculates and sets the minimum x-axis value based on the data.
        auto_scale_x_max():
            Automatically calculates and sets the maximum x-axis value based on the data.
        auto_scale_y_min():
            Automatically calculates and sets the minimum y-axis value based on the data.
        auto_scale_y_max():
            Automatically calculates and sets the maximum y-axis value based on the data.
        select_files():
            Opens a file dialog to select multiple files and updates the UI accordingly.
        clear_files():
            Clears the selected files and resets related UI elements.
        change_path():
            Opens a directory dialog to change the save path for plots.
        update_fit_options():
            Enables or disables the fit options based on the "Enable Fit" checkbox.
        plot():
            Generates and displays the plot based on the selected files and user configurations.
        save_plot():
            Saves the current plot to the specified file path.
        export_defaults():
            Exports the current default values to a text file.
        load_defaults():
            Loads default values from a text file.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Plotting Tool")
        
        self.is_table_mode = False
        self.table_file = None  # Store the selected table file
        self.table_delimiter = None
        self.table_columns = []  # Store selected column pairs: [(x_col, y_col), ...]
        self.column_headers = []  # Store column headers from table
        
        # File selection for multiple files
        self.file_label = tk.Label(root, text="Selected Files: None")
        self.file_label.pack()
        
        file_buttons_frame = tk.Frame(root)
        file_buttons_frame.pack()

        self.select_files_button = tk.Button(file_buttons_frame, text="Select Files", command=self.select_files)
        self.select_files_button.pack(side=tk.LEFT)
        
        self.select_table_button = tk.Button(file_buttons_frame, text="Select Table", command=self.select_table)
        self.select_table_button.pack(side=tk.LEFT)

        self.auto_plot_1st_col = tk.BooleanVar(value=False)
        self.auto_plot_check = tk.Checkbutton(file_buttons_frame, text="1st vs All", variable=self.auto_plot_1st_col)
        self.auto_plot_check.pack(side=tk.LEFT)

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

        self.use_nm2eV = tk.BooleanVar(value=False)
        self.nm2eV_check = tk.Checkbutton(options_frame, text="Use nm to eV", variable=self.use_nm2eV)
        self.nm2eV_check.pack(side=tk.LEFT)
        
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

        # Initialize fit line styles
        self.fit_line_styles = {
            "Solid": "-", 
            "Dotted": ":", 
            "Dashed": "--", 
            "Dash-dot": "-.", 
            "None": "None"
        }

        # Initialize fit equation display variable
        # Remove global fit equation display
        # self.fit_equation = tk.StringVar(value="Fit Equation: N/A")
        # self.fit_equation_label = tk.Label(self.root, textvariable=self.fit_equation, anchor="w")
        # self.fit_equation_label.pack(anchor="w", pady=5)
    
    def nm2eV(self, wl_array):
        """Convert wavelength in nm to energy in eV."""
        h = 4.135667696e-15  # Planck's constant in eV·s
        c = 299792458e9  # Speed of light in nm/s
        hc = h * c  # Planck's constant times speed of light in eV·nm
        #eV_array = h * c / wl_array
        eV_array = np.divide(hc, wl_array)  # Convert wavelength to energy in eV
        return eV_array
    
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
            'line_style': tk.StringVar(value="Solid"),
            'normalize_point': tk.DoubleVar(value=1.0),
            'plot_as_points': tk.BooleanVar(value=False),
            'point_size': tk.DoubleVar(value=15),
            'style_map': line_styles,
            'fit_enabled': tk.BooleanVar(value=False),
            'fit_type': tk.StringVar(value="Linear"),
            'fit_line_style': tk.StringVar(value="Solid"),
            'fit_line_color': tk.StringVar(value="black"),
            'fit_line_thickness': tk.DoubleVar(value=1.5),
            'fit_legend_label': tk.StringVar(value="Fit"),
            'fit_equation': tk.StringVar(value="Fit Equation: N/A")  # Separate fit equation for each line
        }

        self.line_properties.append(line_properties)
        self.create_line_property_frame(len(self.line_properties) - 1, line_properties)

    def create_line_property_frame(self, index, line_properties):
        frame = tk.Frame(self.line_properties_frame)
        frame.pack(anchor="w", pady=2)

        display_name = line_properties['legend_label'].get() if self.is_table_mode else os.path.basename(self.filenames[index])
        tk.Label(frame, text=f"Plot {index + 1}: {display_name}").pack(side=tk.TOP, anchor="w")

        tk.Label(frame, text="Line Thickness:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['line_thickness']).pack(side=tk.LEFT)

        tk.Label(frame, text="Line Color:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['line_color']).pack(side=tk.LEFT)

        tk.Label(frame, text="Legend Label:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['legend_label']).pack(side=tk.LEFT)

        tk.Label(frame, text="Line Style:").pack(side=tk.LEFT)
        style_menu = tk.OptionMenu(frame, line_properties['line_style'], *line_properties['style_map'].keys())
        style_menu.pack(side=tk.LEFT)

        tk.Label(frame, text="Normalize Point:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['normalize_point']).pack(side=tk.LEFT)

        tk.Checkbutton(frame, text="Scatter Graph", variable=line_properties['plot_as_points']).pack(side=tk.LEFT)

        tk.Label(frame, text="Point Size:").pack(side=tk.LEFT)
        tk.Entry(frame, textvariable=line_properties['point_size']).pack(side=tk.LEFT)

        # Fit checkbox in line with graph options
        tk.Checkbutton(frame, text="Enable Fit", variable=line_properties['fit_enabled'], 
                       command=lambda: self.toggle_fit_options(fit_options_frame, line_properties)).pack(side=tk.LEFT)

        # Fit options in a new row beneath the graph options
        fit_options_frame = tk.Frame(self.line_properties_frame)
        fit_options_frame.pack(anchor="w", pady=2)  # Align beneath the graph options
        line_properties['fit_options_frame'] = fit_options_frame  # Store the fit options frame for toggling

    def toggle_fit_options(self, fit_options_frame, line_properties):
        # Clear existing widgets in the fit options frame
        for widget in fit_options_frame.winfo_children():
            widget.destroy()

        if line_properties['fit_enabled'].get():
            # Add fitting options horizontally in a new row
            tk.Label(fit_options_frame, text="Fit Type:").pack(side=tk.LEFT)
            fit_dropdown = ttk.Combobox(fit_options_frame, textvariable=line_properties['fit_type'], 
                                        values=["Linear", "Polynomial (x^2)", "Polynomial (x^3)", 
                                                "Polynomial (x^4)", "Polynomial (x^5)", "Polynomial (x^6)", 
                                                "Exponential"], state="readonly")
            fit_dropdown.pack(side=tk.LEFT)

            tk.Label(fit_options_frame, text="Style:").pack(side=tk.LEFT)
            style_dropdown = ttk.Combobox(fit_options_frame, textvariable=line_properties['fit_line_style'], 
                                          values=list(self.fit_line_styles.keys()), state="readonly")
            style_dropdown.pack(side=tk.LEFT)

            tk.Label(fit_options_frame, text="Color:").pack(side=tk.LEFT)
            tk.Entry(fit_options_frame, textvariable=line_properties['fit_line_color']).pack(side=tk.LEFT)

            tk.Label(fit_options_frame, text="Thickness:").pack(side=tk.LEFT)
            tk.Entry(fit_options_frame, textvariable=line_properties['fit_line_thickness']).pack(side=tk.LEFT)

            tk.Label(fit_options_frame, text="Legend Label:").pack(side=tk.LEFT)
            tk.Entry(fit_options_frame, textvariable=line_properties['fit_legend_label']).pack(side=tk.LEFT)

            # Add fit equation display for this specific line
            tk.Label(fit_options_frame, textvariable=line_properties['fit_equation'], anchor="w").pack(side=tk.LEFT)

    def detect_data_start(self, filename):
        """Detect the line number where numerical data starts."""
        with open(filename, 'r') as file:
            for i, line in enumerate(file):
                # Try to parse the line as numerical data
                try:
                    clean_line = line.replace(',', ' ').replace(';', ' ')
                    if not clean_line.strip() or clean_line.startswith('#'):
                        continue
                    float(clean_line.split()[0])  # Check if the first column is a number
                    return i  # Return the line number where data starts
                except (ValueError, IndexError):
                    continue
        raise ValueError(f"No numerical data found in file: {filename}")

    def get_delimiter(self, filename):
        """Detect the delimiter used in the data."""
        try:
            data_start = self.detect_data_start(filename)
            with open(filename, 'r') as f:
                for _ in range(data_start):
                    f.readline()
                line = f.readline()
                if ',' in line: return ','
                if ';' in line: return ';'
                if '\t' in line: return '\t'
        except:
            pass
        return None

    def auto_scale_x_min(self):
        if not self.filenames and not self.is_table_mode:
            return
        
        try:
            if self.is_table_mode:
                # Load from table file
                data_start = self.detect_data_start(self.table_file)
                all_x_data = []
                for x_col, y_col in self.table_columns:
                    x_data = np.loadtxt(
                        self.table_file, unpack=True, skiprows=data_start, usecols=x_col, delimiter=self.table_delimiter
                    )
                    all_x_data.extend(x_data if x_data.ndim > 0 else [x_data])
                x_data = np.array(all_x_data)
            else:
                # Load from multiple files
                x_data = [
                    np.loadtxt(file, unpack=True, skiprows=self.detect_data_start(file), usecols=0, delimiter=self.get_delimiter(file))
                    for file in self.filenames
                ]
                x_data = np.concatenate(x_data)
            
            self.x_min.set(np.floor(min(x_data) / self.x_tick.get()) * self.x_tick.get())
        except Exception as e:
            print(f"Error in auto_scale_x_min: {e}")
    
    def auto_scale_x_max(self):
        if not self.filenames and not self.is_table_mode:
            return
        
        try:
            if self.is_table_mode:
                data_start = self.detect_data_start(self.table_file)
                all_x_data = []
                for x_col, y_col in self.table_columns:
                    x_data = np.loadtxt(
                        self.table_file, unpack=True, skiprows=data_start, usecols=x_col, delimiter=self.table_delimiter
                    )
                    all_x_data.extend(x_data if x_data.ndim > 0 else [x_data])
                x_data = np.array(all_x_data)
            else:
                x_data = [
                    np.loadtxt(file, unpack=True, skiprows=self.detect_data_start(file), usecols=0, delimiter=self.get_delimiter(file))
                    for file in self.filenames
                ]
                x_data = np.concatenate(x_data)
            
            self.x_max.set(np.ceil(max(x_data) / self.x_tick.get()) * self.x_tick.get())
        except Exception as e:
            print(f"Error in auto_scale_x_max: {e}")
    
    def auto_scale_y_min(self):
        if not self.filenames and not self.is_table_mode:
            return
        
        try:
            if self.is_table_mode:
                data_start = self.detect_data_start(self.table_file)
                all_y_data = []
                for x_col, y_col in self.table_columns:
                    y_data = np.loadtxt(
                        self.table_file, unpack=True, skiprows=data_start, usecols=y_col, delimiter=self.table_delimiter
                    )
                    all_y_data.extend(y_data if y_data.ndim > 0 else [y_data])
                y_data = np.array(all_y_data)
            else:
                y_data = [
                    np.loadtxt(file, unpack=True, skiprows=self.detect_data_start(file), usecols=1, delimiter=self.get_delimiter(file))
                    for file in self.filenames
                ]
                y_data = np.concatenate(y_data)
            
            self.y_min.set(np.floor(min(y_data) / self.y_tick.get()) * self.y_tick.get())
        except Exception as e:
            print(f"Error in auto_scale_y_min: {e}")
    
    def auto_scale_y_max(self):
        if not self.filenames and not self.is_table_mode:
            return
        
        try:
            if self.is_table_mode:
                data_start = self.detect_data_start(self.table_file)
                all_y_data = []
                for x_col, y_col in self.table_columns:
                    y_data = np.loadtxt(
                        self.table_file, unpack=True, skiprows=data_start, usecols=y_col, delimiter=self.table_delimiter
                    )
                    all_y_data.extend(y_data if y_data.ndim > 0 else [y_data])
                y_data = np.array(all_y_data)
            else:
                y_data = [
                    np.loadtxt(file, unpack=True, skiprows=self.detect_data_start(file), usecols=1, delimiter=self.get_delimiter(file))
                    for file in self.filenames
                ]
                y_data = np.concatenate(y_data)
            
            self.y_max.set(np.ceil(max(y_data) / self.y_tick.get()) * self.y_tick.get())
        except Exception as e:
            print(f"Error in auto_scale_y_max: {e}")
    
    def select_table(self):
        """Select a table file and configure columns for plotting."""
        table_file = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not table_file:
            return
        
        try:
            # Detect data start
            data_start = self.detect_data_start(table_file)
            delimiter = self.get_delimiter(table_file)
            self.table_delimiter = delimiter
            
            # Read header if available
            with open(table_file, 'r') as f:
                lines = [f.readline().strip() for _ in range(data_start)]
            
            header_line = lines[-1] if lines else ""
            if header_line.startswith('#'):
                header_line = header_line[1:].strip()
            
            # Try to parse headers, otherwise generate generic names
            header_clean = header_line.replace(',', '').replace('\t', '').replace(' ', '')
            if header_line and not all(c.isdigit() or c in '.-+e' for c in header_clean):
                split_char = delimiter if delimiter else '\t'
                self.column_headers = [h.strip() if h.strip() else f"Column {idx+1}" for idx, h in enumerate(header_line.split(split_char))]
            else:
                # If no valid header, read a line of data to count columns
                data = np.loadtxt(table_file, unpack=True, skiprows=data_start, max_rows=1, delimiter=delimiter)
                if data.ndim == 0:
                    num_cols = 1
                else:
                    num_cols = len(data) if data.ndim > 0 else 1
                self.column_headers = [f"Column {i+1}" for i in range(num_cols)]
            
            # Set table mode
            self.is_table_mode = True
            self.table_file = table_file
            
            if self.auto_plot_1st_col.get():
                num_cols = len(self.column_headers)
                if num_cols > 1:
                    self.table_columns = [(0, i) for i in range(1, num_cols)]
                    self._apply_table_columns_and_update_ui()
                else:
                    print("Table has only one column.")
            else:
                # Open column selection dialog
                self.open_column_selection_dialog()
            
        except Exception as e:
            print(f"Error reading table file: {e}")

    def open_column_selection_dialog(self):
        """Open a dialog to select column pairs for plotting."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Columns to Plot")
        dialog.geometry("500x400")
        
        tk.Label(dialog, text="Select column pairs (X, Y) to plot:", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Create a frame with checkboxes for each possible column pair
        frame = tk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        
        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        
        column_selection = {}
        num_cols = len(self.column_headers)
        
        # Create checkboxes for all possible column pair combinations
        for i in range(num_cols):
            for j in range(i + 1, num_cols):
                var = tk.BooleanVar(value=False)
                col_pair_name = f"{self.column_headers[i]} (X) vs {self.column_headers[j]} (Y)"
                tk.Checkbutton(inner_frame, text=col_pair_name, variable=var).pack(anchor=tk.W)
                column_selection[(i, j)] = var
        
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        def apply_selection():
            self.table_columns = [(i, j) for (i, j), var in column_selection.items() if var.get()]
            self._apply_table_columns_and_update_ui()
            dialog.destroy()
        
        tk.Button(dialog, text="Apply", command=apply_selection, bg="green", fg="white").pack(pady=10)

    def _apply_table_columns_and_update_ui(self):
        if not self.table_columns:
            print("No columns selected.")
            return
        
        # Create line properties for each selected column pair
        self.line_properties.clear()
        for widget in self.line_properties_frame.winfo_children():
            widget.destroy()
        
        for idx, (x_col, y_col) in enumerate(self.table_columns):
            self.add_line_property_set(
                filename=f"{self.column_headers[x_col]} vs {self.column_headers[y_col]}"
            )
        
        # Update file label
        self.file_label.config(
            text=f"Selected Table: {os.path.basename(self.table_file)} ({len(self.table_columns)} plots)"
        )
        
        # Set default file name
        default_file_name = os.path.splitext(os.path.basename(self.table_file))[0]
        self.file_name.set(default_file_name)

    def select_files(self):
        # Reset table mode if switching to file mode
        self.is_table_mode = False
        self.table_file = None
        self.table_columns = []
        
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
        """Clear the selected files/table and reset related UI elements."""
        self.filenames = []
        self.table_file = None
        self.table_columns = []
        self.column_headers = []
        self.is_table_mode = False
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

    def plot(self, delimiter="\t"):
        if not self.filenames and not self.is_table_mode:
            print("No files or table selected.")
            return
        
        plt.figure(figsize=(10, 6))
        
        if self.is_table_mode:
            # Plot data from table file
            data_start = self.detect_data_start(self.table_file)
            
            for plot_idx, (x_col, y_col) in enumerate(self.table_columns):
                try:
                    data = np.loadtxt(
                        self.table_file, unpack=True, skiprows=data_start, 
                        usecols=(x_col, y_col), delimiter=self.table_delimiter
                    )
                    
                    if data.ndim < 2 or data.shape[0] < 2:
                        print(f"Skipping columns {x_col}, {y_col}: insufficient data.")
                        continue
                    
                    data_x, data_y = data[0], data[1]
                    
                    # Convert wavelength to energy in eV if checkbox is selected
                    if self.use_nm2eV.get():
                        data_x = self.nm2eV(data_x)
                        self.x_label.set("Energy (eV)")
                    
                    # Normalize data by point if checkbox is selected
                    if self.normalize_data.get():
                        normalize_point = self.line_properties[plot_idx]['normalize_point'].get()
                        closest_index = (np.abs(data_x - normalize_point)).argmin()
                        data_y = data_y / data_y[closest_index]
                    
                    # Normalize data by maximum if checkbox is selected
                    if self.normalize_max.get():
                        data_y = data_y / np.max(data_y)
                    
                    # Get line properties
                    line_props = self.line_properties[plot_idx]
                    
                    if line_props['plot_as_points'].get():
                        plt.scatter(data_x, data_y, 
                                    color=line_props['line_color'].get(), 
                                    s=line_props['point_size'].get(), 
                                    label=line_props['legend_label'].get())
                    else:
                        plt.plot(data_x, data_y, 
                                 color=line_props['line_color'].get(), 
                                 linewidth=line_props['line_thickness'].get(), 
                                 linestyle=line_props['style_map'][line_props['line_style'].get()],
                                 label=line_props['legend_label'].get())
                    
                    # Perform fitting if enabled
                    if line_props['fit_enabled'].get():
                        fit_type = line_props['fit_type'].get()
                        if fit_type == "Linear":
                            coeffs = np.polyfit(data_x, data_y, 1)
                            fit_func = np.poly1d(coeffs)
                            line_props['fit_equation'].set(f"Fit Equation: y = {coeffs[0]:.4f}x + {coeffs[1]:.4f}")
                        elif fit_type.startswith("Polynomial"):
                            degree = int(fit_type.split("^")[1][0])
                            coeffs = np.polyfit(data_x, data_y, degree)
                            fit_func = np.poly1d(coeffs)
                            equation_terms = [f"{coeff:.4f}x^{i}" for i, coeff in enumerate(reversed(coeffs))]
                            line_props['fit_equation'].set(f"Fit Equation: y = {' + '.join(equation_terms)}")
                        elif fit_type == "Exponential":
                            valid_indices = data_y > 0
                            if not np.any(valid_indices):
                                print("Exponential fit failed: No valid data points.")
                                continue
                            
                            filtered_x = data_x[valid_indices]
                            filtered_y = data_y[valid_indices]
                            log_y = np.log(filtered_y)
                            coeffs = np.polyfit(filtered_x, log_y, 1)
                            fit_func = lambda x: np.exp(coeffs[1]) * np.exp(coeffs[0] * x)
                            line_props['fit_equation'].set(f"Fit Equation: y = {np.exp(coeffs[1]):.4f}e^({coeffs[0]:.4f}x)")
                        
                        fit_x = np.linspace(self.x_min.get(), self.x_max.get(), 500)
                        fit_y = fit_func(fit_x)
                        plt.plot(fit_x, fit_y, 
                                 linestyle=self.fit_line_styles[line_props['fit_line_style'].get()], 
                                 color=line_props['fit_line_color'].get(), 
                                 linewidth=line_props['fit_line_thickness'].get(), 
                                 label=line_props['fit_legend_label'].get())
                    
                except Exception as e:
                    print(f"Error plotting columns {x_col}, {y_col}: {e}")
        
        else:
            # Plot data from multiple files (original behavior)
            # Plot each selected file with corresponding line properties
            for i, filename in enumerate(self.filenames):
                data_start = self.detect_data_start(filename)
                file_delimiter = self.get_delimiter(filename)
                data = np.loadtxt(filename, unpack=True, skiprows=data_start, delimiter=file_delimiter)
                if data.ndim < 2 or data.shape[0] < 2:
                    print(f"Skipping file {filename}: insufficient data.")
                    continue
                data_x, data_y = data[0], data[1]

                # Convert wavelength to energy in eV if checkbox is selected
                if self.use_nm2eV.get():
                    data_x = self.nm2eV(data_x)
                    self.x_label.set("Energy (eV)")
                
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
                if line_props['fit_enabled'].get():
                    fit_type = line_props['fit_type'].get()
                    if fit_type == "Linear":
                        coeffs = np.polyfit(data_x, data_y, 1)
                        fit_func = np.poly1d(coeffs)
                        line_props['fit_equation'].set(f"Fit Equation: y = {coeffs[0]:.4f}x + {coeffs[1]:.4f}")
                    elif fit_type.startswith("Polynomial"):
                        degree = int(fit_type.split("^")[1][0])  # Extract the degree from the dropdown text
                        coeffs = np.polyfit(data_x, data_y, degree)
                        fit_func = np.poly1d(coeffs)
                        equation_terms = [f"{coeff:.4f}x^{i}" for i, coeff in enumerate(reversed(coeffs))]
                        line_props['fit_equation'].set(f"Fit Equation: y = {' + '.join(equation_terms)}")
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
                        line_props['fit_equation'].set(f"Fit Equation: y = {np.exp(coeffs[1]):.4f}e^({coeffs[0]:.4f}x)")

                    # Plot the fit function with user-defined style, color, thickness, and legend label
                    fit_x = np.linspace(self.x_min.get(), self.x_max.get(), 500)
                    fit_y = fit_func(fit_x)
                    plt.plot(fit_x, fit_y, 
                             linestyle=self.fit_line_styles[line_props['fit_line_style'].get()], 
                             color=line_props['fit_line_color'].get(), 
                             linewidth=line_props['fit_line_thickness'].get(), 
                             label=line_props['fit_legend_label'].get())

        font = self.selected_font.get()
        legend_font = {'family': font, 'weight': 'normal', 'size': self.legend_fontsize.get()}
        label_font = {'family': font, 'size': self.label_fontsize.get()}
        tick_font = {'family': font, 'size': self.tick_fontsize.get()}
        
        # Set labels with the selected fonts
        plt.xlabel(self.x_label.get(), fontdict=label_font)
        plt.ylabel(self.y_label.get(), fontdict=label_font)
        
        # Set tick intervals and font
        x_ticks = np.arange(
            np.floor(self.x_min.get() / self.x_tick.get()) * self.x_tick.get(),
            np.ceil(self.x_max.get() / self.x_tick.get()) * self.x_tick.get() + self.x_tick.get(),
            self.x_tick.get()
        )
        y_ticks = np.arange(
            np.floor(self.y_min.get() / self.y_tick.get()) * self.y_tick.get(),
            np.ceil(self.y_max.get() / self.y_tick.get()) * self.y_tick.get() + self.y_tick.get(),
            self.y_tick.get()
        )

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
