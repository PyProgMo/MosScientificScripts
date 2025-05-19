import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class SpectraGluingApp:
    def __init__(self, master):
        self.master = master
        master.title("Spectra Gluing Application")

        self.label = tk.Label(master, text="Open two spectra files to glue them together.")
        self.label.pack()

        self.open_button1 = tk.Button(master, text="Open Spectrum 1", command=self.open_spectrum1)
        self.open_button1.pack()

        self.open_button2 = tk.Button(master, text="Open Spectrum 2", command=self.open_spectrum2)
        self.open_button2.pack()

        self.glue_button = tk.Button(master, text="Glue Spectra", command=self.glue_spectra)
        self.glue_button.pack()

        self.save_button = tk.Button(master, text="Save Result", command=self.save_result)
        self.save_button.pack()

        self.spectrum1 = None
        self.spectrum2 = None
        self.result = None

    def open_spectrum1(self):
        file_path = filedialog.askopenfilename()
        with open(file_path, 'r') as file:
            self.metadata1 = {}
            data_lines = []
            for line in file:
                if line.strip() == "":
                    break  # Stop reading metadata on empty line
                elif ':' in line:
                    key, value = line.split(':', 1)
                    self.metadata1[key.strip()] = value.strip()
            # Read remaining lines as data lines
            for line in file:
                if line.strip():  # Only add non-empty lines
                    data_lines.append(line)
            self.spectrum1 = np.array([list(map(float, line.split('\t'))) for line in data_lines])
        print("Spectrum 1 loaded successfully.")

    def open_spectrum2(self):
        file_path = filedialog.askopenfilename()
        with open(file_path, 'r') as file:
            self.metadata2 = {}
            data_lines = []
            for line in file:
                if line.strip() == "":
                    break  # Stop reading metadata on empty line
                elif ':' in line:
                    key, value = line.split(':', 1)
                    self.metadata2[key.strip()] = value.strip()
            # Read remaining lines as data lines
            for line in file:
                if line.strip():  # Only add non-empty lines
                    data_lines.append(line)
            self.spectrum2 = np.array([list(map(float, line.split('\t'))) for line in data_lines])
        print("Spectrum 2 loaded successfully.")

    def glue_spectra(self):
        if self.spectrum1 is None or self.spectrum2 is None:
            messagebox.showerror("Error", "Please load both spectra first.")
            return

        # Extract wavelengths and values from both spectra
        wavelengths1 = self.spectrum1[:, 0]
        values1 = self.spectrum1[:, 1]
        # Extract wavelengths and values from both spectra
        wavelengths1 = self.spectrum1[:, 0]
        values1 = self.spectrum1[:, 1]
        
        # Create pandas DataFrame for spectrum 1
        dfs1 = pd.DataFrame({'WL': wavelengths1, 'counts': values1})

        wavelengths2 = self.spectrum2[:, 0]
        values2 = self.spectrum2[:, 1]

        dfs2 = pd.DataFrame({'WL': wavelengths2, 'counts': values2})
        # remove overlapping wavelengths from spectrum 2
        wavelengths2, values2 = self.removeoverlap(wavelengths1, wavelengths2, values2)
        plt.plot(wavelengths2, values2, label='Spectrum 2')
        plt.show()

        # Find overlapping wavelengths
        common_wavelengths = np.intersect1d(wavelengths1, wavelengths2)

        # Average the values at the overlapping wavelengths
        averaged_values = []
        for wl in common_wavelengths:
            idx1 = np.where(wavelengths1 == wl)[0][0]
            idx2 = np.where(wavelengths2 == wl)[0][0]
            avg_value = (values1[idx1] + values2[idx2]) / 2
            averaged_values.append((wl, avg_value))

        # Create a global wavelength array based on the first spectrum
        #global_wavelengths = np.linspace(np.min(wavelengths1), np.max(wavelengths1), num=1000)
        # Interpolate the second spectrum according to the global wavelengths
        #interpolated_values2 = np.interp(global_wavelengths, wavelengths2, values2)
        
        # Create final spectrum with interpolated values
        final_wavelengths = np.union1d(wavelengths1, wavelengths2)
        final_values = np.zeros_like(final_wavelengths)

        for wl, avg_value in averaged_values:
            final_values[np.where(final_wavelengths == wl)] = avg_value

        # Fill in non-overlapping values
        for wl in wavelengths1:
            if wl not in common_wavelengths:
                final_values[np.where(final_wavelengths == wl)] = values1[np.where(wavelengths1 == wl)]
        for wl in wavelengths2:
            if wl not in common_wavelengths:
                final_values[np.where(final_wavelengths == wl)] = values2[np.where(wavelengths2 == wl)]
        
        self.result = np.column_stack((final_wavelengths, final_values))
        plt.plot(self.result)
        # plot final_values vs final_wavelengths
        #plt.plot(final_wavelengths, final_values, label='Glued Spectrum')
        plt.title("Glued Spectrum")
        plt.show()
        print("Spectra glued successfully.")

    def save_result(self):
        writemetadata = {}
        for i in self.metadata1.keys():
            writemetadata[i+' Spec1'] = self.metadata1[i]
        for i in self.metadata2.keys():
            writemetadata[i+' Spec2'] = self.metadata2[i]
        writemetadata['Glued'] = 'True'

        if self.result is None:
            print("No result to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text files", "*.txt"),
                                                              ("All files", "*.*")])
        
        with open(file_path, 'w') as f:
            for key, value in writemetadata.items():
                f.write(f"{key} = {value}\n")
            f.write("\n")
            f.write("Wavelength\tSpectrumeter Counts\n")
            for row in self.result:
                f.write(f"{row[0]}\t{row[1]}\n")
        print("Result saved successfully.")
    
    def removeoverlap(self, S1, S2):
        # Remove overlapping wavelengths of the pd.dataframes S1 and S2
        # S1 is the first spectrum, S2 is the second spectrum
        # Find overlapping wavelengths
        overlap = np.intersect1d(S1['WL'], S2['WL'])
        if len(overlap) == 0:
            return S1, S2

        # Get start and end of overlap
        wl_start = np.min(overlap)
        wl_end = np.max(overlap)
        wl_middle = (wl_start + wl_end) / 2

        # Determine direction of arrays
        dir_s1 = 1 if S1['WL'].iloc[-1] > S1['WL'].iloc[0] else -1
        dir_s2 = 1 if S2['WL'].iloc[-1] > S2['WL'].iloc[0] else -1

        # Remove appropriate half of overlap from each spectrum
        if dir_s1 > 0:
            S1 = S1[S1['WL'] <= wl_middle]
        else:
            S1 = S1[S1['WL'] >= wl_middle]

        if dir_s2 > 0:
            S2 = S2[S2['WL'] >= wl_middle]
        else:
            S2 = S2[S2['WL'] <= wl_middle]

        return S1, S2

if __name__ == "__main__":
    root = tk.Tk()
    app = SpectraGluingApp(root)
    root.mainloop()
