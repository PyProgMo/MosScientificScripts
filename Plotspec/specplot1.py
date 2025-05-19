import numpy as np
import matplotlib.pyplot as plt
import os

def read_and_plot(filename):
    wavelengths = []
    intensities = []
    
    with open(filename, 'r') as file:
        for line in file:
            # Skip comment lines
            if line.startswith('#'):
                continue
            
            # Parse data lines
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    wavelength = float(parts[0])
                    intensity = float(parts[1])
                    wavelengths.append(wavelength)
                    intensities.append(intensity)
                except ValueError:
                    continue  # Skip lines that can't be parsed

    # Convert to numpy arrays for better performance
    wavelengths = np.array(wavelengths)
    intensities = np.array(intensities)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(wavelengths, intensities, label='Intensity', color='blue')
    plt.xlabel('Wavelength (nm)', fontsize=14)
    plt.ylabel('Intensity (counts)', fontsize=14)
    plt.title('Wavelength vs. Intensity', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    plt.legend(fontsize=12)
    plt.savefig('plot.png', dpi=1200)
    plt.show()

# change working directory to the dir of this file
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Example usage:
read_and_plot('spect1.txt')
