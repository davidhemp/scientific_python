import logging
from collections import namedtuple
from time import time

import numpy as np
from scipy.signal import butter, lfilter, freqz
from scipy.optimize import basinhopping, curve_fit

from data_sets import PSDData
#saving.logger.setLevel(logging.INFO)

class Processer(object):
    def __init__(self, level="ERROR"):
        self.logger = logging.getLogger("Processing")
        try:
            level_value = eval('logging.%s' %level.upper())
        except AttributeError:
            level_value = logging.ERROR
            print('Logging level not found, default to DEBUG')
        self.logger.setLevel(level_value)

        # create the logging file handler
        sh = logging.StreamHandler()
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(format_string)
        sh.setFormatter(formatter)
        self.logger.setLevel(level_value)
        self.logger.addHandler(sh)


    def rms(self, y):
        return np.sqrt(np.mean(np.square(y)))

    def butterworth_filter(self, time_data, lowcut=0, highcut=1,
                            btype = 'band', order=5):

        def butter_b_a(lowcut, highcut, fs, order=5, btype='band'):
            nyq = 0.5 * fs
            low = lowcut / nyq
            high = highcut / nyq
            if btype.lower() == 'band':
                b, a = butter(order, [low, high], btype = btype)
            elif btype.lower() == 'low':
                b, a = butter(order, low, btype = btype)
            elif btype.lower() == 'high':
                b, a = butter(order, high, btype = btype)
            else:
                raise ValueError('Filter type unknown')
            return b, a

        def get_filter_response(b, a, sample_freq=(2*np.pi), no_freq=500):
            """
            This function takes an array of coefficients and finds the
            frequency response of the filter using scipy.signal.freqz.
            Verbosity sets if the response should be plotted

            Parameters
            ----------
                b, a : ndarray, ndarray
                    Numerator and denominator in the z transfer array
                sample_freq : float
                    Sample frequency (in Hz) to simulate (used to convert
                     frequency range to normalised frequency range)
                no_freq : int
                    Number of frequencies to use to simulate the frequency and
                     phase response of the filter. Default is 500.
            Returns
            -------
            freqs : ndarray
                Array containing the frequencies at which the gain is
                 calculated
            freq_response : ndarray
                Array containing the gain in dB of the filter when simulated
                (20*log_10(A_out/A_in))
            phase_response: ndarray
                Array containing the phase response of the filter in radians
            """
            w, h = freqz(b=b, a=a, worN=no_freq)
            freqs = w/(np.pi)*sample_freq/2.0
            himag = np.array([hi.imag for hi in h])
            freq_response = 20*np.log10(np.abs(h))
            phase_response = np.unwrap(np.arctan2(np.imag(h), np.real(h)))
            return freqs, freq_response, phase_response

        self.logger.debug('Filtering data')
        start_time = time()
        b, a =  butter_b_a(lowcut, highcut, time_data.fs,
                            order = order, btype = btype)
        time_data.filter_response = get_filter_response(
                                                    a=a,
                                                    b=b,
                                                    sample_freq=time_data.fs)
        filtered = lfilter(b, a, time_data.y)
        self.logger.debug("Data filtered in %i seconds" % (time()-start_time))
        return filtered

    def psd(self, x, y, fs, filename="", key=0):
        from scipy.signal import welch
        # self.logger.debug("Generating PSD data")
        start_time = time()
        f, Pxx_den = welch(y,
                        fs = fs,
                        nperseg = 1000000,
                        window = "hanning")
        # self.logger.debug("PSD data generated in %i seconds"
                                # % (time()-start_time))
        return f, Pxx_den

    def peak_cuts(self, psd_data, bandwidth = 10000):
        cuts = dict()
        for key, center in psd_data.centers.iteritems():
            clause1 = psd_data.xpsd >= (center - bandwidth)
            clause2 = psd_data.xpsd <= (center + bandwidth)
            clause = clause1 * clause2
            cuts[key] = np.where(clause)[0]
        return cuts

    def phase_space(self, x, y, trap_freq, fs, gamma = 1e5, offset = 0):
        start_time = time()
        momentum = []
        scale = 10**9
        position = scale*(y + offset)/gamma
        for i in range(len(position)-1):
            momentum.append(fs*(position[i+1]-position[i])/(trap_freq*2*np.pi))
        self.logger.debug("Phase space data generated in %i seconds"
                                % (time()-start_time))
        return position[:-1], momentum

    def psd_fit(self, psd_data, feedback = False):
        def taylor_damping(r):
            d = 364e-12
            viscosity = 18.6e-6
            density = 2650
            kb = 1.38e-23
            top = 0.619*9*np.pi*viscosity*d**2
            bottom = np.sqrt(2)*density*kb*300
            return (self.pressure*top)/(r*bottom)

        def model(x, r, w0, gamma, feedback = 0, deltaw0 = 0):
            w0 = w0*2*np.pi
            x = x*2*np.pi
            deltaw0 = deltaw0*2*np.pi
            mass = 2650*(4./3)*np.pi*r**3
            damping = taylor_damping(r)
            top = 1.38*10**-(23)*300*damping/(np.pi*mass)
            w = w0 + deltaw0
            feedback_g = damping + feedback
            bottom = ((w)**2 - x**2)**2 + (x*(feedback_g))**2
            return gamma**2*top/bottom + self.noise

        def model_feedback(x, feedback, deltaw0 = 1000):
            return model(x, self.r, self.w0, self.gamma, feedback, deltaw0)

        def fitting_with_feedback(psd_data, key,
                                    feedback = 0.11, deltaw0 = 1000):
            self.r, self.w0, self.gamma = psd_data.fit_parms[key][:3]
            p0 = [feedback]
            popt, pcov = curve_fit(model_feedback, self.xdata,
                                    self.ydata, p0 = p0)
            parms = [self.r, self.w0, self.gamma, popt[0]]
            return parms, pcov

        def fitting(f0 = 56399, r = 38*10**-9, gamma = 5*10e4):
            p0 = [r, f0, gamma]
            while True:
                popt, pcov = curve_fit(model,
                                        self.xdata,
                                        self.ydata,
                                        p0 = p0)
                if all(value > 0 for value in popt):
                    break
                else:
                    print('Negative fits')
            return popt, pcov

        self.pressure = psd_data.pressure*100
        self.noise = psd_data.noise
        fit_parms = dict()
        fit_errors = dict()
        for key, center in psd_data.centers.iteritems():
            self.xdata = psd_data.xpsd[psd_data.cuts[key]]
            self.ydata = psd_data.ypsd[psd_data.cuts[key]]
            if feedback:
                fit_parms[key], fit_errors[key] = \
                                        fitting_with_feedback(psd_data, key)
            else:
                fit_parms[key], fit_errors[key] = fitting(f0 = center)
        return fit_parms, fit_errors

_inst = Processer()
logger = _inst.logger
butterworth_filter = _inst.butterworth_filter
psd = _inst.psd
phase_space = _inst.phase_space
peak_cuts = _inst.peak_cuts
psd_fit = _inst.psd_fit
rms = _inst.rms

import saving

class EFieldDisplacement(object):
    def __init__(self, power = 0.5):
        POWER = power
        WAVELENGTH = 1550*10**(-9)
        NA = 0.9
        W_0 = WAVELENGTH / (2*NA)
        self.Z_RAY = (np.pi * W_0**2)/WAVELENGTH
        self.MAX_I0 = (2*0.4)/(np.pi*(W_0**2))
        N_INDEX = 1.54
        RADIUS = 100*10**(-9)
        DISTANCE = 3*10**(-2)
        c = 3.*10**(8)
        ratio = (N_INDEX - 1)/(N_INDEX + 2)
        self.ALPHA = ratio*(4.*np.pi*RADIUS**3)/(c)

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
            _rms = np.sqrt(np.mean(np.square(_data)))
            y_rms.append(np.mean(_rms))
            y_rms_std.append(np.std(_rms))

        y_rms_normalised = abs(np.array(y_rms)/y_rms[0] - 1)
        ret.y = 100*y_rms_normalised/0.05 #100mn/0.05V check this
        ret.y_std = 100*np.array(y_rms_std)/0.05

        if len(x) == 0:
            ret.x = np.arange(len(ret.y))
        else:
            ret.x = x
            ret.y = ret.y[:len(x)]
            ret.y_std = ret.y_std[:len(x)]

        ret.x_std = 0
        ret.m, ret.m_std = self.fit(ret.x, ret.y)
        fit_data = [self.position_master(i*1000, ret.m)*10**(9) for i in x]
        ret.fit_data = np.array(fit_data)
        ret.fit_data_std = ret.fit_data * ret.m_std/ret.m
        return ret

    def position_master(self, x, charge):
        q = charge*1.6*10**(-19)
        # I have no idea why the 8.0 is needed
        ret = 8.0*(8*q*self.Z_RAY**2)/(self.ALPHA*self.MAX_I0)
        return x*ret

    def fit(self, x, y_rms):
        charges = np.arange(0, 10, 0.1)
        y_rms = y_rms*10**(-9) #Remember y is kept in nm
        voltages = x * 1000
        ret = []
        for position, voltage in zip(y_rms, x):
            _ = []
            for charge in charges:
                diff = abs(position - self.position_master(voltage*1000, charge))
                _.append(diff)
            ret.append(charges[_.index(min(_))])
        return np.mean(ret), np.std(ret)
