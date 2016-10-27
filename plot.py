import os

import matplotlib.pyplot as plt

import process
import myplots
import saving
from data_sets import TimeData

def plot(filename, pressure=300, centers={'z':76095}, noise=4*10**(-14)):
    path = os.getcwd()
    time_data = saving.load_data(filename)
    time_data.pressure, time_data.centers = pressure, {'z':76095}

    psd_data = process.psd(time_data)
    psd_data.centers, psd_data.noise = centers, noise
    psd_data.cuts = process.peak_cuts(psd_data)
    psd_data.fit_parms, psd_data.fit_errors = process.psd_fit(psd_data)
    myplots.psd_with_fit(psd_data)

    time_data = process.butterworth_filter(time_data,
                                            time_data.centers['z'],
                                            bandwidth = 20000)
    position, momentum = process.phase_space(time_data, time_data.centers['z'])
    plt.figure('Position')
    plt.plot(position, momentum)
    plt.show()
