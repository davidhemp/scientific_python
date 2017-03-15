import logging
from collections import namedtuple
from time import time

import numpy as np
from scipy.signal import butter, lfilter, freqz, filtfilt
from scipy.optimize import basinhopping, curve_fit

#saving.logger.setLevel(logging.INFO)

class Processor(object):
    def __init__(self, level="DEBUG", logger_name = "Processing"):
        self.logger = logging.getLogger(logger_name)
        try:
            level_value = eval('logging.%s' %level.upper())
        except AttributeError:
            level_value = logging.DEBUG
            print('Logging level not found, default to DEBUG')
        self.logger.setLevel(level_value)

        # create the logging file handler
        sh = logging.StreamHandler()
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(format_string)
        sh.setFormatter(formatter)
        self.logger.setLevel(level_value)
        self.logger.addHandler(sh)

    @classmethod
    def rms(y):
        return np.sqrt(np.mean(np.square(y)))

    def mov_ave(self, data, pnts=50):
        rtn = []
        self.logger.debug("Preforming moving average")
        for i in range(0, len(data)-pnts):
            rtn.append(np.mean(data[i:i+pnts]))
        self.logger.debug("Moving average completed in %i seconds")
        return np.array(rtn)

    def butterworth_filter(self, y, fs, lowcut=0, highcut=1,
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
        b, a =  butter_b_a(lowcut, highcut, fs, order = order, btype = btype)
        response = get_filter_response(a = a, b = b, sample_freq = fs)
        # filtered = lfilter(b, a, y)
        filtered = filtfilt(b, a, y)
        self.logger.debug("Data filtered in %i seconds" % (time()-start_time))
        return filtered, response

    def psd(self, x, y, fs, nperseg = 1e6):
        from scipy.signal import welch
        self.logger.debug("Generating PSD data")
        start_time = time()
        xpsd, ypsd = welch(y, fs = fs, nperseg = nperseg, window = "hanning")
        self.logger.debug("PSD data generated in %i seconds"
                                % (time()-start_time))
        return xpsd, ypsd

    def cut_peak(self, center, xpsd, ypsd, bandwidth = 40000):
        clause1 = (xpsd >= (center - bandwidth))
        clause2 = (xpsd <= (center + bandwidth))
        clause = clause1 * clause2
        cut_indexs = np.where(clause)[0]
        return xpsd[cut_indexs], ypsd[cut_indexs]

    def taylor_damping(self, r):
        d = 364e-12
        viscosity = 18.6e-6
        density = 2650
        kb = 1.38e-23
        top = 0.619*9*np.pi*viscosity*d**2
        bottom = np.sqrt(2)*density*kb*300
        return (self.pressure*100*top)/(r*bottom)

    def damping(self, r):
        kb = 1.38e-23
        d = 364e-12
        L = 1e-6
        Kn = (kb*300)/(L*np.sqrt(2)*np.pi*d**2*self.pressure*100)
        viscosity = 18.6e-6
        mass = 2650*(4./3)*np.pi*r**3
        left = (6*np.pi*viscosity*r)/(mass)
        center = 0.619/(0.619+Kn)
        right = (0.31*Kn)/(0.785+1.152*Kn+Kn**2)
        return left*center*right

    def model(self, x, r, w0, gamma, feedback = 0, deltaw0 = 0, *args):
        if r<0 or w0<0 or gamma<0 or feedback<0:
            return x*1e9
        w0 = w0*2*np.pi
        x = x*2*np.pi
        deltaw0 = deltaw0*2*np.pi
        mass = 2650*(4./3)*np.pi*r**3
        damping = self.damping(r)
        left = 1.38*10**-(23)*300/(np.pi*mass)
        right_top = damping
        w = w0 + deltaw0
        feedback_g = damping + feedback
        right_bottom = ((w)**2 - x**2)**2 + (x*(feedback_g))**2
        right = right_top/right_bottom
        return gamma**2*left*right/(2*np.pi)**3 + self.noise

    def imp_model(self, x, w0, damping, feedback=0, noise = 1e-12):
        if w0<0 or feedback<1:
            return x*1e9
        mass = 2650*(4./3)*np.pi*self.r**3
        constant = 1.38*10**-(23)*300/(np.pi*mass)
        top = self.gamma*(constant*damping)
        bottom = (w0**2-x**2)**2+(damping+feedback)**2*x**2
        return top/bottom+noise

    def psd_fit(self, x, y, freq_center, pressure, noise,
                ref_parms = [], ref_errors = [], feedback=False):

        def model_feedback(x, feedback, deltaw0):
            return self.model(x, self.r, self.w0, self.gamma,
                            feedback, deltaw0)

        def fitting_with_feedback(x, y,
                                    ref_parms, ref_errors):
            self.r, self.w0, self.gamma = ref_parms[:3]
            if len(ref_parms) == 5:
                feedback = ref_parms[3]
                deltaw0 = ref_parms[4]
            else:
                feedback = 1
                deltaw0 = 1000
            p0 = [feedback, deltaw0]
            popt, pcov = curve_fit(model_feedback, x, y, p0 = p0)
            gamma0 = self.damping(self.r)
            T = 300*gamma0/(gamma0 + popt[0])
            parms = [self.r, self.w0, self.gamma, popt[0], popt[1], T]
            if type(pcov) == type(0.1):
                return parms, ref_errors + [1e10, 1e10, 1e10]
            errors = list(np.sqrt(np.absolute(np.diag(pcov))))
            error_r = np.square(ref_errors[0]/ref_parms[0])
            error_feedback = np.square(errors[0]/popt[0])
            error_T = np.sqrt(2*0.3**2 + error_r + error_feedback)*T
            errors.append(error_T)
            return parms, ref_errors + errors

        def fitting(x, y, f0):
            r = 100e-9
            gamma = 1e5
            p0 = [r, f0, gamma]
            n = 5
            while True:
                popt, pcov = curve_fit(self.model, x, y, p0 = p0)
                if all(i>0 for i in popt):
                    break
                else:
                    logger.error('Negative fit parms: %i trys left' %n)
                    n-=0
                    if n <= 0:
                        raise ValueError('Negative values used')
            errors = np.sqrt(np.absolute(np.diag(pcov)))
            return popt, errors

        self.noise = noise
        self.pressure = pressure
        if feedback:
            fit_parms, fit_errors = fitting_with_feedback( x,
                                                            y,
                                                            ref_parms,
                                                            ref_errors)
        else:
            fit_parms, fit_errors = fitting(x, y, freq_center)
        return list(fit_parms), list(fit_errors)

    def psd_ave(self, data, chucks=100, filename=""):
        n = len(data[0])/chucks
        data_sets = [data[1][i:i+n] for i in range(0, len(data[1]), n)][:-1]
        time_sets = [data[0][i:i+n] for i in range(0, len(data[0]), n)][:-1]
        xpsd, ypsd = self.psddata(time_sets[0], data_sets[0])
        for i in xrange(len(data_sets)):
            t_xpsd, t_ypsd = self.psddata(time_sets[i], data_sets[i])
            ypsd += t_ypsd
        ypsd /= len(data_sets)
        return xpsd, ypsd

    def phase_space(self, x, y, trap_freq, fs, gamma=1e5):
        start_time = time()
        momentum = []
        scale = 10**9
        position = scale*(y)/gamma
        for i in range(len(position)-1):
            momentum.append(fs*(position[i+1]-position[i])/(trap_freq*2*np.pi))
        self.logger.debug("Phase space data generated in %i seconds"
                                % (time()-start_time))
        return np.array(position[:-1]), np.array(momentum)


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
