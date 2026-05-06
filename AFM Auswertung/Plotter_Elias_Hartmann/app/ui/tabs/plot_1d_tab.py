import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class Plot1DTab(ttk.Frame):
    def __init__(self, master, data_model, **kwargs):
        super().__init__(master, **kwargs)
        self.data_model = data_model
        
        # Variables for configuration
        self.title_var = tk.StringVar(value="1D Cross-Section")
        self.xlabel_var = tk.StringVar(value="Length")
        self.ylabel_var = tk.StringVar(value="Height")
        self.color_var = tk.StringVar(value="blue")
        self.linestyle_var = tk.StringVar(value="-")
        self.fontsize_var = tk.IntVar(value=12)
        
        self._init_ui()
        
    def _init_ui(self):
        # Layout splitting: left controls, right canvas
        self.ctrl_frame = ttk.LabelFrame(self, text="1D Plot Customization", width=300)
        self.ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._build_controls()
        self._build_plot_area()
        
    def _build_controls(self):
        # 1. Title
        ttk.Label(self.ctrl_frame, text="Plot Title:").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Entry(self.ctrl_frame, textvariable=self.title_var).pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # 2. Labels
        ttk.Label(self.ctrl_frame, text="X Label (Length):").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Entry(self.ctrl_frame, textvariable=self.xlabel_var).pack(fill=tk.X, padx=5, pady=(0, 10))
        
        ttk.Label(self.ctrl_frame, text="Y Label (Height):").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Entry(self.ctrl_frame, textvariable=self.ylabel_var).pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # 3. Line Color
        ttk.Label(self.ctrl_frame, text="Line Color:").pack(anchor=tk.W, padx=5, pady=2)
        color_combo = ttk.Combobox(self.ctrl_frame, textvariable=self.color_var, state="readonly")
        color_combo['values'] = ('blue', 'red', 'green', 'black', 'orange', 'purple')
        color_combo.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # 4. Line Style
        ttk.Label(self.ctrl_frame, text="Line Style:").pack(anchor=tk.W, padx=5, pady=2)
        ls_combo = ttk.Combobox(self.ctrl_frame, textvariable=self.linestyle_var, state="readonly")
        ls_combo['values'] = ('-', '--', '-.', ':')
        ls_combo.pack(fill=tk.X, padx=5, pady=(0, 10))
        
        # 5. Font Size
        ttk.Label(self.ctrl_frame, text="Font Size:").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Spinbox(self.ctrl_frame, from_=8, to=36, textvariable=self.fontsize_var).pack(fill=tk.X, padx=5, pady=(0, 20))
        
        # 6. Button
        ttk.Button(self.ctrl_frame, text="Render Plot", command=self.update_plot).pack(fill=tk.X, padx=5, pady=5)
        
    def _build_plot_area(self):
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.canvas_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def on_data_ready(self):
        # Auto-update plot parameters from metadata units if available
        meta = self.data_model.metadata
        if 'X Unit' in meta:
            if meta['X Unit'] == 'MicroMeter':
                self.xlabel_var.set(r"Length ($\mu$m)")
            else:
                self.xlabel_var.set(f"Length ({meta['X Unit']})")
        if 'Y Unit' in meta:
            self.ylabel_var.set(f"Height ({meta['Y Unit']})")
            
        self.update_plot()
        
    def update_plot(self):
        if self.data_model.df is None:
            messagebox.showinfo("No Data", "Please load a 1D file first.")
            return
            
        # Update plotting styles based on config
        fs = self.fontsize_var.get()
        title = self.title_var.get()
        xlbl = self.xlabel_var.get()
        ylbl = self.ylabel_var.get()
        c = self.color_var.get()
        ls = self.linestyle_var.get()
        
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        
        # Render the line plot
        x_data = self.data_model.df['Length']
        y_data = self.data_model.df['Height']
        
        self.ax.plot(x_data, y_data, color=c, linestyle=ls)
        
        self.ax.set_title(title, fontsize=fs)
        self.ax.set_xlabel(xlbl, fontsize=fs)
        self.ax.set_ylabel(ylbl, fontsize=fs)
        self.ax.tick_params(labelsize=fs*0.8) 
        self.ax.grid(True, linestyle='--', alpha=0.6)
        
        self.figure.tight_layout()
        self.canvas.draw()