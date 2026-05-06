import tkinter as tk
import matplotlib
from app.ui.main_window import Application

# Set global Matplotlib save resolution to 600 DPI
matplotlib.rcParams['savefig.dpi'] = 600

def main():
    root = tk.Tk()
    root.title("AFM Data Visualizer")
    root.geometry("1000x800")
    
    app = Application(master=root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
