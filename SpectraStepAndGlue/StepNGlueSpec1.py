import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt

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
            metadata = {}
            data_lines = []
            for line in file:
                if line.strip() == "":
                    break  # Stop reading metadata on empty line
                elif ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            # Read remaining lines as data lines
            for line in file:
                if line.strip():  # Only add non-empty lines
                    data_lines.append(line)
            self.spectrum1 = np.array([list(map(float, line.split('\t'))) for line in data_lines])
        messagebox.showinfo("Info", "Spectrum 1 loaded successfully.")

    def open_spectrum2(self):
        file_path = filedialog.askopenfilename()
        with open(file_path, 'r') as file:
            metadata = {}
            data_lines = []
            for line in file:
                if line.strip() == "":
                    break  # Stop reading metadata on empty line
                elif ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
            # Read remaining lines as data lines
            for line in file:
                if line.strip():  # Only add non-empty lines
                    data_lines.append(line)
            self.spectrum2 = np.array([list(map(float, line.split('\t'))) for line in data_lines])
        messagebox.showinfo("Info", "Spectrum 2 loaded successfully.")

    def glue_spectra(self):
        if self.spectrum1 is None or self.spectrum2 is None:
            messagebox.showerror("Error", "Please load both spectra first.")
            return
        # Assuming spectra are 1D arrays and we simply concatenate them
        self.result = np.concatenate((self.spectrum1, self.spectrum2))
        plt.plot(self.result)
        plt.title("Glued Spectrum")
        plt.show()
        messagebox.showinfo("Info", "Spectra glued successfully.")

    def save_result(self):
        if self.result is None:
            messagebox.showerror("Error", "No result to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text files", "*.txt"),
                                                              ("All files", "*.*")])
        np.savetxt(file_path, self.result)
        messagebox.showinfo("Info", "Result saved successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpectraGluingApp(root)
    root.mainloop()
