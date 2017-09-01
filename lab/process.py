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

    @classmethod
    def mov_ave(self, data, pnts=50):
        start_time = time()
        if (self.logger):
            self.logger.debug("Preforming moving average")
        cum = _np.cumsum(data, dtype=float)
        cum[n:] = cum[n:] - cum[:-n]
        ret = cum[n - 1:] / n
        end_time = time() - start_time
        if (self.logger):
            self.logger.debug(
                    "Moving average completed in {} seconds".format(end_time))
        return ret

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
        '''
        Generates a power spectrial density of the given time data

        Parameters
        ----------
        x : numpy array
            Time series data
        y : numpy array
            Amplitude for each time point
        fs : int
            sample frequency
        nperseg: int (optional)
            number of segments, how many frequencies to return.

        Returns
        -------
        xpsd : numpy array
            Frequency data
        ypsd : numpy array
            Amplitude data in units of m^2/Hz (or V^2/Hz if not converted)
        '''
        from scipy.signal import welch
        self.logger.debug("Generating PSD data")
        start_time = time()
        xpsd, ypsd = welch(y, fs = fs, nperseg = nperseg, window = "hanning")
        self.logger.debug("PSD data generated in %i seconds"
                                % (time()-start_time))
        return xpsd, ypsd

    def cut_peak(self, center, xpsd, ypsd, bandwidth = 40000):
        '''
        Returns data centered on the frequency peak.

        Parameters
        ----------

        center : Int
                Center frequency of the trap signal
        xpsd : numpy array
            Frequency data
        ypsd : numpy array
            Amplitude data
        bandwidth: Int (optional)
            Cut off bandwidth

        Returns
        -------
        xpsd : numpy array
            Truncated frequency data
        ypsd : numpy array
            Truncated amplitude data
        '''
        clause1 = (xpsd >= (center - bandwidth))
        clause2 = (xpsd <= (center + bandwidth))
        clause = clause1 * clause2
        cut_indexs = np.where(clause)[0]
        return xpsd[cut_indexs], ypsd[cut_indexs]

    def damping(self, r):
        '''
        Damping on the particle for a given pressure

        Parameters
        ----------
        r : float
            Particle radius in metres.
        self.pressure: float
            Defined at object creation and is an interal parameter. This is to
            prevent it becoming a fit parameter but accident.

        Outputs
        -------
        gamma_0 : float
                The damping from air collitions in the particle at that pressure
        '''
        kb = 1.38e-23 # boltzmann constant
        d = 364e-12 # diameter of the gas particles
        Kn = (kb*300)/(r*np.sqrt(2)*np.pi*d**2*self.pressure*100) # Knudsen number
        viscosity = 18.6e-6
        mass = 2650*(4./3)*np.pi*r**3
        left = (6*np.pi*viscosity*r)/(mass)
        center = 0.619/(0.619+Kn)
        right = 1+((0.31*Kn)/(0.785+1.152*Kn+Kn**2))
        return left*center*right

    def model(self, x, r, w0, gamma, feedback = 0, deltaw0 = 0, *args):
        '''
        Model of the particles PSD peak for a given frequency. Refer to paper
        for more details.

        Parameters
        ----------
        x : float/int
            Single frequency
        r : float
            Particle radius
        w0 : float/int
            Centre/natural frequnecy of the oscillator
        gamma : float/int
            Conversion factor to go from V/Hz to m/Hz

        Outputs
        -------
        Amplitude : float
            The particles Amplitude (in units of m^2/Hz)
        '''
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


    def psd_fit(self, x, y, freq_center, pressure, noise,
                ref_parms = [], ref_errors = [], feedback=False):
        '''
        This method is used to fit the "model" method to experimental data. This
        data be done stand alone but it is recommended to use the Data object class.

        To fit data with feedback on, previous fit data without feedback is needed
        to obtain gamma and radius.

        Parameters
        ----------
        x : numpy array
            Frequency data to fit to.
        y : numpy array
            Amplitude data to fit to.
        freq_center : float/int
            Centre/natural frequnecy of the oscillator for that degree of freedom.
        pressure : float/int
            Pressure inside the chamber
        noise: float
            Noise floor of detection system.
        ref_parms : array like
            Fit Parameters from mbar fit.
        ref_errors : array like
            Errors from previous fits, using to propigate errors.
        feedback : boolean
            Is feedback on or off.

        Outputs
        -------
        fit_parms : list
            Fit Parameters.
        fit_errors
            Fit errors.
        '''
        def model_feedback(x, feedback, deltaw0):
            return self.model(x,
                            self.r,
                            self.w0,
                            self.gamma,
                            feedback,
                            deltaw0)

        def fitting_with_feedback(x, y, ref_parms, ref_errors):
            '''
                Use fit data from a previous fit to find feedback numbers
            '''
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

    def psd_ave(self, data, chucks=100):
        '''
        Takes time data, chucks it, takes a PSD of each chuck, and then averages
        to chucks together.

        Parameters
        ----------
        data : 2d array
            [0] is time data and [1] is amplitude data.
        chucks: int (optional)
            The number of chucks to break the data down into.

        Returns
        -------
        xpsd : numpy array
            Averaged frequency data
        ypsd : numpy array
            Averaged amplitude data
        '''
        n = len(data[0])/chucks
        data_sets = [data[1][i:i+n] for i in range(0, len(data[1]), n)][:-1]
        time_sets = [data[0][i:i+n] for i in range(0, len(data[0]), n)][:-1]
        xpsd, ypsd = self.psddata(time_sets[0], data_sets[0])
        for i in xrange(len(data_sets)):
            t_xpsd, t_ypsd = self.psddata(time_sets[i], data_sets[i])
            ypsd += t_ypsd
        ypsd /= len(data_sets)
        return xpsd, ypsd

    def phase_space(self, y, r, fs, gamma=1e5):
        '''
        Produces phase-space data with the amplitude data.

        Parameters
        ----------
        y : array like
            Time amplitude data in units of Volts
        r : float
            Particle radius, for mass
        fs : float/int
            Sample frequency to abtain particle velocity
        gamma : int
            Conversion contant to change Volts into metres
        '''
        start_time = time()
        momentum = []
        # scale = 10**9
        scale = 1
        position = scale*(y)/gamma
        mass = 2500*(4/3)*np.pi*(r*scale)**3
        for i in range(len(position)-1):
            momentum.append(fs*(position[i+1]-position[i])*mass)
        self.logger.debug("Phase space data generated in %i seconds"
                                % (time()-start_time))
        return np.array(position[:-1]), np.array(momentum)
