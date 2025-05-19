import os
DEFAULTS_FILE = 'defaults.txt'

defaulttypes = {
    # General inits
    'windowsize_X': int,
    'windowsize_Y': int,
    # Load Data Notebook
    'data_file': str,
    'filename': str,
    'file_extension': str,
    'multiple_Background': bool,
    'linear_Background': bool,
    'remove_cosmics': bool,
    'cosmic_threshold': int,
    'cosmic_width': int,
    'cosmic_method': str,
    'clara_image': str,
    'newton_spectrum': str,
    # Hyperspectra Notebook
    'lowest_wavelength': float,
    'highest_wavelength': float,
    'colormap_threshold': int,
    'fontsize': int,
    'maxfev': int,
    'Wavelength axis': str,
    'Background (BG)': str,
    'Counts (PL)': str,
    'Spectrum (PL-BG)': str,
    'data_set': str,
    'selected_pixel_x': int,
    'selected_pixel_y': int,
    'selected_fit_function': str,
    'seperate_fits': bool,
    'save_hsi': str,
    'load_hsi_saved': str, 
    'Matrix_grid_dx': float,
    'Matrix_grid_dy': float,
    'enable_buttonmatrix': bool, 
    'loadonstart': bool,
}

defaults={
    # General inits
    'Matrix_grid_dx': None,
    'Matrix_grid_dy': None,
    'windowsize_X': 900,
    'windowsize_Y': 900,
    # Load Data Notebook
    # Select Folder Frame
    'data_file': 'C:/Users/mol95ww/Desktop/Evaluation/data/VP/test7_MoS2_ML_2sec/test7_MoS2_ML_2sec',
    'filename': 'spectrum', 
    'file_extension': '.txt',
    # Background Subtraction Frame
    'multiple_Background': False,
    'linear_Background': True,
    # Cosmic Ray Removal Frame
    'remove_cosmics': False,
    'cosmic_threshold': 100,
    'cosmic_width': 10,
    'cosmic_method': 'Linear Interpolation',
    # Clara Image Frame
    'clara_image': 'C:/Users/mol95ww/Desktop/Evaluation/data/2024/qdot_100fach/Laser_in_zpos/145_0.asc',
    'newton_spectrum': 'C:/Users/mol95ww/Desktop/Evaluation/data/2024/Perovskite/N1_Sndoping/Pb-Sn_0_0625/PL_Sn_Image_0_0625_1250g_500lnm_470-1030nm.asc',
    # Hyperspectra Notebook
    # cmap frame
    'lowest_wavelength': 500, 
    'highest_wavelength': 700,
    'colormap_threshold': 10000,
    'fontsize': 13,
    'maxfev': 2000,
    #speckeys
    'Wavelength axis': 'WL', 
    'Background (BG)': 'BG',
    'Counts (PL)': 'PL', 
    'Spectrum (PL-BG)': 'PLB',
    'data_set': 'Spectrum (PL-BG)',
    # buttonframe
    'selected_pixel_x': 0,
    'selected_pixel_y': 0,
    'selected_fit_function': 'gaussian',
    'seperate_fits': False,
    'save_hsi': "hsidata/hsi.txt", 
    'load_hsi_saved': "hsidata/hsi.txt",
    'enable_buttonmatrix': False, 
    'loadonstart': False
}

# load defaults

def initdefaults():
    loadeddefaults = load_defaults()
    reqdefaults = defaults.copy()
    for i in loadeddefaults.keys():
        try:
            reqdefaults[i] = defaulttypes[i](loadeddefaults[i])
        except Exception as Error:
            if loadeddefaults[i] == 'None':
                pass
            else:
                print(f'Error: {Error} while loading Entries. Using default value: {i}={reqdefaults[i]}')
    return reqdefaults

# save defaults
def save_defaults(variables):
    """Save default values to a file."""
    with open(DEFAULTS_FILE, 'w') as file:
        for name, value in variables.items():
            file.write(f'{name} = {value}\n')

# load defaults
def load_defaults():
    """Load default values from a file."""
    variables = {}
    if os.path.exists(DEFAULTS_FILE):
        with open(DEFAULTS_FILE, 'r') as file:
            for line in file:
                # Split each line into name and value
                if '=' in line:
                    name, value = line.split('=', 1)
                    name = name.strip()
                    value = value.strip()
                    # Handle basic types
                    if value.isdigit():
                        value = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        value = float(value)
                    elif value.lower() in ('true', 'false'):
                        value = value.lower() == 'true'
                    elif value.lower() == 'none':
                        value = None
                    variables[name] = value
    return variables

def testdefaults():
    for i in list(defaults.keys()):
        if i not in list(defaulttypes.keys()):
            print(f'{i} not in defaulttypes')
        if i not in list(defaults.keys()):
            print(f'{i} not in defaults')
        if defaulttypes[i] != type(defaults[i]):
            print(f'{i} not the same type')
    for key, value in defaults.items():
        print(f'{key}: {value}')
    
    variables = load_defaults()
    for key, value in variables.items():
        print(f'{key}: {value}')


# check definitions 
if __name__ == '__main__':
    try:
        testdefaults()
        print('All definitions are correct')
    except Exception as Error:
        print('Error while loading defaults')
        print(f'Error: {Error}')

    # code for testing:
    # self.defaults = deflib.initdefaults()