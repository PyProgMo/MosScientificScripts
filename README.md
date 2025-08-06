# MosPhDscripts

A collection of useful scripts for various purposes.

## Available Scripts

### [`Auto_stage_creator`](Auto_stage_creator)
Create coordinates for PLM VI autostage to prevent "holes" in the autostage map. especially for small steps important. Availabe for python(Auto_stage_creator/python) and c++(Auto_stage_creator/cpp)

### [`Imagescaling`](Imagescaling)
Just run the scripts in the folder: 'rotateimag2.py' and 'sci_rescale_7.py' checkout the two descriptions below

### [`rotateimage2`](Imagescaling)
Rotate an image by custom degree

### [`sci_rescale_X`](Imagescaling)
Add a scale to the image. Open the image, then move the scale.  
*Note: The scale spawns on the top right corner. Just dragndrop it.*

### [`Kinprocessing`](Kinprocessing)
Load Kinetic series of Clara images from PLM (files saved seperately) to process decaying signal

### [`Plotspec`](Plotspec)
Easy template to load a single spectrum and plot it in a jupyter notebook by a "quick'n'dirty" appreach

### [`SpectraStepAndGlue`](SpectraStepAndGlue)
Glue 2 spectra together (e g 400-520 nm and 500-720 nm to 400-720 nm)

### [`loaddefaults_examplecode`](loaddefaults_examplecode)
A Bigger bigger project needs default values that are stored in a txt file. This Project is the bridge from the .txt file to a dict

### [`plot_interface`](plot_interface)
Plot multiple spectra normalized. Use this to plot multiple spectra fast. Autor: Jakob Walter

### [`powermeasurements`](powermeasurements)
Measure spectra at different powers to obtain a power-dependency of the PL-intensity in the regime. Kind of fuzzy working with (maybe improvement might be required)

### [`pyautoclicker`](pyautoclicker)
Just what is says. An Autoclicker. Create ur procedure and run it when u want. 

### [`webplotdigitalizer`](webplotdigitalizer)
Maybe wrong name. Use Data with webplotdigizalizer to obtain data.txt. Than use this script to valuate the data. Find out if the figure and caption agree with each other. 
