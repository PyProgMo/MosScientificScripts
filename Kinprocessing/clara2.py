import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import matplotlib, os, sys, re
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.ticker import MaxNLocator
# add code to process the selected files or directory
import claralib3 as cl
import importlib

def select_directory(root, close=True):
    """
    Opens a directory selection dialog and returns the selected path
    
    Args:
        root: Tkinter root window
        close: Close the root window after selection (default: True)
        
    Returns:
        str: Selected directory path or empty string if cancelled
    """
    directory = filedialog.askdirectory(
        parent=root,
        initialdir=".",
        title="Select Directory"
    )
    if close:
        root.destroy()
    return directory

def select_files(root, close=True):
    """
    Opens a file selection dialog and returns the selected paths
    
    Args:
        root: Tkinter root window
        close: Close the root window after selection (default: True)
        
    Returns:
        list: Selected file paths or empty list if cancelled
    """
    files = filedialog.askopenfilenames(
        parent=root,
        initialdir=".",
        title="Select Files",
        filetypes=(("All files", "*.*"),)
    )
    if close:
        root.destroy()
    return files

def getdir():
    root = tk.Tk()
    return select_directory(root, close=True)

def getfiles():
    root = tk.Tk()
    return select_files(root, close=True)


# second notebook
# load the files here - adjust d and f to the desired directory and file
#d = getdir() # open dir # run this cell to open a dir and save it on d
#print(d)
d = "C:/Users/volib/Desktop/Evaluation/data/2024/qdot_100fach/Laser_in_zpos_test".replace("/", "\\")
print('d = ', d)
#f = getfiles() # open files # run this cell to open files and save them to the array f
# example: f = C:\Users\volib\Desktop\Evaluation\data\2024\qdot_100fach\Laser_in_zpos
f = "C:/Users/volib/Desktop/Evaluation/data/2024/qdot_100fach/Laser_in_zpos_test/145_0.asc".replace("/", "\\")
if len(f) == 1:
    f = f[0]
    print(f)
print('f = ', f)

# create tkinter window
root = tk.Tk()
root.geometry('{}x{}'.format(800, 600))
frame = ttk.Frame(root)
# create nodeframes
nodeframes = {}
# create notebook with title "Clara1"
notebook = ttk.Notebook(frame)
notebook.pack(fill="both", expand=True)
nodeframes["Clara1"] = ttk.Frame(notebook)
notebook.add(nodeframes["Clara1"], text="Clara1")
# pack the clara1 frame
frame.pack(fill="both", expand=True)

dx = dx = 0.0568*2#0.0568 
dy = 0.0568*2#0.0568


# create clara processing frame
imp = cl.imageprocessor(nodeframes["Clara1"], f, cl.loadclaraimage, None, dx, dy)

# add new notebook tab for the clara kinetics processing
nodeframes["Clara Kinetics"] = ttk.Frame(notebook)
notebook.add(nodeframes["Clara Kinetics"], text="Clara Kinetics")
kin = cl.clarakinetics(nodeframes["Clara Kinetics"], os.path.dirname(f), dx, dy)

# select the the "Clara Kinetics" tab
notebook.select(nodeframes["Clara Kinetics"]) 

def on_closing():
    try:
        
        kin.close()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)


# run the tkinter main loop - required to plot images and interact with the GUI
root.mainloop()