import numpy as np
import os, sys, re, cv2, copy, gzip, pickle, copy, bz2
from scipy.optimize import curve_fit
import scipy.sparse as sp
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.path import Path
from matplotlib.widgets import Button
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime

class imageprocessor():
    def __init__(self, Notebook, loadfunct, metadata, dx, dy, imagefile=''):
        self.Notebook = Notebook
        self.imagefile = imagefile
        self.loadfunct = loadfunct
        self.metadata = metadata
        self.dx = dx
        self.dy = dy
        self.g2dpopt = None
        self.loadfnvar = tk.StringVar()
        self.buildload()
    
    def buildload(self):
        # build a notebook to load the files
        self.load_frame = tk.Frame(self.Notebook, borderwidth=5, relief="ridge")
        self.load_frame.grid(row=0, column=0, sticky='nsew')
        # add a label to the frame
        self.load_label = tk.Label(self.load_frame, text='Load Image')
        self.load_label.grid(row=0, column=0)
        # show the filename
        self.loadfnvar.set(self.imagefile)
        self.load_filename = tk.Label(self.load_frame, textvariable=self.loadfnvar)
        self.load_filename.grid(row=0, column=1)
        # add a button to open a dialog to select the file
        self.load_button = tk.Button(self.load_frame, text='Browse', command=self.browsefile)
        self.load_button.grid(row=0, column=2)
        # add a button to load the file
        self.load_button = tk.Button(self.load_frame, text='Load', command=self.loadfile)
        self.load_button.grid(row=0, column=3)

    def browsefile(self):
        self.imagefile = tk.filedialog.askopenfilename()
        self.loadfnvar.set(self.imagefile)

    def loadfile(self):
        self.imagedata = self.loadfunct(self.imagefile)
        self.buildnotebook()

    def fit2dgaussian(self):
        self.g2dpopt = fit_gaussian_2d(self.imagedata, self.dx, self.dy)
    
    def buildnotebook(self):
        # load the image 
        self.imagedata = self.loadfunct(self.imagefile)
        # create a new frame for the image processing
        self.image_frame = tk.Frame(self.Notebook, borderwidth=5, relief="ridge")
        self.image_frame.grid(row=0, column=0, sticky='nsew')

        # create a new frame for the image processing
        self.image_frame = tk.Frame(self.Notebook, borderwidth=5, relief="ridge")
        self.image_frame.grid(row=0, column=0, sticky='nsew')
        self.plotimage = tk.Button(self.image_frame, text='Plot Image', command=self.plotimage)
        self.plotimage.grid(row=0, column=0)
        self.fitg2Dbutton = tk.Button(self.image_frame, text='Fit 2D Gaussian', command=lambda: self.fit2dgaussian())
        self.fitg2Dbutton.grid(row=0, column=1)
        self.plotfitbutton = tk.Button(self.image_frame, text='Plot Fit', command=lambda: plot2dfit(self.imagedata, self.g2dpopt, self.dx, self.dy))
        self.plotfitbutton.grid(row=0, column=2)
        self.area = tk.Button(self.image_frame, text='Area', command=lambda: area2dgaussian(self.imagefile, self.g2dpopt, np.exp(-2), self.dx, self.dy))
        self.area.grid(row=0, column=3)
    
# loadclaraimage function from deflib1
def loadclaraimage(file, metadata=False):
    coord = None
    readz = False
    if metadata == True:
        try:
            coord = float(file.split('\\')[-1].split('.')[0].replace('_', '.')) # z in mum
            readz = True
        except:
            readz = False
        if readz == False:
            spf = file.split('\\')[-1].split('.')[0]
            rc = 0
            for i in reversed(spf):
                if i.isdigit():
                    rc += 1
                else:
                    break
            try:
                coord = float(spf[-rc:])
            except:
                pass

    with open(file) as f:
        if metadata == True:
            mdr = {}
            for i in range(34):
                line = f.readline()
                match = re.match(r"^(.*?):\s+(.+)$", line.strip())
                if match:
                    key, value = match.groups()
                    mdr[key.strip()] = value.strip()
            mdr['z'] = coord
        # old: skip the first 34 lines
        else:
            for i in range(34):
                f.readline()
        fload = f.readlines()
    x = []
    y = []
    data = []
    for i in fload:
        isplit = i.split('\n')[0].split('\t')
        x.append(float(isplit[0]))
        for j in range(1, len(isplit)):
            if isplit[j] == '':
                pass
            else:
                y.append(float(isplit[j]))
        data.append(y)
        y = []  
    if metadata == True:
        return np.asarray(data), mdr
    else:
        return np.asarray(data)

def getcimages(dir):
    # try to load the files with loadlaraimage
    files = os.listdir(dir)
    try:
        files = [f for f in files if f.endswith('.asc')]
        if len(files) > 0:
            return files
    except:
        print('No files found')
        return []

class clarakinetics():
    def __init__(self, Notebook, dir, dx, dy):
        self.Notebook = Notebook
        self.dir = dir
        self.dx = dx
        self.dy = dy
        self.plotexists = False
        self.procplotexists = False
        self.plotprocimageN = 0
        self.plotimageN = 0
        self.colormap = tk.StringVar()
        self.dt = tk.StringVar()
        self.kinparam = tk.StringVar()
        self.selkinseries = tk.StringVar()
        self.kinmethod = tk.StringVar()
        self.proccolormap = tk.StringVar()
        self.sdir = tk.StringVar()
        self.imageN = tk.StringVar()
        self.procimageN = tk.StringVar()
        self.procseries = tk.StringVar()
        self.procseriesselect = tk.StringVar()
        self.loadfnvar = tk.StringVar()

        self.dt.set('15')
        self.colormap.set('gray')
        self.proccolormap.set('gray')
        self.buildnotebook()
    
    def buildnotebook(self):
        # create a new frame for the kinetics processing
        self.kinetics_frame = tk.Frame(self.Notebook, border=1, relief="ridge")
        self.kinetics_frame.grid(row=0, column=0, sticky='nsew')

        # add entry to select a dir and save on self.sdir

        self.sdir.set(self.dir)
        self.dirlabel = tk.Label(self.kinetics_frame, text='Directory:')
        self.dirlabel.grid(row=0, column=0, sticky='w')
        self.direntry = tk.Entry(self.kinetics_frame, textvariable=self.sdir, width=100)
        self.direntry.grid(row=0, column=1, sticky='w')
        # add a button to browse the files
        self.loadbutton = tk.Button(self.kinetics_frame, text='Browse', command=self.browsefiles)
        self.loadbutton.grid(row=0, column=2, sticky='w')
        # add a button to load the files
        self.loadbutton = tk.Button(self.kinetics_frame, text='Load', command=self.loadfiles)
        self.loadbutton.grid(row=0, column=3, sticky='w')

        # construct implotframe in a new frame on the notebook
        self.implframe = tk.Frame(self.kinetics_frame)
        self.implframe.grid(row=1, column=0, columnspan=4, sticky='nsew')

    def buildkinfit(self, frame, startcol=0, startrow=3):
        self.rateconstantvar = tk.StringVar()
        # add a spacer on the frame
        self.spacer = tk.Label(frame, text=' ')
        self.spacer.grid(row=startrow, column=startcol)

        # add a label to the frame
        self.kinlabel = tk.Label(frame, text='Kinetics model:')
        self.kinlabel.grid(row=startrow+1, column=startcol)

        # add a combobox to select the kinetics model
        self.kinorders = ['0 order', '1st order', '2nd order', '3rd order']
        self.kinordersel = ttk.Combobox(frame, values=self.kinorders, width=10)
        self.kinordersel.grid(row=startrow+1, column=startcol+1)
        # add button to obtain the rate constant
        self.kinbutton = tk.Button(frame, text='Calculate Rate Constant', command=lambda: self.compute_rate_constant(self.kinordersel.get(), self.kinetics_data, float(self.dt.get()), self.kinparam))
        self.kinbutton.grid(row=startrow+1, column=startcol+2)

        # display rate constant
        self.rateconstlabel = tk.Label(frame, text='Rate constant:')
        self.rateconstlabel.grid(row=startrow+2, column=startcol)
        # display the rate constant
        self.rateconstentry = tk.Label(frame, textvariable=self.rateconstantvar)
        self.rateconstentry.grid(row=startrow+2, column=startcol+1)

        # add a button to plot the kinetics and the fit


    def compute_rate_constant(self, order, y, dt, param):
        self.rateconstant = calculate_rate_constant(order, y, dt, param)
        self.rateconstantvar.set(str(self.rateconstant))
        
    def plotdataandfit(self, frame, x, y, fit, startcol=0, startrow=0):
        pass
    
    def kinplot(self, notebook, row=0):
        # get plotimage from self.cimages[i].imagedata
        self.plotimageN = 0

        # create a new frame for the image plotting where one image will be displayed
        self.implotframe = tk.Frame(notebook, border=2, relief='ridge')
        self.implotframe.grid(row=row, column=0, columnspan=4, sticky='nsew')

        # all possible colormaps
        self.allcmlist = list(plt.colormaps())
        # add a selectbox to select the colormap
        self.colormaplabel = tk.Label(self.implotframe, text='Colormap:')
        self.colormaplabel.grid(row=0, column=0)
        self.colormapselect = ttk.Combobox(self.implotframe, textvariable=self.colormap, values=self.allcmlist, width=10)
        # bind the selectbox to the function plotimage
        self.colormapselect.bind('<<ComboboxSelected>>', lambda event: self.plotimage())
        self.colormapselect.grid(row=0, column=1)
        # add a button to plot the image
        self.plotbutton = tk.Button(self.implotframe, text='Plot Image N', command=self.plotimage)
        self.plotbutton.grid(row=0, column=2)

        # add selectbox to select the image to plot
        self.imageN.set('0')
        self.imageNlabel = tk.Label(self.implotframe, text='Image:')
        self.imageNlabel.grid(row=0, column=3)
        # self.implotframe, self.imageN, *range(len(self.cimages)))
        self.imageNselect = ttk.Combobox(self.implotframe, textvariable=self.imageN, values=[str(i) for i in range(len(self.cimages))])
        # bind the selectbox to the function imageNselecttoN
        self.imageNselect.bind('<<ComboboxSelected>>', lambda event: self.imageNselecttoN())
        self.imageNselect.grid(row=0, column=4)

        # add 2 buttons to switch in the kinetic series 
        self.prevbutton = tk.Button(self.implotframe, text='Previous', command=self.previmage)
        self.prevbutton.grid(row=1, column=0)
        self.nextbutton = tk.Button(self.implotframe, text='Next', command=self.nextimage)
        self.nextbutton.grid(row=1, column=2)
        # print which N image is being displayed
        self.imlabel = tk.Label(self.implotframe, text='Image: '+str(self.plotimageN))
        self.imlabel.grid(row=1, column=1)
    
    def imageNselecttoN(self):
        self.plotimageN = int(self.imageN.get())
        self.updimglabel()
        self.plotimage()

    def plotimage(self):
        # update the image according to the selected image
        self.pltimg = np.asarray(self.cimages[self.plotimageN].imagedata)

        # if plot already exists: 
        if self.plotexists:
            # just adjust the image
            self.cim = self.ax.imshow(self.pltimg, cmap=self.colormap.get())
            # delete the colorbar and create a new one
            self.cbar.remove()
            self.cbar = self.fig.colorbar(self.cim, ax=self.ax)

        else:
            # create a new plot
            self.fig, self.ax = plt.subplots(figsize=(5, 5))
            self.cim = self.ax.imshow(self.pltimg, cmap=self.colormap.get())
            self.plotexists = True
            # add colorbar
            self.cbar = self.fig.colorbar(self.cim, ax=self.ax)

        # set cmat to gryscale
        self.ax.set_title(self.cfnames[self.plotimageN])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_aspect('equal')
        self.ax.grid(False)

        # add close event
        self.fig.canvas.mpl_connect('close_event', lambda event: self.close())
        # show the plot
        self.fig.show()
    
    def updateimage(self):
        self.updimglabel()
        self.plotimage()
    
    def updateprocimage(self):
        self.updprocimglabel()
        self.plotprocimage()
        self.selkinseriesbox.set(self.procseriesselect.get())

    def nextimage(self):
        self.plotimageN += 1
        if self.plotimageN >= len(self.cimages):
            self.plotimageN = 0
        self.updateimage()
    
    def nextprocimage(self):
        self.plotprocimageN += 1
        if self.plotprocimageN >= len(self.procimages[self.procseriesselect.get()]):
            self.plotprocimageN = 0
        self.updateprocimage()

    def previmage(self):
        self.plotimageN -= 1
        if self.plotimageN < 0:
            self.plotimageN = len(self.cimages)-1
        self.updateimage()
    
    def prevprocimage(self):
        self.plotprocimageN -= 1
        if self.plotprocimageN < 0:
            self.plotprocimageN = len(self.procimages[self.procseriesselect.get()])-1
        self.updateprocimage()

    def updloaddir(self):
        self.dir = self.sdir.get()

        self.cfnames = getcimages(self.dir)
        print('Loaded', len(self.cfnames), 'files')
    
    def updimglabel(self):
        text='Image: '+str(self.plotimageN)
        self.imlabel.config(text=text)
    
    def updprocimglabel(self):
        text='Image: '+str(self.plotprocimageN)
        self.procimlabel.config(text=text)
    
    def loadfiles(self):
        self.cimages = []
        self.cfnames = []
        self.cfnames = getcimages(self.dir)
        for i in range(len(self.cfnames)):
            self.cimages.append(clarafile(self.dir+"\\"+self.cfnames[i], self.dx, self.dy))

        self.kinplot(self.Notebook, row=2)  # plot the loaded images
        self.buildroiframe(self.Notebook, row=3) # build the roi editing frame
        self.buildprocframe(self.Notebook, row=4) # build the processed images frame
        self.buildkinframe(self.Notebook, row=5) # build the kinetics processing frame

    def browsefiles(self):
        self.dir = tk.filedialog.askdirectory()
        self.sdir.set(self.dir)
    
    def close(self):
        self.plotexists = False
    
    def procclose(self):
        self.procplotexists = False
    
    def buildroiframe(self, notebook, row=0):
        self.roilist = {}

        # create a new frame for the roi editing on the notebook
        self.roiframe = tk.Frame(notebook, border=2, relief='ridge')
        self.roiframe.grid(row=row, column=0, sticky='nsew')
        # add text to the frame
        self.roilabel = tk.Label(self.roiframe, text='ROI Editing')
        self.roilabel.grid(row=0, column=0, sticky='w')
        # add a combobox to select the roi
        self.roiselgui = ttk.Combobox(self.roiframe, values=list(self.roilist.keys()))
        self.roiselgui.grid(row=0, column=1)
        self.roihand = Roihandler(self.roilist, self.cimages[0].imagedata)

        # add start button to start the roi selection
        self.startbutton = tk.Button(self.roiframe, text='Start ROI editing', command=lambda: self.roihand.construct(self.cimages[0].imagedata, self.roiselgui))
        self.startbutton.grid(row=0, column=2)
        # add a button to delete the roi
        self.delbutton = tk.Button(self.roiframe, text='Delete ROI', command=self.roihand.delete_roi)
        self.delbutton.grid(row=0, column=3)
        # add a button to plot the roi
        self.plotroibutton = tk.Button(self.roiframe, text='Plot ROI', command=self.roihand.plotroi)
        self.plotroibutton.grid(row=0, column=4)
        # add a button to mulitply ROI with image data
        self.multiroibutton = tk.Button(self.roiframe, text='Multiply ROI to Images', command=self.multiroi2imagedata)
        self.multiroibutton.grid(row=0, column=5)
    
    '''
    def buildprocframe(self, notebook, row=0):
        # store processed image series in a dict
        self.procimages = {}

        self.procframe = tk.Frame(notebook, border=2, relief='ridge')
        self.procframe.grid(row=row, column=0, sticky='nsew')
        self.proclabel = tk.Label(self.roiframe, text='Processed Images')
        self.proclabel.grid(row=0, column=0, sticky='w')

        # add a combobox to select the processed image
        self.procimage = tk.StringVar()
        self.procimage.set('0') '''
    
    def multiroi2imagedata(self):
        roi = self.roilist[self.roiselgui.get()]
        seriesname = f'{self.roiselgui.get()}_series'
        # copy imageseries and store them in self.procimages
        self.procimages[seriesname] = copy.deepcopy(self.imageseries)
        # apply roi to the imageseries, set to to nan where roi is 0
        # old multiplication, very slow        
        '''
        for i in range(len(self.procimages[seriesname])):
            for j in range(len(self.procimages[seriesname][i])):
                for k in range(len(self.procimages[seriesname][i][j])):
                    if np.isnan(roi[j][k]):
                        self.procimages[seriesname][i][j][k] = np.nan
        '''
        # new multiplication, faster (thanks to github copilot for the idea XD)
        for i in range(len(self.procimages[seriesname])):
            self.procimages[seriesname][i] = np.where(np.isnan(roi), np.nan, self.procimages[seriesname][i])

        # update the entries in procseriesselect (values = self.procimages)
        self.updkinseries()
        # set the selected series to the new series
        self.procseriesselect.set(seriesname)

    def buildprocframe(self, notebook, row=0):
        self.procimages = {}
        self.procnextimage = 0
        # build a frame to plot the processed images
        self.plotprocimageN = 0

        # create a new frame to plot the processed images where the image will be displayed
        self.procplotframe = tk.Frame(notebook, border=2, relief='ridge')
        self.procplotframe.grid(row=row, column=0, sticky='nsew')

        # add a Label to the frame
        self.proclabel = tk.Label(self.procplotframe, text='Processed Kinetic Series')
        self.proclabel.grid(row=0, column=0)

        # add a combobox to select the Kinetic Series
        self.procseries.set('')
        self.procseriesselect = ttk.Combobox(self.procplotframe, textvariable=self.procseries, values=[list(self.procimages.keys())])
        self.procseriesselect.grid(row=0, column=1)
        self.procseriesselect.bind('<<ComboboxSelected>>', lambda event: self.plotprocimage())

        # all possible colormaps
        self.proccmlabel = tk.Label(self.procplotframe, text='Colormap:')
        self.proccmlabel.grid(row=1, column=0)
        self.proccmselect = ttk.Combobox(self.procplotframe, textvariable=self.proccolormap, values=self.allcmlist, width=10)
        self.proccmselect.bind('<<ComboboxSelected>>', lambda event: self.plotprocimage())
        self.proccmselect.grid(row=1, column=1)
        # add a button to plot the image
        self.plotprocbutton = tk.Button(self.procplotframe, text='Plot Processed Image N', command=self.plotprocimage)
        self.plotprocbutton.grid(row=1, column=2)

        # add selectbox to select the image to plot
        self.procimageN.set('0')
        self.procimageNlabel = tk.Label(self.procplotframe, text='Image:')
        self.procimageNlabel.grid(row=1, column=3)
        self.procimageNselect = ttk.Combobox(self.procplotframe, textvariable=self.procimageN, values=[str(i) for i in range(len(self.cimages))])
        self.procimageNselect.bind('<<ComboboxSelected>>', lambda event: self.procimageNselecttoN())
        self.procimageNselect.grid(row=1, column=4)

        # add 2 buttons to switch in the kinetic series
        self.prevprocbutton = tk.Button(self.procplotframe, text='Previous', command=self.prevprocimage)
        self.prevprocbutton.grid(row=2, column=0)
        self.nextprocbutton = tk.Button(self.procplotframe, text='Next', command=self.nextprocimage)
        self.nextprocbutton.grid(row=2, column=2)
        # print which N image is being displayed
        self.procimlabel = tk.Label(self.procplotframe, text='Image: '+str(self.plotprocimageN))
        self.procimlabel.grid(row=2, column=1)

        # add a button to export the selected image to a file
        self.exportprocimbutton = tk.Button(self.procplotframe, text='Export Processed Image', command=self.exportprocimage)
        self.exportprocimbutton.grid(row=2, column=5)

        # add a button to load or save a series
        self.savekinbutton = tk.Button(self.procplotframe, text='Save Kinetic Series', command=self.savekinseries)
        self.savekinbutton.grid(row=2, column=3)
        self.loadkinbutton = tk.Button(self.procplotframe, text='Load Kinetic Series', command=self.loadkinseries)
        self.loadkinbutton.grid(row=2, column=4)
    
    def exportprocimage(self):
        # ask for a filename
        filename = tk.filedialog.asksaveasfilename(defaultextension='.npy')
        # export the image
        np.save(filename, self.procimages[self.procseriesselect.get()][self.plotprocimageN])

    def savekinseries(self):
        # ask for a filename
        filename = tk.filedialog.asksaveasfilename(defaultextension='.roiims')
        # save the series to the file
        #np.save(filename, self.procimages[self.procseriesselect.get()])
        compsaveimseries(self.procimages[self.procseriesselect.get()], filename)
    
    def loadkinseries(self):
        # ask for a filename
        filename = tk.filedialog.askopenfilename()
        # load the series from the file
        loadedname = 'loaded_'+filename.split('/')[-1].split('.')[0]
        # add the loaded series to the keys of procseriesselect
        # self.procimages[loadedname] = np.load(filename)
        self.procimages[loadedname] = comploadimseries(filename)
        # update the entries in procseriesselect (values = self.procimages)
        self.updkinseries()
        # set the selected series to the new series
        self.procseriesselect.set(loadedname)
        
    
    def procimageNselecttoN(self):
        self.plotprocimageN = int(self.procimageN.get())
        self.plotprocimage()

    def plotprocimage(self):
        # set procpltimg to np.nan on all pixels
        self.procpltimg = np.full_like(self.cimages[0].imagedata, np.nan) 
        # set the image
        self.procpltimg = np.asarray(self.procimages[self.procseriesselect.get()][self.plotprocimageN])
        # if plot already exists:
        if self.procplotexists:
            # just adjust the image
            self.proccim = self.procax.imshow(self.procpltimg, cmap=self.proccolormap.get())
            # delete the colorbar and create a new one
            self.proccbar.remove()
            self.proccbar = self.procfig.colorbar(self.proccim, ax=self.procax)
        
        else:
            # create a new plot
            self.procfig, self.procax = plt.subplots(figsize=(5, 5))
            self.proccim = self.procax.imshow(self.procpltimg, cmap=self.proccolormap.get())
            self.procplotexists = True
            # add colorbar
            self.proccbar = self.procfig.colorbar(self.proccim, ax=self.procax)

        # set proccmat to gryscale
        self.procax.set_title(self.cfnames[self.plotprocimageN])
        self.procax.set_xlabel('X')
        self.procax.set_ylabel('Y')
        self.procax.set_aspect('equal')
        self.procax.grid(False)

        # add close event
        self.procfig.canvas.mpl_connect('close_event', lambda event: self.procclose()) 
        # show the plot
        self.procfig.show()

    def updateprocimage(self):
        self.updprocimglabel()
        self.plotprocimage()
    
    def updkinseries(self):
        #self.procseriesselect = ttk.Combobox(self.procplotframe, textvariable=self.procseries, values=[list(self.procimages.keys())])
        # update the entries of the combobox
        self.procseriesselect['values'] = list(self.procimages.keys())
        self.selkinseriesbox['values'] = list(self.procimages.keys())
    
    def buildkinframe(self, notebook, row=0):
        self.kinframe = tk.Frame(notebook, border=2, relief='ridge')
        self.kinframe.grid(row=row, column=0, sticky='nsew')
        
        # add a headline to the frame
        self.kinlabel = tk.Label(self.kinframe, text='Kinetics Processing')
        # grid the headline to the first row
        self.kinlabel.grid(row=0, sticky='w')

        # select combobox to select a processed image
        self.selkinserieslabel = tk.Label(self.kinframe, text='Select series:')
        self.selkinserieslabel.grid(row=1, column=0)
        self.selkinseriesbox = ttk.Combobox(self.kinframe, textvariable=self.selkinseries, values=[list(self.procimages.keys())])
        self.selkinseriesbox.grid(row=1, column=1)

        # add entry for dt (seconds)
        self.dtlabel = tk.Label(self.kinframe, text='dt (min):')
        self.dtlabel.grid(row=1, column=2)
        self.dtentry = tk.Entry(self.kinframe, textvariable=self.dt, width=10)
        self.dtentry.grid(row=1, column=3)

        # store image series in self.imageseries
        self.imageseries = []
        for i in range(len(self.cimages)):
            self.imageseries.append(self.cimages[i].imagedata)
        
        self.kinmethods = ['Thresholding', 'Integration', 'Edge detection']
        self.kinmethodlabel = tk.Label(self.kinframe, text='Select Int method:')
        self.kinmethodlabel.grid(row=2, column=0)
        # select method to compute the kinetics
        self.kinmethod.set(self.kinmethods[0])
        self.kinmethodselect = ttk.Combobox(self.kinframe, textvariable=self.kinmethod, values=self.kinmethods)
        self.kinmethodselect.grid(row=2, column=1)

        # add a parameter for kinetics processing
        self.kinparamlabel = tk.Label(self.kinframe, text='Parameter:')
        self.kinparamlabel.grid(row=2, column=2)
        self.kinparam = tk.Entry(self.kinframe, textvariable=self.kinparam, width=10)
        self.kinparam.grid(row=2, column=3)
        
        # create a new instance of NanocrystalKinetics
        self.Nckin = NanocrystalKinetics(self.imageseries)
        
        # add a button to compute the kinetics
        self.kinbutton = tk.Button(self.kinframe, text='Calculate Kinetics', command=lambda: self.comptokin())
        self.kinbutton.grid(row=2, column=4)

        # add a button to plot the kinetics
        self.plotkinbutton = tk.Button(self.kinframe, text='Plot Kinetics', command=self.Nckin.plot_kinetics)
        self.plotkinbutton.grid(row=2, column=5)

        # export kinetics image to a file
        self.exportkinbutton = tk.Button(self.kinframe, text='Export Kinetics', command=self.exportkinetics)
        self.exportkinbutton.grid(row=2, column=6)
    
    def comptokin(self):
        self.kinetics_data = self.Nckin.compute_kinetics1(self.procimages[self.procseriesselect.get()], float(self.dt.get()), self.kinmethod.get())
        self.buildkinfit(self.kinframe)
    
    def exportkinetics(self):

        list = self.Nckin.plotxaxis.tolist()
        # ask for a filename
        filename = tk.filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])
        #np.savetxt(filename, np.column_stack(np.round(self.Nckin.plotxaxis, 6), np.round(self.Nckin.kinetics_data, 6), delimiter=';', header='Time (s), Kinetics'))
        np.savetxt(filename, np.column_stack((np.round(self.Nckin.plotxaxis, 12), np.round(self.Nckin.kinetics_data, 12))), delimiter=';', header='Time (s), Kinetics')
        #np.savetxt(filename, np.column_stack((self.Nckin.plotxaxis, self.Nckin.kinetics_data)), delimiter=';', header='Time (s); Kinetics', fmt='%.6f', newline='\n', comments='', encoding='utf-8')

        with open(filename, 'w') as f:
            f.write('Time (s); Kinetics\n')
            for i in range(len(self.Nckin.plotxaxis)):
                # german export format for excel files
                f.write(str(self.Nckin.plotxaxis[i]).replace('.', ',')+';'+str(self.Nckin.kinetics_data[i]).replace('.', ',')+'\n')

class clarafile():
    def __init__(self, file, dx, dy):
        self.fn = file
        self.dx = dx
        self.dy = dy
        self.imagedata, self.metadata = loadclaraimage(self.fn, True)
        self.time = datetime.strptime(self.metadata['Date and Time'], "%a %b %d %H:%M:%S.%f %Y")
        self.tint = self.metadata['Exposure Time (secs)']

def gaussian_2d(coords, x0, y0, sigma_x, sigma_y, amplitude):
    """
    Compute a 2D Gaussian function.
    """
    x, y = coords
    return amplitude * np.exp(
        -(((x - x0)**2) / (2 * sigma_x**2) + ((y - y0)**2) / (2 * sigma_y**2))
    ).ravel()

def fit_gaussian_2d(data, dx, dy):
    """
    Fit a 2D Gaussian function to the data.
    
    Parameters:
    - data: 2D numpy array containing the data to fit.
    - dx: Spacing along the x-axis.
    - dy: Spacing along the y-axis.
    
    Returns:
    - popt: Optimal parameters of the 2D Gaussian (x0, y0, sigma_x, sigma_y, amplitude).
    """
    # Create a meshgrid for the x and y values
    x = np.arange(data.shape[1]) * dx
    y = np.arange(data.shape[0]) * dy
    X, Y = np.meshgrid(x, y)

    # Initial guess for the parameters
    initial_guess = (
        x[np.argmax(data) % data.shape[1]],  # x0 guess
        y[np.argmax(data) // data.shape[1]],  # y0 guess
        1,  # sigma_x guess
        1,  # sigma_y guess
        np.max(data)  # amplitude guess
    )

    # Fit the 2D Gaussian function to the data
    popt, _ = curve_fit(
        gaussian_2d, (X.ravel(), Y.ravel()), data.ravel(), p0=initial_guess
    )
    return popt

def popt2fwhm(popt):
    """
    Convert the parameters of a 2D Gaussian fit to Full Width at Half Maximum (FWHM).
    """
    sigma_x, sigma_y = popt[2], popt[3]
    fwhm_x = 2 * np.sqrt(2 * np.log(2)) * sigma_x
    fwhm_y = 2 * np.sqrt(2 * np.log(2)) * sigma_y
    return fwhm_x, fwhm_y

def area2dgaussian(data, popt, thresh, dx, dy):
    # return the size of the area of the gaussian
    x0, y0, sigma_x, sigma_y, amplitude = popt
    xbelowthresh = find_x_thresh(x0, sigma_x, amplitude, thresh)
    ybelowthresh = find_x_thresh(y0, sigma_y, amplitude, thresh)
    xsize = abs(x0 - xbelowthresh)/2
    ysize = abs(y0 - ybelowthresh)/2
    print('fit widht x and y:', xsize, ysize, 'dx and dy:', dx, dy, 'x0, y0:', x0, y0, 'xsize, ysize:', xsize, ysize, 'xbelowthresh, ybelowthresh:', xbelowthresh, ybelowthresh)
    # Calculate the area of ellipse 
    print('Area of ellipse:', round(np.pi * xsize * ysize, 3))
    return np.pi * sigma_x * sigma_y

def plot2dfit(data, popt, dx, dy):
    """
    Plot the original 2D data and the 2D Gaussian fit.
    
    Parameters:
    - data: 2D numpy array containing the original data.
    - popt: Optimal parameters of the 2D Gaussian (x0, y0, sigma_x, sigma_y, amplitude).
    - dx: Spacing along the x-axis.
    - dy: Spacing along the y-axis.
    """
    # Extract fit parameters
    x0, y0, sigma_x, sigma_y, amplitude = popt
    
    # Create a meshgrid for the fit
    x = np.arange(data.shape[1]) * dx
    y = np.arange(data.shape[0]) * dy
    X, Y = np.meshgrid(x, y)

    # Compute the 2D Gaussian fit
    fit = amplitude * np.exp(
        -(((X - x0)**2) / (2 * sigma_x**2) + ((Y - y0)**2) / (2 * sigma_y**2))
    )

    # Plot the original data
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    ax[0].imshow(data, extent=[x.min(), x.max(), y.min(), y.max()], origin='lower', cmap='viridis')
    ax[0].set_title('Original Data')
    ax[0].set_xlabel('X in mum')
    ax[0].set_ylabel('Y in mum')
    
    # Plot the fitted data
    ax[1].imshow(fit, extent=[x.min(), x.max(), y.min(), y.max()], origin='lower', cmap='viridis')
    ax[1].set_title('2D Gaussian Fit')
    ax[1].set_xlabel('X in mum')
    ax[1].set_ylabel('Y in mum')

    # add colorbars
    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.87, 0.15, 0.05, 0.7])
    fig.colorbar(ax[0].imshow(data, extent=[x.min(), x.max(), y.min(), y.max()], origin='lower', cmap='viridis'), cax=cbar_ax)
    cbar_ax.set_ylabel('Counts')
    
    plt.tight_layout()
    plt.show()

def find_x_thresh(x0, sigma_x, amplitude, thresh):
    """
    Find x_thresh, the x-coordinate where the Gaussian amplitude falls to thresh.

    Parameters:
    - x0: Center of the Gaussian.
    - sigma_x: Standard deviation of the Gaussian along the x-axis.
    - amplitude: Peak amplitude of the Gaussian.
    - thresh: Threshold value to find x_thresh.

    Returns:
    - x_thresh: The x-coordinate where the amplitude equals thresh.
    # np.sqrt(-2 * sigma_x**2 * np.log(thresh / amplitude) is the formula for x_thresh
    # This formula is derived from the Gaussian function.
    # We can use this formula to find x_thresh without iterating over the Gaussian function.
    """
    if thresh > amplitude:
        raise ValueError("Threshold cannot exceed the Gaussian amplitude.")
    
    # Solve for x_thresh using the Gaussian formula
    x_thresh = x0 + np.sqrt(-2 * sigma_x**2 * np.log(thresh / amplitude))
    return x_thresh

class Roihandler():
    def __init__(self, roilist={}, pixmatrix=[[]]):
        self.roi_mode = True
        self.roi_points = []
        self.roi_lines = []
        self.fig = None
        self.roilist = roilist
        self.pixmatrix = pixmatrix
        self.pixmatrix = np.transpose(self.pixmatrix)

    def construct(self, pixmatrix, roiselgui):
        self.roi_mode = True
        self.pixmatrix = pixmatrix
        self.pixmatrix = np.transpose(self.pixmatrix)
        self.roiselgui = roiselgui
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(right=0.89)# distance on right side for buttons
        self.ax.imshow(pixmatrix, cmap='viridis')
        # plt.axess([left, bottom, width, height])
        self.ax_button_toggle = plt.axes([0.89, 0.95, 0.1, 0.05])
        self.button_toggle = Button(self.ax_button_toggle, 'Save ROI')
        self.button_toggle.on_clicked(self.toggle_roi)
        self.ax_button_clear = plt.axes([0.89, 0.89, 0.1, 0.05])
        self.button_clear = Button(self.ax_button_clear, 'Clear ROI')
        self.button_clear.on_clicked(self.clear_roi)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.show()
        self.selnewestroi()

    def toggle_roi(self, event):
        if self.roi_mode == True:
            fig, ax = plt.subplots()
            self.button_toggle.label.set_text('Edit ROI')
            if len(self.roi_points) > 2:
                nrois = len(list(self.roilist.keys()))
                for i in range(len(self.roi_points)):
                    self.roi_points[i] = [float(self.roi_points[i][0]), float(self.roi_points[i][1])]
                newroi = highlight_roi(self.pixmatrix, self.roi_points)
                # transpose newroi
                #newroi = np.transpose(newroi)
                self.roilist[str('roi'+str(nrois+1))] = newroi
                cax = ax.imshow(newroi, cmap='viridis')
                # add colorbar to the plot
                cbar = fig.colorbar(cax, ax=ax)

                plt.show()
                self.roi_points.clear()
                self.roiselgui['values'] = list(self.roilist.keys()) # update the values of the combobox
                self.roiselgui.set(self.roiselgui['values'][-1]) # set the combobox to the newest roi
            self.roi_mode = False

        else:
            self.roiselgui['values'] = list(self.roilist.keys()) # update the values of the combobox
            self.roiselgui.set(self.roiselgui['values'][-1]) # set the combobox to the newest roi
            self.button_toggle.label.set_text('Save ROI')
            self.roi_points.clear()
            self.clear_roi_lines()
            self.roi_mode = True
            plt.draw()


    def clear_roi(self, event):
        self.clear_roi_points()
        self.clear_roi_lines()
        plt.draw()
            
    def on_click(self, event):
        if self.roi_mode and event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            self.roi_points.append((x, y))
            point_plot, = self.ax.plot(x, y, 'ro')
            self.roi_lines.append(point_plot)
            if len(self.roi_points) > 1:
                line_plot, = self.ax.plot([self.roi_points[-2][0], x],
                                            [self.roi_points[-2][1], y], 'r-')
                self.roi_lines.append(line_plot)
            plt.draw()

    def clear_roi_points(self):
        self.roi_points.clear()

    def clear_roi_lines(self):
        for line in self.roi_lines:
            line.remove()
        self.roi_lines.clear()
    
    def plotroi(self, fontsize=12):
        # get selection of self.roiselgui
        roi = self.roilist[self.roiselgui.get()]
        self.fig, self.ax = plt.subplots()
        cax = self.ax.imshow(roi, cmap='viridis')
        cbar = self.fig.colorbar(cax, ax=self.ax)
        cbar.set_label('ROI', fontsize=fontsize)
        cbar.ax.tick_params(labelsize=fontsize)
        self.ax.set_title('Region of Interest')
        self.ax.set_xlabel('Nanostage X Axis in \u03bcm', fontsize=fontsize)
        self.ax.set_ylabel('Nanostage Y Axis in \u03bcm', fontsize=fontsize)
        self.fig.canvas.draw()
        self.fig.show()

    def delete_roi(self):
        if self.roiselgui.get() != '':
            del self.roilist[self.roiselgui.get()]
            self.roiselgui['values'] = list(self.roilist.keys())
            self.selnewestroi()
            self.fig.canvas.draw()
        else:
            pass
    
    def selnewestroi(self):
        if len(self.roilist) > 0:
            self.roiselgui.set(list(self.roilist.keys())[-1])
        else:
            self.roiselgui.set('')

# highlight_roi function from deflib1
#roi = region of interest, returns a matrix with 1s in the region of interest and NaNs elsewhere
def highlight_roi(Mat, points):
    Mat = np.asarray(Mat)
    # Create a copy of the matrix initialized with NaN
    result = np.full_like(Mat, np.nan, dtype=float)
    # Get grid of all pixel coordinates in the matrix
    y, x = np.meshgrid(np.arange(Mat.shape[1]), np.arange(Mat.shape[0]))
    points_grid = np.vstack((x.ravel(), y.ravel())).T
    # Create a Path object from the points (closed polygon)
    polygon_path = Path(points)
    # Find which points are inside the polygon
    inside_mask = polygon_path.contains_points(points_grid)
    inside_mask = inside_mask.reshape(Mat.shape)
    # Set inside points to 1, leaving the rest as NaN
    result[inside_mask] = 1
    return np.transpose(result)

class NanocrystalKinetics:
    def __init__(self, image_series):
        """
        Initialize the class with a series of grayscale images.
        :param image_series: List or NumPy array of 2D grayscale images.
        """
        self.image_series = image_series
        self.kinetics_data = None

    def compute_kinetics1(self, imgs, dt, method):
        """
        Compute the kinetics by measuring the total area of the nanocrystals above a threshold.
        :param threshold: Intensity threshold to binarize images.
        :return: NumPy array with kinetics data over time.
        """
        self.dt = dt
        self.method = method
        kinetics = []
        self.image_series = imgs
        for img in self.image_series:
            # Ensure image is in uint8 format
            img_uint8 = np.uint8(img) if img.dtype != np.uint8 else img
            
            # Compute the total area of detected nanocrystals
            area = np.sum(img_uint8)
            kinetics.append(area)
        
        self.kinetics_data = np.array(kinetics)
        return self.kinetics_data

    def plot_kinetics(self):
        """
        Plot the kinetics data.
        """
        if self.kinetics_data is None:
            raise ValueError("Kinetics data not computed. Run compute_kinetics() first.")

        # dreate x-axis values according to self.dt
        self.plotxaxis = np.arange(len(self.kinetics_data)) * self.dt / 60
        self.axisfactor = 1000
        
        # create a plot
        self.kinfig, self.kinax = plt.subplots(figsize=(8, 5))
        #self.kinax.plot(self.kinetics_data, marker='o', linestyle='-') # no x-axis
        self.kinax.plot(self.plotxaxis, self.kinetics_data/self.axisfactor, marker='o', linestyle='-')
        self.kinax.set_title('Nanocrystal Kinetics')
        self.kinax.set_xlabel('Time (h)')
        self.kinax.set_ylabel('Image counts integrated x {}'.format(self.axisfactor))
        self.kinax.tick_params(axis='both', which='major', labelsize=14)
        self.kinax.grid(True)
        self.kinfig.tight_layout()
        self.kinfig.show()

# Example usage NanocrystalKinetics
# image_series = [np.random.randint(0, 255, (100, 100), dtype=np.uint8) for _ in range(10)]
# kinetics_analyzer = NanocrystalKinetics(image_series)
# kinetics_data = kinetics_analyzer.compute_kinetics(threshold=100)
# kinetics_analyzer.plot_kinetics()

class PlotManager:
    """Manages an individual plot in a separate Matplotlib window."""
    
    def __init__(self, data, title):
        self.data = data
        self.title = title
        self.figure, self.ax = plt.subplots()
        self.image = self.ax.imshow(self.data, cmap="viridis")
        self.ax.set_title(self.title)
        self.figure.canvas.manager.set_window_title(self.title)

    def update_plot(self, new_data):
        """Updates the plot with new data."""
        self.data = new_data
        self.image.set_data(self.data)
        self.ax.set_title("Updated " + self.title)
        self.figure.canvas.draw()

class PlotController:
    """Manages multiple plot instances and stores them in a dictionary."""
    
    def __init__(self):
        self.plots = {}  # Dictionary to store plot instances

    def create_plot(self, name, data):
        """Creates a new plot with a given name and stores it in the dictionary."""
        if name in self.plots:
            print(f"Plot '{name}' already exists!")
        else:
            self.plots[name] = PlotManager(data, name)  # Store plot in dictionary
            print(f"Created plot: {name}")

    def modify_plot(self, name):
        """Modifies an existing plot by updating its data with random values."""
        if name in self.plots:
            new_data = np.random.rand(*self.plots[name].data.shape) * 10  # Generate random data of the same shape
            self.plots[name].update_plot(new_data)
            print(f"Modified plot: {name}")
        else:
            print(f"Plot '{name}' does not exist!")

def compsaveimseries(array_series, filename):
    """
    Save an array of 2D arrays by replacing np.nan with (global max + 1) and compressing them.
    
    Parameters:
    - array_series: np.ndarray, array of 2D np.ndarrays containing np.nan values.
    - filename: str, the filename to save the compressed data.
    """
    # Determine the global maximum across all 2D arrays
    max_val = max(np.nanmax(arr) for arr in array_series)
    placeholder = max_val + 1
    
    # Replace np.nan with placeholder and convert each to sparse format
    sparse_series = []
    for arr in array_series:
        arr_replaced = np.where(np.isnan(arr), placeholder, arr)
        sparse_series.append(sp.csr_matrix(arr_replaced))
    
    # Save the sparse matrices and placeholder using gzip compression
    with gzip.open(filename, 'wb') as f:
        pickle.dump({'sparse_series': sparse_series, 'placeholder': placeholder}, f)

def comploadimseries(filename):
    """
    Load the compressed array series, restoring np.nan where appropriate.
    
    Parameters:
    - filename: str, the filename to load the compressed data from.
    
    Returns:
    - list of np.ndarray, the reconstructed 2D arrays with np.nan values.
    """
    # Load the data
    with gzip.open(filename, 'rb') as f:
        data = pickle.load(f)
    
    sparse_series = data['sparse_series']
    placeholder = data['placeholder']
    
    # Convert each sparse matrix back to dense and restore np.nan
    restored_series = []
    for sparse_matrix in sparse_series:
        dense_array = sparse_matrix.toarray()
        dense_array[dense_array == placeholder] = np.nan
        restored_series.append(dense_array)
    
    return restored_series

def calculate_rate_constant(order: str, y: np.ndarray, dt: float, param: float = 1.0) -> float:
    if not isinstance(dt, (float, int)):
        raise ValueError("Time interval (dt) must be a float or int.")

    y0 = y[0]  # Initial concentration
    yt = y[-1]  # Final concentration
    t = dt * (len(y) - 1)  # Total time

    if order == '0 order':
        # Zero-order rate constant from a linear fit where k is the slope
        p = np.polyfit(np.arange(len(y)) * dt, y, 1)
        k = p[0]
    elif order == '1st order':
        if yt <= 0:
            raise ValueError("Final concentration must be greater than zero for first-order reactions.")
        popt, _ = curve_fit(k1model, np.arange(len(y)) * dt, y, p0=[1.0, y0])
        k = popt[0]
    elif order == '2nd order':
        if yt == 0:
            raise ValueError("Final concentration cannot be zero for second-order reactions.")
        k = (1 / yt - 1 / y0) / t
    elif order == '3rd order':
        if yt == 0:
            raise ValueError("Final concentration cannot be zero for third-order reactions.")
        k = (1 / (yt ** 2) - 1 / (y0 ** 2)) / (2 * t)
    else:
        raise ValueError("Invalid reaction order. Choose from '0 order', '1st order', '2nd order', '3rd order'.")

    return k

# First-order rate constant from an exponential fit
def k1model(t, k, A):
    return A * np.exp(-k * t)