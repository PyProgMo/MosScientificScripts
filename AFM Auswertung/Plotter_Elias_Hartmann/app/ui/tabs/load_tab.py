import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class LoadTab(ttk.Frame):
    def __init__(self, master, data_model, data_1d_model, on_loaded_callback, on_1d_loaded_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.data_model = data_model
        self.data_1d_model = data_1d_model
        self.on_loaded_callback = on_loaded_callback
        self.on_1d_loaded_callback = on_1d_loaded_callback
        
        self._init_ui()
        
    def _init_ui(self):
        # File paths
        self.path_var = tk.StringVar()
        self.path_1d_var = tk.StringVar()
        
        # 2D Matrix Load Section
        control_frame = ttk.LabelFrame(self, text="2D Matrix File Selection")
        control_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        btn_browse = ttk.Button(control_frame, text="Browse 2D Data", command=self._browse_file)
        btn_browse.grid(row=0, column=0, padx=5, pady=5)
        
        lbl_path = ttk.Label(control_frame, textvariable=self.path_var)
        lbl_path.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 1D Cut Load Section
        control_1d_frame = ttk.LabelFrame(self, text="1D Cut File Selection")
        control_1d_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        btn_1d_browse = ttk.Button(control_1d_frame, text="Browse 1D Data", command=self._browse_1d_file)
        btn_1d_browse.grid(row=0, column=0, padx=5, pady=5)
        
        lbl_1d_path = ttk.Label(control_1d_frame, textvariable=self.path_1d_var)
        lbl_1d_path.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Output Info Text area
        info_frame = ttk.LabelFrame(self, text="Parsing Info")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_info = tk.Text(info_frame, wrap=tk.WORD, height=15)
        self.text_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _browse_file(self):
        filepath = filedialog.askopenfilename(
            title="Select XYZ format file",
            filetypes=(("Text files", "*.txt;*.dat;*.xyz;*.csv"), ("All files", "*.*"))
        )
        if filepath:
            self.path_var.set(filepath)
            self._load_file(filepath)
            
    def _load_file(self, path):
        try:
            self.text_info.delete("1.0", tk.END)
            self.data_model.load_from_file(path)
            
            info = f"Loaded file successfully: {os.path.basename(path)}\n\n"
            info += "-- Metadata --\n"
            info += self.data_model.get_metadata_str()
            info += "\n\n-- Data Metrics --\n"
            z = self.data_model.matrix_z
            info += f"Matrix Grid Shape: {z.shape}\n"
            info += f"Min Z: {float(z.min()):.4f}, Max Z: {float(z.max()):.4f}\n"
            
            self.text_info.insert(tk.END, info)
            
            # trigger root update
            self.on_loaded_callback()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load the file:\n{str(e)}")

    def _browse_1d_file(self):
        filepath = filedialog.askopenfilename(
            title="Select 1D Cut file",
            filetypes=(("Text files", "*.txt;*.dat;*.xyz;*.csv"), ("All files", "*.*"))
        )
        if filepath:
            self.path_1d_var.set(filepath)
            self._load_1d_file(filepath)
            
    def _load_1d_file(self, path):
        try:
            self.text_info.delete("1.0", tk.END)
            self.data_1d_model.load_from_file(path)
            
            info = f"Loaded 1D file successfully: {os.path.basename(path)}\n\n"
            info += "-- Metadata --\n"
            info += self.data_1d_model.get_metadata_str()
            info += "\n\n-- Data Metrics --\n"
            df = self.data_1d_model.df
            info += f"Total Data Points: {len(df)}\n"
            info += f"Min Height: {df['Height'].min():.4e}, Max Height: {df['Height'].max():.4e}\n"
            
            self.text_info.insert(tk.END, info)
            
            # trigger root update
            self.on_1d_loaded_callback()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load 1D file:\n{str(e)}")
