import os
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.widgets import CheckButtons, Button
from tkinter import Tk, filedialog
import matplotlib.colors as mcolors

SpectDataFloats = ['Slit Width (µm)', 'Central Wavelength (nm)',
                   'Cooling Temperature (°C)',
                   'Exposure Time (s)',
                   #'Wavelength First Pixel (nm)', # is obtained from WL
                   #'Wavelength Last Pixel (nm)',
                   'Delta Wavelength (nm)',
                   'x-position',
                   'y-position',
                   'z-position',
                   'Short Wavelength (nm)',
                   'Long Wavelength (nm)',
                   'magnification']

class SpectrumData:
    def __init__(self, filename, WL, BG, loadeachbg = False, linearbg=False, powernW=0, tint=2):
        self.loadeachbg = loadeachbg
        self.linearbg = linearbg
        self.WL = WL
        if self.loadeachbg == True:
            self.BG = []
        else:
            self.BG = BG
        self.filename = filename
        self.readinkeys = ['BG', 'PL'] # WL is defined in XYMap
        self.openFstate = [] # open floats state from metadata
        self.openDstate = [] # open Data from spectrometer
        self.dataokay = False    # set True if everything openend properly
        self.data = {}
        self.roistore = {}
        self.PL = []
        self.powernW = powernW
        self.tint = tint
        self._read_file()

    def _read_file(self):
        with open(self.filename, 'r') as file:
            lines = file.readlines()

        # Process lines to store variables
        startreaddata = False
        for line in lines:
            if ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                if key in SpectDataFloats:
                    try:
                        self.data[key] = float(value)
                    except:
                        self.data[key] = value
                        self.openFstate.append(False)
                else:
                    self.data[key] = value
            elif '\t' in line:  # Data lines with tabs
                parts = line.split()
                if startreaddata == False:
                    count = 0
                    # start reading if at least two keys in the line
                    for i in parts:
                        if i in self.readinkeys:
                            count += 1
                    if count > 1:
                        startreaddata = True
                elif startreaddata == True:
                    try:
                        if self.loadeachbg == True:
                            self.BG.append(int(parts[1]))
                        #self.WL.append(float(parts[0]))  WL is only read once by XYMap since each SpectrumData has the same WL-axis
                        self.PL.append(int(parts[2]))
                    except Exception as e:
                        messagebox.showerror("Error", str(e))
        if self.loadeachbg == True and self.linearbg == True:
            av = np.mean(self.BG)
            for i in range(len(self.BG)):
                self.BG[i] = av

        try:
            self.PLB = np.subtract(self.PL, self.BG).tolist() # add PLB = PL-BG
        except Exception as e:
            messagebox.showerror("Error", str(e))
        # write openstate list
        for i in SpectDataFloats:
            if i not in list(self.data.keys()):
                self.openFstate.append(False)
        if len(self.WL) == 0:
            self.openDstate.append(None)
        if len(self.BG) == 0:
            self.openDstate.append(None)
        if len(self.PL) == 0:
            self.openDstate.append(None)
        self.setOK()

    def setOK(self):
        if False in self.openFstate:
            pass
        elif None in self.openDstate:
            pass
        else:
            self.dataokay = True

    # return a specific attribute of this class
    def get_attribute(self, attr_name:str):
        try:
            return getattr(self, attr_name)
        except AttributeError as e:
            print("Attribute {} not found in class SpectrumData.".format(attr_name))

class InteractivePlot:
    def __init__(self, x, normspec, activespecs, specabs, labels=None):
        """
        Initialize the interactive plot.
        Args:
            x (list or array): The x values shared by all datasets.
            normspec (list of lists or arrays): List of y datasets.
            activespecs: list of bools to store the visibility state of the lines
            y_array not normalized
            labels (list of str): Labels for the datasets. If None, auto-generate labels as ['y1', 'y2', ...].
        """
        self.fig, self.ax = plt.subplots()
        self.activespecs = activespecs
        self.specabs = specabs
        self.normspecs = normspec
        self.WL = x
        
        # Dynamically adjust layout to leave space for checkboxes and buttons
        max_labels = len(self.normspecs)
        checkbox_height = max(0.029 * max_labels, 0.3)  # Minimum height of 0.3, grows with more labels
        plt.subplots_adjust(left=0.28, bottom=0.1, top=0.80)
        
        # Use labels if provided, otherwise auto-generate labels
        self.labels = labels if labels else [f"y{i+1}" for i in range(len(self.normspecs))]
        
        # Initialize data and plot lines
        self.lines = self.get_sample_data(self.WL, self.normspecs)
        self.check = None
        self.set_line_colors2()
        self.setup_plot(checkbox_height)
    
    def get_sample_data(self, x, y_arrays, plotlabel='Counts normalized'):
        """
        Generate plot lines from x and multiple y datasets.
        Args:
            x (list or array): The x values shared by all datasets.
            y_arrays (list of lists or arrays): List of y datasets.
        Returns:
            dict: A dictionary mapping labels to their corresponding Line2D objects.
        """
        lines = {}
        for label, y in zip(self.labels, y_arrays):
            lines[label] = self.ax.plot(x, y, label=label, lw=0.5)[0]
            # adjust the color of the line
            lines[label].set_color('black')
            # set the fontsize of the axis
            self.ax.fontsize = 12
            # name y-axis counts per second
            self.ax.set_ylabel(plotlabel)
            # name x-axis power in nW
            self.ax.set_xlabel('Wavelength (nm)')
            # set y-axis limits to np.amax and np.amin of y_arrays
            self.ax.set_ylim([np.amin(y_arrays), np.amax(y_arrays)])
            if self.activespecs[self.labels.index(label)] == False: # set line invisible if not active
                lines[label].set_visible(False)
        return lines

    def set_line_colors1(self, start_color='blue', end_color='yellow'):
        """
        Adjust the colors of the lines in self.lines to form a gradient between start_color and end_color.

        Args:
            start_color (str): The starting color of the gradient (e.g., 'blue').
            end_color (str): The ending color of the gradient (e.g., 'yellow').
        """
        # Convert start and end colors to RGB using matplotlib's color converter
        start_rgb = np.array(mcolors.to_rgb(start_color))
        end_rgb = np.array(mcolors.to_rgb(end_color))

        # Get the total number of lines
        num_lines = len(self.lines)

        # Generate the color gradient
        for i, (label, line) in enumerate(self.lines.items()):
            # Calculate the interpolation factor
            t = i / (num_lines - 1) if num_lines > 1 else 0
            # Interpolate between start_rgb and end_rgb
            color = start_rgb * (1 - t) + end_rgb * t
            # Set the line color
            line.set_color(color)
    
    def set_line_colors2(self, start_color='green', end_color='red'):
        # possible colors are: 
        # 'blue', 'green', 'red', 'yellow', 'orange', 'purple', 'pink', 'brown', 'gray', 'cyan', 'black', 'white', 'lightgray', 'darkgray'
        # 'lightblue', 'lightgreen', 'lightred', 'lightyellow', 'lightorange', 'lightpurple', 'lightpink', 'lightbrown', 'lightgray', 'lightcyan', ... 
        # very good working colors: ('blue', 'yellow')('red', 'green')('purple', 'orange')('teal', 'pink')('navy', 'gold') ('lightblue', 'darkblue')
        """
        Adjust the colors of the lines in self.lines to form a gradient between start_color and end_color.

        Args:
            start_color (str): The starting color of the gradient (e.g., 'blue').
            end_color (str): The ending color of the gradient (e.g., 'yellow').
        """
        # Convert start and end colors to RGB using matplotlib's color converter
        start_rgb = np.array(mcolors.to_rgb(start_color))
        end_rgb = np.array(mcolors.to_rgb(end_color))

        # Get the total number of lines
        num_lines = len(self.lines)

        # Generate the color gradient
        for i, (label, line) in enumerate(self.lines.items()):
            # Calculate the interpolation factor with a gamma adjustment for better visibility
            gamma = 1.5  # Adjust gamma as needed (gamma > 1 for darker emphasis, gamma < 1 for lighter emphasis)
            t = (i / (num_lines - 1) if num_lines > 1 else 0) ** gamma
            # Interpolate between start_rgb and end_rgb
            color = start_rgb * (1 - t) + end_rgb * t
            # Set the line color
            line.set_color(color)   
    
    def setup_plot(self, checkbox_height):
        """
        Set up the plot, including checkboxes, buttons, and legend.
        Args:
            checkbox_height (float): Dynamic height of the checkbox area based on the number of datasets.
        """
        # Adjust checkbox area dynamically
        checkbox_start_y = 0.5 - checkbox_height / 1.8
        rax = plt.axes([0.05, checkbox_start_y, 0.15, checkbox_height])  # [left, bottom, width, height]
        # set font size of labels
        plt.rcParams.update({'font.size': 10})
        self.check = CheckButtons(rax, labels=self.labels, actives=[True] * len(self.labels))
        
        # Add "Plot All" button
        button_ax_all = plt.axes([0.05, checkbox_start_y + checkbox_height + 0.05, 0.15, 0.05])  # "Plot All" button
        self.plot_all_button = Button(button_ax_all, 'toggle lines')
        
        # Add "Save Plot" button
        button_ax_save = plt.axes([0.21, checkbox_start_y + checkbox_height + 0.05, 0.15, 0.05])  # "Save Plot" button
        self.save_plot_button = Button(button_ax_save, 'Save Plot')

        # Add "Toggle Colors" button
        print(checkbox_start_y, checkbox_height, checkbox_start_y + checkbox_height)
        button_ax_togglelinecounts = plt.axes([0.05, checkbox_start_y + checkbox_height, 0.15, 0.05])  # "Toggle Colors" button
        self.toggle_linecounts_button = Button(button_ax_togglelinecounts, 'toggle Counts')
        
        # Connect the callback functions
        self.check.on_clicked(self.toggle_visibility)
        self.plot_all_button.on_clicked(self.plot_all)
        self.save_plot_button.on_clicked(self.save_plot)
        self.toggle_linecounts_button.on_clicked(self.toggle_linecounts)

        print(self.activespecs)
        
        # Add legend
        self.ax.legend(
            loc="upper left",               # Position relative to the bounding box
            bbox_to_anchor=(1.0, 1.2),        # (x, y) coordinates of the anchor point
            borderaxespad=0.5,              # Padding between the plot and legend)
            fontsize= 9                    # Font size of the legend   
        )
        plt.draw()

    def clear_sample_data(self):
        """
        Remove all lines currently stored in self.lines from the plot.
        """
        if hasattr(self, 'lines') and self.lines:
            # Iterate over all Line2D objects in self.lines
            for label, line in self.lines.items():
                # Remove the line from the axes
                line.remove()
            
            # Clear the lines dictionary
            self.lines.clear()
            
            # Optionally redraw the canvas to reflect changes
            self.ax.figure.canvas.draw()
        else:
            print("No lines to remove or self.lines is not defined.")
    
    def toggle_linecounts(self, event):
        # toggle between normalized counts and raw counts
        if self.ax.get_ylabel() == 'Counts normalized':
            self.clear_sample_data()
            self.lines = self.get_sample_data(self.WL, self.specabs, plotlabel='Counts per second')
        elif self.ax.get_ylabel() == 'Counts per second':
            self.clear_sample_data()
            self.lines = self.get_sample_data(self.WL, self.normspecs, plotlabel='Counts normalized')
        self.set_line_colors2()
        plt.draw()
    
    def toggle_visibility(self, label):
        """
        Callback function to toggle visibility of individual lines.
        """
        line = self.lines[label]
        line.set_visible(not line.get_visible())
        # store visibility state of the line in array
        self.activespecs[self.labels.index(label)] = line.get_visible()

        plt.draw()
    
    def plot_all(self, event):
        """
        Callback function to make all lines visible and check all boxes.
        """
        for label, line in self.lines.items():
            if line.get_visible() == True:
                line.set_visible(False)
            else:
                line.set_visible(True)
            self.toggle_visibility(label)
            # store visibility state of the line in array

            self.activespecs[self.labels.index(label)] = line.get_visible()
        for i in range(len(self.check.labels)):
            self.check.set_active(i)  # Check all boxes

        plt.draw()
    
    def save_plot(self, event):
        """
        Callback function to save the current plot as an image with 600 DPI.
        Opens a file dialog to select the file save location.
        """
        # Hide the main Tkinter window
        root = Tk()
        root.withdraw()
        
        # Open file dialog to select save path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            # Save the plot with 600 DPI
            self.fig.savefig(file_path, dpi=600)
            print(f"Plot saved to {file_path}")
        root.destroy()
    
    def show(self):
        """
        Display the plot.
        """
        plt.show()

class OpenSpec:
    def __init__(self, path, linearbg=False, loadeachbg=False):
        self.path = path
        self.spectra = {}
        self.readinkeys = ['WL']
        self.linearbg = linearbg
        self.loadeachbg = loadeachbg
        os.chdir(self.path)
        self.fnames = os.listdir(self.path)
        imax = len(self.fnames)
        i = 0
        while i < imax: 
            if '.txt' not in self.fnames[i]:
                self.fnames.pop(i)
                imax -= 1
            i+=1
        self.specs = {}

    def loadfiles(self):
        # read WL axis once for all files (must be same for all datafiles)
        gotWL = False
        gotBG = False
        i = 0
        self.WL = []
        self.BG = []
        while gotWL == False or gotBG == False:
            try:
                if self.fnames[i].split('.')[-1] == 'txt':
                    with open(self.fnames[i], 'r') as file:
                        lines = file.readlines()
            except Exception as e:
                print('Error While trying to read WL axis. No WL found in {} Files. {}'.format(i, str(e)))
            # Process lines to store variables
            startreaddata = False 
            for line in lines:
                if '\t' in line:  # Data lines with tabs
                    parts = line.split()
                    if startreaddata == False:
                        count = 0
                        # start reading if at least two keys in the line
                        for j in parts:
                            if j in self.readinkeys:
                                count += 1
                        if count > 0:
                            startreaddata = True
                    elif startreaddata == True:
                        if gotWL == False:
                            try:
                                self.WL.append(float(parts[0]))
                            except Exception as e:
                                print('Error While trying to read WL axis from {}. {}'.format(self.fnames[i], str(e)))
                        if gotBG == False or self.loadeachbg == False:
                            try:
                                self.BG.append(float(parts[1]))
                            except Exception as e:
                                print('Error While trying to read WL axis from {}. {}'.format(self.fnames[i], str(e)))

            i += 1
            if len(self.WL) > 1:
                gotWL = True
            if len(self.BG) > 1:
                gotBG = True
        
        if self.loadeachbg == False:
            if self.linearbg == True:
                av = np.mean(self.BG)
                for i in range(len(self.BG)):
                    self.BG[i] = av

        for i in self.fnames:
            powernW, tint = getpowerbyname(i)
            specobj = SpectrumData(i, self.WL, self.BG, self.loadeachbg, self.linearbg, powernW, tint)
            if specobj.dataokay == True:
                #self.specs.append(specobj)
                self.specs[i] = specobj

def getpowerbyname(name):
    power = '0'
    tint = 2
    if 'nW' in name:
        try:
            power = name.split('nW')[0].split('_')[-1]
            if power[0] == '0':
                power = float(power[1:])/10
            else:
                power = float(power)
        except Exception as e:
            print('Error while trying to get power from filename: {}'.format(str(e)))
            power = 0
    if 'sec' in name:
        try:
            tint = name.split('sec')[0].split('_')[-1]
            if tint[0] == '0':
                tint = float(tint[1:])/10
            else:
                tint = float(tint)  
        except Exception as e:
            print('Error while trying to get tint from filename: {}'.format(str(e)))
            tint = 2
    return power, tint

def savefig(fig, filename, dpi=600):
    # try to get savedir
    try:
        save_dir = save_dir_var.get()
        print('Save Directory: {}'.format(save_dir))
    except:
        # set savedir to current directory
        save_dir = os.getcwd()
        print('No savedir selected. Saving to current directory: {}'.format(save_dir))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    fig.savefig(os.path.join(save_dir, filename), dpi=dpi)
    print('Figure saved as: {}'.format(os.path.join(save_dir, filename)))
    

class PowerWLplot:
    def __init__(self, Laserspotarea=4.27): # laserspotarea in µm²
        self.openspec = []
        self.colors = ['red', 'blue', 'green', 'orange', 'purple', 'black', 'brown', 'pink', 'gray', 'cyan']
        self.powernW = []
        self.maxint = []
        self.maxinterror = []
        self.countsint = []
        self.countsinterror = []
        self.tint = []
        self.Laserspotarea = Laserspotarea
        self.specdata = []
        self.activespecs = []
    def getpowermaxint(self):
        powerN = []
        maxintN = []
        countsintN = []
        tintN = []
        maxintNerror = []
        countsintNerrorx = []
        countsintNerrory = []
        specdata = []
        activespecs = []
        for i in [-1]:#range(len(self.openspec)): # in range[-1]
            for j in range(len(list(self.openspec[i].specs.keys()))):
                powerN.append(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].powernW)
                maxintN.append(max(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].PLB))
                # X-Error power error: 0.005+2*3/powerN[-1]
                # Y-Error counts error: time 0.0005 counts 0.1 = 0.0005+0.1
                powererror = (0.005+2*3/powerN[-1])*powerN[-1]
                maxintNerror.append([
                    powererror,                 # X-Error                                                                       
                    np.std(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].PLB)+maxintN[-1]*(0.0005+0.05) # Y-Error
                    ])
                countsintN.append(sum(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].PLB))
                countsintNerrorx.append(powererror)
                countsintNerrory.append(np.sqrt(sum(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].PLB)))
                tintN.append(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].tint)
                specdata.append(self.openspec[i].specs[list(self.openspec[i].specs.keys())[j]].PLB)
                activespecs.append(True)
        # correction factors for all numbers
        for i in range(len(maxintN)):
            maxintN[i] /= tintN[i]
            #maxintN[i] /= self.Laserspotarea
            # powerN[i] /= self.Laserspotarea divide power by Laser spotarea if needed
            powerN[i] *= 0.3 # 3 is the factor that gets lost by the beam splitter and 4 mirrors
            countsintN[i] /= tintN[i] # divide powerN by the integration time in seconds
            for j in range(len(specdata[i])):
                specdata[i][j] /= tintN[i] # divide powerN by the integration time in seconds
        self.powernW.append(powerN) # is in sort
        self.maxint.append(maxintN) # is in sort
        # there was an issure with maxintNerror, maybe fix this in the future
        self.maxinterror = maxintNerror # is not in sort, maybe add 
        self.countsint.append(countsintN) # is in sort
        self.countsinterror.append([countsintNerrorx, countsintNerrory]) # is in sort
        self.tint.append(tintN) # is in sort
        self.specdata.append(specdata) # is in sort
        self.activespecs.append(activespecs) # is not in sort but is not required to be sorted (at the current time)

        # sort values by power
        #self.powernW, self.maxint, self.maxinterror, self.countsint, self.countsinterror, self.tint, self.specdata = zip(*sorted(zip(self.powernW, self.maxint, self.maxinterror, self.countsint, self.countsinterror, self.tint, self.specdata)))
        for i in range(len(self.powernW)):
            self.powernW[i], sortedarrays = sort_power_and_intensity(self.powernW[i], [self.maxint[i], self.countsint[i], self.countsinterror[i][0], self.countsinterror[i][1], self.tint[i], self.specdata[i]])
            index = 0
            self.maxint[i] = sortedarrays[index]
            index += 1
            self.countsint[i] = sortedarrays[index]
            index += 1
            self.countsinterror[i][0] = sortedarrays[index]
            index += 1
            self.countsinterror[i][1] = sortedarrays[index]
            index += 1
            self.tint[i] = sortedarrays[index]
            index += 1
            self.specdata[i] = sortedarrays[index] 
            # maybe add more items to sort here, depending on what is needed
            # note, 

        print('Power: {}'.format(self.powernW))

    def pltpowermaxintlinear(self):
        """Plots the power vs maximum intensity."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            ax.scatter(self.powernW[i], self.maxint[i], color=self.colors[i], label=labels[i])#'Counts {}'.format(i+1))
            # add error bars of maxint[i] to the plot
            ax.errorbar(self.powernW[i], self.maxint[i], yerr=self.maxinterror[i][1], xerr=self.maxinterror[i][0], fmt='o', color=self.colors[i])
            # fit a linear regression line to the data
            m, b = np.polyfit(self.powernW[i], self.maxint[i], 1)
            ax.plot(self.powernW[i], m*np.array(self.powernW[i]) + b, color=self.colors[i], label='Fit {}'.format(i+1))
            print("Slope: {:.2f}, Intercept: {:.2f}".format(m, b))

        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        # save fig with 600 dpi
        savefig(fig, 'PowerMaxIntlinear.png', 600)
    
    def plotpowercountsintlinear(self):
        """Plots the power vs counts per second."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']

        for i in range(len(self.powernW)):
            ax.scatter(self.powernW[i], self.countsint[i], color=self.colors[i], label=labels[i])#'Counts {}'.format(i+1))
            # add error bars of countsint[i] to the plot
            ax.errorbar(self.powernW[i], self.countsint[i], yerr=self.countsinterror[i], fmt='o', color=self.colors[i])
            # fit a linear regression line to the data
            m, b = np.polyfit(self.powernW[i], self.countsint[i], 1)
            ax.plot(self.powernW[i], m*np.array(self.powernW[i]) + b
                    , color=self.colors[i], label='Fit {}'.format(i+1))
            print("Slope: {:.2f}, Intercept: {:.2f}".format(m, b))
        
        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerCountsIntlinear.png', 600)
    
    def pltpowermaxintzerofit(self):
        """Plots the power vs maximum intensity."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            print(i)
            ax.scatter(self.powernW[i], self.maxint[i], color=self.colors[i], label=labels[i])#'Measurement {}'.format(i+1))
            # add error bars of maxint[i] to the plot
            ax.errorbar(self.powernW[i], self.maxint[i], yerr=self.maxinterror[i][1], xerr=self.maxinterror[i][0], fmt='o', color=self.colors[i])
            # fit a linear regression line to the data
            # fit a line to the data that goes through the origin
            m = np.sum(np.multiply(self.powernW[i], self.maxint[i])) / np.sum(np.square(self.powernW[i]))
            ax.plot(self.powernW[i], m*np.array(self.powernW[i]), color=self.colors[i], label='Fit {}'.format(i+1))
            print("fit Slope: {:.2f}".format(m))

        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerMaxIntzerofit.png', 600)

    def pltpowercountsintzerofit(self):
        """Plots the power vs counts per second with a fit line through the origin."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            ax.scatter(self.powernW[i], self.countsint[i], color=self.colors[i],
                       label=labels[i])#'Counts {}'.format(i+1))
            # fit a fit line to the data that goes through the origin
            m = np.sum(np.multiply(self.powernW[i], self.countsint[i])) / np.sum(np.square(self.powernW[i]))
            ax.plot(self.powernW[i], m*np.array(self.powernW[i]), color=self
                    .colors[i], label='Fit {}'.format(i+1))
            print("fit Slope: {:.2f}".format(m))
        
        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerCountsIntzerofit.png', 600)
    
    def plotpowermaxintonlypoints(self):
        """Plots the power vs maximum intensity."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            print(i)
            ax.scatter(self.powernW[i], self.maxint[i], color=self.colors[i], label=labels[i])#'Measurement {}'.format(i+1))
            # add error bars of maxint[i] to the plot
            ax.errorbar(self.powernW[i], self.maxint[i], yerr=self.maxinterror[i][1], xerr=self.maxinterror[i][0], fmt='o', color=self.colors[i])

        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerMaxIntonlypoints.png', 600)
    
    def plotpowercountsintonlypoints(self):
        """Plots the power vs counts per second."""
        fig, ax = plt.subplots()
        labels = ['Increasing Power', 'Decreasing Power']
        for i in range(len(self.powernW)):
            ax.scatter(self.powernW[i], self.countsint[i], color=self.colors[i],
                       label=labels[i])
        ax.legend()
        ax.set_xlabel('Power in nW')#/$\mu m^2$')
        ax.set_ylabel('Counts per second')
        ax.set_title('$N_1$ Perovskites Excitation Power vs PL counts')
        plt.tight_layout()
        plt.show()
        savefig(fig, 'PowerCountsIntonlypoints.png', 600)
    
    def pltspecnormalized(self):
        """Plots the normalized spectra."""
        self.specnormalized = []
        self.specabs = []
        self.plotlabels = []
        self.WL = self.openspec[0].WL
        for i in range(len(self.openspec)):
            for j in range(len(self.openspec[i].specs)):
                # Normalize the spectra set the maximum to 1 and the minimum to 0
                maxspec = np.amax(self.specdata[i][j])
                minspec = np.amin(self.specdata[i][j])
                self.specnormalized.append((self.specdata[i][j] - minspec) / (maxspec - minspec))
                self.specabs.append(self.specdata[i][j])
                self.plotlabels.append('{} nW'.format(round(self.powernW[i][j], 1)))
            self.interactive_specplot = InteractivePlot(self.WL, self.specnormalized, self.activespecs[i], self.specabs, labels=self.plotlabels)
            self.interactive_specplot.show()

# Sorting function to sort the files by power
def get_sort_indexes(atosort):
    """
    Returns the indices that can be used to sort the array.
    
    Args:
        atosort (list): The array to be sorted.
    
    Returns:
        list: Indices that would sort the array.
    """
    asortind = sorted(range(len(atosort)), key=lambda i: atosort[i])
    return asortind

def sort_power_and_intensity(Power, Intensity):
    """
    Sorts the Power array and rearranges the Intensity arrays to maintain the pairing.
    
    Args:
        Power (list): The array of Power values to sort.
        Intensity (list of lists): The array of arrays of Intensity values paired with Power.
    
    Returns:
        tuple: Two sorted lists, (sorted_Power, sorted_Intensity), where sorted_Intensity
               has all subarrays rearranged to match the sorted Power order.
    """
    # Obtain the sorting indices
    asortind = get_sort_indexes(Power)
    
    # Rearrange Power based on sorting indices
    sorted_Power = [Power[i] for i in asortind]
    
    # Rearrange each Intensity sub-array based on sorting indices
    sorted_Intensity = [[Intensity[j][i] for i in asortind] for j in range(len(Intensity))]
    
    return sorted_Power, sorted_Intensity
    
# GUI Functionality
def select_search_dir():
    """Opens a directory selection dialog to choose the search directory."""
    dir_path = filedialog.askdirectory(title="Select Search Directory")
    if dir_path:
        search_dir_var.set(dir_path)

def loadfiles(PIplot):
    """Loads the files from the selected search directory."""
    search_dir = search_dir_var.get()
    if not search_dir:
        messagebox.showerror("Error", "Please select a search directory.")
        return
    openspec = OpenSpec(search_dir)
    openspec.loadfiles()
    PIplot.openspec.append(openspec)
    PIplot.getpowermaxint()

def plotpowermaxintaxpb(PIplot):
    PIplot.pltpowermaxintlinear()

def plotpowermaxnofit(PIplot):
    PIplot.plotpowermaxintonlypoints()

def select_save_dir(save_dir_var):
    print("Select Save Directory:", save_dir_var.get())
    """Opens a directory selection dialog to choose the save directory."""
    dir_path = filedialog.askdirectory(title="Select Save Directory")
    if dir_path:
        save_dir_var.set(dir_path)

# Example usage:
# Assuming the text files are located in a folder named "testfiles":
openspec = OpenSpec("C:/Users/volib/Desktop/Evaluation/code/SpecMap/SpecMap1/openspec/testfiles".replace('\\', '/'))
# Initialize GUI
root = tk.Tk()
root.title("Plot Power vs PL Maximum (2sec Integration)")
windowwidth = 400
windowheight = 450
root.geometry("{}x{}".format(windowwidth, windowheight))

# Variables to hold directory paths
PIplot = PowerWLplot(5.3)
# Load files from selected directory
save_dir_var = tk.StringVar()
# set to C:\Users\volib\Desktop\Promotion\Reports\2025\250114\images
save_dir_var.set('C:/Users/volib/Desktop/Promotion/Reports/2025/250114/images/rising'.replace('\\', '/'))
search_dir_var = tk.StringVar()

# Create Widgets
tk.Button(root, text="Select Search Directory", command=select_search_dir).pack()
tk.Button(root, text="Load Files", command=lambda: loadfiles(PIplot)).pack()
# add save directory selection
tk.Label(root, text="Save Directory:").pack()
# add save directory selection button
tk.Button(root, text="Select Save Directory", command=lambda: select_save_dir(save_dir_var)).pack()
saveentry = tk.Entry(root, textvariable=save_dir_var, width=windowwidth).pack()

# add spacing # Highest Intensity
tk.Label(root, text="Highest Intensity").pack()
tk.Button(root, text="Plot Power vs Max Intensity", command=lambda: plotpowermaxnofit(PIplot)).pack()
tk.Button(root, text="Plot Power vs PL Maximum Linear", command=lambda: plotpowermaxintaxpb(PIplot)).pack()
tk.Button(root, text="Plot Power vs PL Maximum Zero fit", command=lambda: PIplot.pltpowermaxintzerofit()).pack()
# add spacing # Integrate spectrum
tk.Label(root, text="Full Spectrum integrated").pack()
tk.Button(root, text="Plot Power vs Counts per second", command=lambda: PIplot.plotpowercountsintonlypoints()).pack()
tk.Button(root, text="Plot Power vs Counts per second Linear", command=lambda: PIplot.plotpowercountsintlinear()).pack()
tk.Button(root, text="Plot Power vs Counts per second Zero fit", command=lambda: PIplot.pltpowercountsintzerofit()).pack()
# add spacing # Plot all spectra normalized
tk.Label(root, text="Plot all spectra normalized").pack()
tk.Button(root, text="Plot all spectra normalized", command=lambda: PIplot.pltspecnormalized()).pack()

root.mainloop()