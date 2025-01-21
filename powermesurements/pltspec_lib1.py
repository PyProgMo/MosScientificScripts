import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons, Button
from tkinter import Tk, filedialog

class InteractivePlot:
    def __init__(self, x, y_arrays, labels=None):
        """
        Initialize the interactive plot.
        Args:
            x (list or array): The x values shared by all datasets.
            y_arrays (list of lists or arrays): List of y datasets.
            labels (list of str): Labels for the datasets. If None, auto-generate labels as ['y1', 'y2', ...].
        """
        self.fig, self.ax = plt.subplots()
        
        # Dynamically adjust layout to leave space for checkboxes and buttons
        max_labels = len(y_arrays)
        checkbox_height = max(0.03 * max_labels, 0.3)  # Minimum height of 0.3, grows with more labels
        plt.subplots_adjust(left=0.5, bottom=0.1, top=1 - checkbox_height)
        
        # Use labels if provided, otherwise auto-generate labels
        self.labels = labels if labels else [f"y{i+1}" for i in range(len(y_arrays))]
        
        # Initialize data and plot lines
        self.lines = self.get_sample_data(x, y_arrays)
        self.check = None
        self.setup_plot(checkbox_height)
    
    def get_sample_data(self, x, y_arrays):
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
            lines[label] = self.ax.plot(x, y, label=label)[0]
            # name y-axis counts per second
            self.ax.set_ylabel('Counts per second')
            # name y-axis power in nW
            self.ax.set_ylabel('Power (nW)')
        return lines
    
    def setup_plot(self, checkbox_height):
        """
        Set up the plot, including checkboxes, buttons, and legend.
        Args:
            checkbox_height (float): Dynamic height of the checkbox area based on the number of datasets.
        """
        # Adjust checkbox area dynamically
        checkbox_start_y = 0.5 - checkbox_height / 2
        rax = plt.axes([0.05, checkbox_start_y, 0.3, checkbox_height])  # [left, bottom, width, height]
        self.check = CheckButtons(rax, labels=self.labels, actives=[True] * len(self.labels))
        
        # Add "Plot All" button
        button_ax_all = plt.axes([0.05, checkbox_start_y + checkbox_height + 0.05, 0.15, 0.05])  # "Plot All" button
        self.plot_all_button = Button(button_ax_all, 'Plot All')
        
        # Add "Save Plot" button
        button_ax_save = plt.axes([0.21, checkbox_start_y + checkbox_height + 0.05, 0.15, 0.05])  # "Save Plot" button
        self.save_plot_button = Button(button_ax_save, 'Save Plot')
        
        # Connect the callback functions
        self.check.on_clicked(self.toggle_visibility)
        self.plot_all_button.on_clicked(self.plot_all)
        self.save_plot_button.on_clicked(self.save_plot)
        
        # Add legend
        self.ax.legend()
    
    def toggle_visibility(self, label):
        """
        Callback function to toggle visibility of individual lines.
        """
        line = self.lines[label]
        line.set_visible(not line.get_visible())
        plt.draw()
    
    def plot_all(self, event):
        """
        Callback function to make all lines visible and check all boxes.
        """
        for label, line in self.lines.items():
            line.set_visible(True)
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

# Example usage
x = [0, 1, 2, 3, 4, 5]
y_arrays = [
    [0, 1, 4, 9, 16, 25],  # y1
    [0, -1, -2, -3, -4, -5],  # y2
    [5, 4, 3, 2, 1, 0],  # y3
    [2, 3, 4, 5, 6, 7],  # y4
    [10, 9, 8, 7, 6, 5],  # y5
    [1, 2, 1, 2, 1, 2],  # y6
    [-2, -3, -4, -5, -6, -7],  # y7
    [3, 2, 1, 0, -1, -2],  # y8
    [4, 5, 6, 7, 8, 9],  # y9
    [9, 8, 7, 6, 5, 4],  # y10
    [11, 12, 13, 14, 15, 16],  # y11
]
Labels = ['y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8', 'y9', 'y10', 'y11']

# Create and display the interactive plot
plot = InteractivePlot(x, y_arrays, Labels)
plot.show()
