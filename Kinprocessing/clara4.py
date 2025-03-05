import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import numpy as np
import matplotlib, os, sys, re
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.ticker import MaxNLocator
# add code to process the selected files or directory
import claralib4 as cl

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
d = "C:/Users/volib/Desktop/Evaluation/data/2024/Perovskite/Caroline_Kloth/clarakin_t1/tm1/image/N1Uncaped_40step_15min/kinascfiles".replace("/", "\\")
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

class ClaraApp:
    def __init__(self, root):
        self.root = root
        self.loadframe = ttk.Frame(root)

        # create nodeframes
        self.nodeframes = {}
        # create notebook with title "Clara1"
        self.notebook = ttk.Notebook(self.loadframe)
        self.notebook.pack(fill="both", expand=True)
        self.nodeframes["Clara1"] = ttk.Frame(self.notebook)
        self.notebook.add(self.nodeframes["Clara1"], text="Clara1")
        # pack the clara1 frame
        self.loadframe.pack(fill="both", expand=True)

        self.dx = 0.0568*2#0.0568 
        self.dy = 0.0568*2#0.0568

        # create clara processing frame
        self.imp = cl.imageprocessor(self.nodeframes["Clara1"], cl.loadclaraimage, None, self.dx, self.dy, f)

        # add new notebook tab for the clara kinetics processing
        self.nodeframes["Clara Kinetics"] = ttk.Frame(self.notebook)
        # make the clara kinetics processing frame expandible and fit to windowsize
        self.nodeframes["Clara Kinetics"].pack(fill="both", expand=True)
        # add the clara kinetics processing frame to the notebook
        self.notebook.add(self.nodeframes["Clara Kinetics"], text="Clara Kinetics")
        kin = cl.clarakinetics(self.nodeframes["Clara Kinetics"], d, self.dx, self.dy)

        # init the clara kinetics processing
        #self.roisetup()

        # select the the "Clara Kinetics" tab
        self.notebook.select(self.nodeframes["Clara Kinetics"]) 
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # run the tkinter main loop - required to plot images and interact with the GUI
        self.root.mainloop()
    
    def roisetup(self):
        # roi frame below the clara kinetics processing on the "Clara Kinetics" tab
        self.roiframe = ttk.Frame(self.nodeframes["Clara Kinetics"], border=2, relief="groove")
        self.roiframe.grid(row=1, column=0, sticky="nsew")
        # create a label for the roi frame 
        self.roilabel = ttk.Label(self.roiframe, text="ROI")
        self.roilabel.grid(row=1, column=1, sticky="nsew")
        # create a button to select the roi
        
        self.roihandler = cl.Roihandler()

    def on_closing(self):
        try: 
            self.kin.close()
        except:
            pass
        self.root.destroy()

Clara = ClaraApp(root)