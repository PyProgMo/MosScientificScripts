import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class Kinobtainer():
    def __init__(self, imseries):
        self.kinseries = imseries # series of images as 2D numpy arrays
        self.kinlength = len(imseries)
        self.date_format = "%a %b %d %H:%M:%S.%f %Y"
    
        self.kinfunctions = ['integrate']

    
    def obtain_t(self):
        self.tarr = np.zeros(self.kinlength)
        for i in range(self.kinlength):
            self.tarr[i] = datetime.strptime(self.kinseries[i].metadata['Date and Time'], self.date_format)
