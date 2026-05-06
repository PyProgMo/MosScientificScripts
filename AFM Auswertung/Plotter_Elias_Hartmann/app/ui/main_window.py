import tkinter as tk
from tkinter import ttk
from app.ui.tabs.load_tab import LoadTab
from app.ui.tabs.plot_tab import PlotTab
from app.ui.tabs.plot_1d_tab import Plot1DTab
from app.models.afm_data import AFMData
from app.models.afm_1d_data import AFM1DData

class Application(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        
        self.data_model = AFMData()
        self.data_1d_model = AFM1DData()
        
        self._init_ui()
        
    def _init_ui(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.load_tab = LoadTab(self.notebook, self.data_model, self.data_1d_model, self.on_data_loaded, self.on_1d_data_loaded)
        self.plot_tab = PlotTab(self.notebook, self.data_model)
        self.plot_1d_tab = Plot1DTab(self.notebook, self.data_1d_model)
        
        self.notebook.add(self.load_tab, text='Load Data')
        self.notebook.add(self.plot_tab, text='2D Plot Configuration')
        self.notebook.add(self.plot_1d_tab, text='1D Cut Plot')

    def on_data_loaded(self):
        # Notify the 2D plot tab to refresh UI logic or parameters
        self.plot_tab.on_data_ready()
        
    def on_1d_data_loaded(self):
        # Notify the 1D plot tab to refresh UI logic or parameters
        self.plot_1d_tab.on_data_ready()
