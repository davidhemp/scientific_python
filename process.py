import logging
from collections import namedtuple

import numpy as n
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt

import saving
saving.logger.setLevel(logging.ERROR)


def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

class EFieldDisplacement(object):
    def __init__(self, power = 0.5):
        POWER = power
        WAVELENGTH = 1550*10**(-9)
        NA = 0.9
        W_0 = WAVELENGTH / (2*NA)
        self.Z_RAY = (n.pi * W_0**2)/WAVELENGTH
        self.MAX_I0 = (2*0.4)/(n.pi*(W_0**2))
        N_INDEX = 1.54
        RADIUS = 100*10**(-9)
        DISTANCE = 3*10**(-2)
        c = 3.*10**(8)
        ratio = (N_INDEX - 1)/(N_INDEX + 2)
        self.ALPHA = ratio*(4.*n.pi*RADIUS**3)/(c)

    def run_process(self, filelist, label="", x = [], plot=True):
        ret = namedtuple('processed', ['m',
                                        'm_std',
                                        'x',
                                        'x_std'
                                        'y',
                                        'y_std',
                                        'fit_data',
                                        'fit_data_std'])
        y_rms = []
        y_rms_std = []
        for pointlist in filelist:
            _data = []
            for filename in pointlist:
                data = saving.load_data(filename)
                if len(data.x) > 0 :
                    _data.append(data.y)
            _rms = n.sqrt(n.mean(n.square(_data)))
            y_rms.append(n.mean(_rms))
            y_rms_std.append(n.std(_rms))

        y_rms_normalised = abs(n.array(y_rms)/y_rms[0] - 1)
        ret.y = 100*y_rms_normalised/0.05 #100mn/0.05V check this
        ret.y_std = 100*n.array(y_rms_std)/0.05

        if len(x) == 0:
            ret.x = n.arange(len(ret.y))
        else:
            ret.x = x
            ret.y = ret.y[:len(x)]
            ret.y_std = ret.y_std[:len(x)]

        ret.x_std = 0
        ret.m, ret.m_std = self.fit(ret.x, ret.y)
        fit_data = [self.position_master(i*1000, ret.m)*10**(9) for i in x]
        ret.fit_data = n.array(fit_data)
        ret.fit_data_std = ret.fit_data * ret.m_std/ret.m

    def position_master(self, x, charge):
        q = charge*1.6*10**(-19)
        # I have no idea why the 8.0 is needed
        ret = 8.0*(8*q*self.Z_RAY**2)/(self.ALPHA*self.MAX_I0)
        return x*ret

    def fit(self, x, y_rms):
        charges = n.arange(0, 10, 0.1)
        y_rms = y_rms*10**(-9) #Remember y is kept in nm
        voltages = x * 1000
        ret = []
        for position, voltage in zip(y_rms, x):
            _ = []
            for charge in charges:
                diff = abs(position - self.position_master(voltage*1000, charge))
                _.append(diff)
            ret.append(charges[_.index(min(_))])
        return n.mean(ret), n.std(ret)
