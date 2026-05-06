import pandas as pd
import numpy as np

class AFM1DData:
    """
    Model representing parsed 1D AFM Data (e.g., a cross-section cut).
    Handles loading the text format into a pandas DataFrame for line plotting.
    """
    def __init__(self):
        self.filepath = None
        self.metadata = {}
        self.df = None
        
    def load_from_file(self, filepath):
        self.filepath = filepath
        self.metadata = {}
        self.df = None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        data_start_idx = 0
        
        # Parse metadata
        for i, line in enumerate(lines):
            line_str = line.strip()
            if not line_str:
                continue
                
            # If it looks like the header for a 2-column format
            if line_str.startswith('X\t') or ('X' in line_str and 'Y' in line_str and 'Z' not in line_str):
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
            
            # Convert comma decimal to dot (supports exponents too)
            row_clean = row_str.replace(',', '.')
            parts = row_clean.split()
            if len(parts) >= 2:
                try:
                    raw_rows.append([float(parts[0]), float(parts[1])])
                except ValueError:
                    continue

        if not raw_rows:
            raise ValueError("No valid 1D data found after header.")
            
        self.df = pd.DataFrame(raw_rows, columns=['Length', 'Height'])
        
        # Convert Units from meters to micrometers and nanometers
        if self.metadata.get('X Unit', '') == 'UnitMeter':
            self.df['Length'] *= 1e6
            self.metadata['X Unit'] = 'MicroMeter'
            
        if self.metadata.get('Y Unit', '') == 'UnitMeter':
            self.df['Height'] *= 1e9
            self.metadata['Y Unit'] = 'nm'
            
    def get_metadata_str(self):
        return "\n".join([f"{k}: {v}" for k, v in self.metadata.items()])