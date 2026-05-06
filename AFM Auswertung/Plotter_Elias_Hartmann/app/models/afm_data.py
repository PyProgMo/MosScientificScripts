import pandas as pd
import numpy as np

class AFMData:
    """
    Model representing parsed AFM Data.
    Handles loading the custom text format into a 2D matrix for imshow plotting.
    """
    def __init__(self):
        self.filepath = None
        self.metadata = {}
        self.matrix_z = None
        self.extent = None # [xmin, xmax, ymin, ymax]
        
    def load_from_file(self, filepath):
        self.filepath = filepath
        self.metadata = {}
        self.matrix_z = None
        self.extent = None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        data_start_idx = 0
        
        # Parse metadata
        for i, line in enumerate(lines):
            line_str = line.strip()
            if not line_str:
                continue
                
            if line_str.startswith('X\t') or 'X' in line_str and 'Y' in line_str and 'Z' in line_str:
                data_start_idx = i + 1
                break
                
            if ':' in line_str:
                key, val = line_str.split(':', 1)
                self.metadata[key.strip()] = val.strip()

        # Parse Data block
        raw_rows = []
        for line in lines[data_start_idx:]:
            row_str = line.strip()
            if not row_str:
                continue
            
            # Convert comma decimal to dot
            row_clean = row_str.replace(',', '.')
            parts = row_clean.split()
            if len(parts) >= 3:
                try:
                    raw_rows.append([float(parts[0]), float(parts[1]), float(parts[2])])
                except ValueError:
                    continue

        if not raw_rows:
            raise ValueError("No valid data found after header.")
            
        df = pd.DataFrame(raw_rows, columns=['X', 'Y', 'Z'])
        
        # Convert X,Y,Z table into a solid 2D matrix.
        # Pivot the table assuming a regular grid
        pivot_df = df.pivot_table(index='Y', columns='X', values='Z')
        
        # Depending on plotting convention, pivot might need to be sorted/inverted.
        # Imshow naturally places origin at top-left. Sort index/col just to be sure.
        pivot_df = pivot_df.sort_index(ascending=True) # Y
        pivot_df = pivot_df.sort_index(axis=1, ascending=True) # X
        
        self.matrix_z = pivot_df.values
        
        # Calculate extent bounds: [left, right, bottom, top]
        self.extent = [df['X'].min(), df['X'].max(), df['Y'].min(), df['Y'].max()]
        
    def get_metadata_str(self):
        return "\n".join([f"{k}: {v}" for k, v in self.metadata.items()])
