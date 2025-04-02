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
            print("Please load both spectra first.")
            return

        # Extract wavelengths and values from both spectra
        wavelengths1 = self.spectrum1[:, 0]
        values1 = self.spectrum1[:, 1]
        # Extract wavelengths and values from both spectra
        wavelengths1 = self.spectrum1[:, 0]
        values1 = self.spectrum1[:, 1]
        
        # Create pandas DataFrame for spectrum 1
        self.dfs1 = pd.DataFrame({'WL': wavelengths1, 'counts': values1})

        wavelengths2 = self.spectrum2[:, 0]
        values2 = self.spectrum2[:, 1]

        self.dfs2 = pd.DataFrame({'WL': wavelengths2, 'counts': values2})
        # remove overlapping wavelengths from spectrum 2
        print('removing overlapping wavelengths')
        #self.dfs1, self.dfs2 = self.removeoverlap(self.dfs1, self.dfs2)
        self.dfs1, self.dfs2 = self.interpoverlap(self.dfs1, self.dfs2)

        # plot dfs1 and dfs2
        plt.plot(self.dfs1['WL'], self.dfs1['counts'], label='Spectrum 1')
        plt.plot(self.dfs2['WL'], self.dfs2['counts'], label='Spectrum 2')
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

        # Get start and end of overlap
        wl1s = S1['WL'].iloc[0]
        wl1e = S1['WL'].iloc[-1]
        wl2s = S2['WL'].iloc[0]
        wl2e = S2['WL'].iloc[-1]
        print('wl1s:', wl1s, 'wl1e:', wl1e, 'wl2s:', wl2s, 'wl2e:', wl2e)

        # Determine and remove overlapping wavelengths
        # 1st case: S1 is before S2
        if wl1s < wl2e:
            if wl1e > wl2s:
                print('case 1')
                overlapcenter = (wl1e + wl2s) / 2
                S1 = S1[S1['WL'] < overlapcenter]
                S1 = S1[S1['counts'] <= S1[S1['WL'] < overlapcenter]['counts'].max()]
                S2 = S2[S2['WL'] > overlapcenter]
                S2 = S2[S2['counts'] <= S2[S2['WL'] > overlapcenter]['counts'].max()]
        # 2nd case: S1 is after S2
        elif wl2s < wl1e:
            if wl2e > wl1s:
                print('case 2')
                overlapcenter = (wl2e + wl1s) / 2
                S2 = S2[S2['WL'] < overlapcenter]
                S2 = S2[S2['counts'] <= S2[S2['WL'] < overlapcenter]['counts'].max()]
                S1 = S1[S1['WL'] > overlapcenter]     
                S2 = S2[S2['counts'] <= S2[S2['WL'] > overlapcenter]['counts'].max()]
        return S1, S2

    def interpoverlap(self, S1, S2):
        # Remove overlapping wavelengths of the pd.dataframes S1 and S2
        # S1 is the first spectrum, S2 is the second spectrum
        # Find overlapping wavelengths

        # Get start and end of overlap
        wl1s = S1['WL'].iloc[0]
        wl1e = S1['WL'].iloc[-1]
        wl2s = S2['WL'].iloc[0]
        wl2e = S2['WL'].iloc[-1]
        print('wl1s:', wl1s, 'wl1e:', wl1e, 'wl2s:', wl2s, 'wl2e:', wl2e)

        # Determine and remove overlapping wavelengths
        # 1st case: S1 is before S2
        if wl1s < wl2e:
            if wl1e > wl2s:
                print('case 1')
                # Find overlap region
                overlap_start = max(wl1s, wl2s)
                overlap_end = min(wl1e, wl2e)
                
                # Create interpolation points in overlap region
                overlap_points = np.linspace(overlap_start, overlap_end, 100)
                
                # Interpolate both spectra in overlap region
                S1_interp = np.interp(overlap_points, 
                                    S1[S1['WL'].between(overlap_start, overlap_end)]['WL'],
                                    S1[S1['WL'].between(overlap_start, overlap_end)]['counts'])
                S2_interp = np.interp(overlap_points, 
                                    S2[S2['WL'].between(overlap_start, overlap_end)]['WL'],
                                    S2[S2['WL'].between(overlap_start, overlap_end)]['counts'])
                
                # Create weighted average transition
                weights = np.linspace(1, 0, len(overlap_points))
                interp_counts = S1_interp * weights + S2_interp * (1 - weights)
                
                # Create new dataframe with interpolated region
                S1 = S1[S1['WL'] < overlap_start]
                S2 = S2[S2['WL'] > overlap_end]

                # make sure S1 and S2 are sorted by WL
                S1 = S1.sort_values('WL')
                S2 = S2.sort_values('WL')

                # make sure S1 ['WL'] and S2 ['WL'] are of type float
                S1['WL'] = S1['WL'].astype(float)
                S2['WL'] = S2['WL'].astype(float)
                S1['counts'] = S1['counts'].astype(float)
                S2['counts'] = S2['counts'].astype(float)

                print(S1)
                print(S2)
                
                # Add interpolated region to S1
                overlap_df = pd.DataFrame({'WL': overlap_points, 'counts': interp_counts})
                S1 = pd.concat([S1, overlap_df]).sort_values('WL')
        # 2nd case: S1 is after S2
        elif wl2s < wl1e:
            if wl2e > wl1s:
                print('case 2')
                # Find overlap region
                overlap_start = max(wl2s, wl1s)
                overlap_end = min(wl2e, wl1e)
                
                # Create interpolation points in overlap region
                overlap_points = np.linspace(overlap_start, overlap_end, 100)
                
                # Interpolate both spectra in overlap region
                S2_interp = np.interp(overlap_points,
                                    S2[S2['WL'].between(overlap_start, overlap_end)]['WL'],
                                    S2[S2['WL'].between(overlap_start, overlap_end)]['counts'])
                S1_interp = np.interp(overlap_points,
                                    S1[S1['WL'].between(overlap_start, overlap_end)]['WL'],
                                    S1[S1['WL'].between(overlap_start, overlap_end)]['counts'])
                
                # Create weighted average transition
                weights = np.linspace(1, 0, len(overlap_points))
                interp_counts = S2_interp * weights + S1_interp * (1 - weights)
                
                # Create new dataframe with interpolated region
                S2 = S2[S2['WL'] < overlap_start]
                S1 = S1[S1['WL'] > overlap_end]
                
                # Add interpolated region to S2
                overlap_df = pd.DataFrame({'WL': overlap_points, 'counts': interp_counts})
                S2 = pd.concat([S2, overlap_df]).sort_values('WL')
        return S1, S2

if __name__ == "__main__":
    root = tk.Tk()
    app = SpectraGluingApp(root)
    root.mainloop()
