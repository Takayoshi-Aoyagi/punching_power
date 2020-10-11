import datetime

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np


class Plotter:
    
    @classmethod
    def plot(cls, t, y):
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))
        plt.plot(t, y)
        plt.gcf().autofmt_xdate()
        #plt.show()
        return fig
        
