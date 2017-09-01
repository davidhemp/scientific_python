import datetime

import saving
import process
np = process.np
import myplots
plt = myplots.plt

class Data(object):
    def __init__(self, filename, pressure=1e-5, feedback = False):
        self.filename = filename
        f_nopath = filename.split('/')[-1]
        self.loader = saving.Loader(logger_name = "Saving_" + f_nopath)
        self.processer = process.Processor(
                                    logger_name = "Processing_" + f_nopath)
        self.plotter = myplots.Plotter()
        self.x, self.y = self.loader.load_data(self.filename)
        self.fs = len(self.x)/(2*self.x[-1])
        self.pressure = pressure
        self.feedback = feedback
        self._creation_time = datetime.datetime.now()
        self.xpsd = []
        self.ypsd = []
        self.centers = dict()
        self.filtered = dict()
        self.filter_response = dict()
        self.filtered_psd = dict()
        self.phase_space = dict()
        self.cuts = dict()
        self.fit_parms = {'z':[], 'x':[], 'y':[]}
        self.fit_errors = {'z':[], 'x':[], 'y':[]}
        self.fit_data = dict()
        self.noise = dict()

    def psd(self):
        self.xpsd, self.ypsd = self.processer.psd(self.x, self.y, self.fs)

    def filter_time(self, key = 'z', bandwidth = 20000):
        f, r = self.processer.butterworth_filter(self.y,
                                        lowcut = self.centers[key] - bandwidth,
                                        highcut = self.centers[key] + bandwidth,
                                        fs = 1e6)
        self.filtered[key] = f
        self.filter_response[key] = r

    def psd_filtered(self, key='z'):
        xpsd, ypsd = self.processer.psd(self.x, self.filtered[key], 1e6)
        self.filtered_psd[key] = [xpsd, ypsd]

    def plot_filtered(self, key='z'):
        if 'z' not in self.filtered:
            self.filter_time(key=key)
        if 'z' not in self.filtered_psd:
            self.psd_filtered(key)
        self.plotter.filtered_plot(self.x, self.filtered[key],
                                   self.filtered_psd[key],
                                   self.filter_response[key])

    def peak_cuts(self, bandwidth = 12000):
        cuts = dict()
        for key, center in self.centers.iteritems():
            self.cuts[key] = self.processer.cut_peak(self.centers[key],
                                                    self.xpsd,
                                                    self.ypsd,
                                                    bandwidth)

    def fit_to_psd(self):
        if len(self.cuts) == 0:
            self.peak_cuts()
        for key, center in self.centers.iteritems():
            self.fit_parms[key], self.fit_errors[key] = \
                    self.processer.psd_fit(
                                x = self.cuts[key][0],
                                y = self.cuts[key][1],
                                freq_center = self.centers[key],
                                feedback = self.feedback,
                                ref_parms = list(self.fit_parms[key]),
                                ref_errors = list(self.fit_errors[key]),
                                pressure = self.pressure,
                                noise = self.noise[key])
            self.fit_data[key] = self.processer.model(self.cuts[key][0],
                                                        *self.fit_parms[key][:])
    def generate_model(self):
        for key in self.centers.iterkeys():
            self.processer.noise = self.noise[key]
            self.fit_data[key] = self.processer.model(self.cuts[key][0],
                                                    *self.fit_parms[key][:])

    def print_parms(self):
        units = ['Radius, nm', 'f0, Hz', 'conversion factor',
                    'feedback, radians/sec', 'deltaw0, radians/sec', 'temp, k']
        for key in self.fit_parms.iterkeys():
            fit_values = self.fit_parms[key]
            fit_errors = self.fit_errors[key]
            print(key)
            for value, error, unit in zip(fit_values, fit_errors, units):
                print("%0.3e +/- %0.3e %s" %(value, error, unit))

    def plot_psd(self):
        if len(self.xpsd) != 0 and len(self.ypsd) != 0:
            self.plotter.plot_psd(self.xpsd, self.ypsd,
                                fig_name = 'PSD data for %s' %self.filename)
            plt.show()
        else:
            raise ValueError('Missing xpsd/ypsd data')

    def plot_cuts(self):
        fig_name = ('PSD cuts for %s' %(self.filename))
        for cut in self.cuts.itervalues():
            self.plotter.plot_psd(cut[0], cut[1], fig_name = fig_name)

        plt.show()

    def plot_cuts_fits(self):
        fig_name = ('PSD cuts with fits for %s' %(self.filename))
        for key, cut in self.cuts.iteritems():
            self.plotter.plot_psd(cut[0], cut[1], fig_name = fig_name)
            self.plotter.plot_psd(cut[0], self.fit_data[key],
                                    fig_name = fig_name)
        plt.show()

    # def dual_plot(self):
    #     fig_name = ('PSD cuts with fits for %s' %(self.filename))
    #     for key, cut in self.cuts.iteritems():
    #         self.plotter.plot_psd(cut[0], cut[1],)
    #         self.plotter.plot_psd(cut[0], self.fit_data[key],
    #                                 fig_name = fig_name)
    #     plt.show()
    #

    def get_phase_space(self, key='z'):

        gamma = self.fit_parms[key][2]
        trap_freq = self.centers[key]
        y = self.filtered[key]
        p, m = self.processer.phase_space(self.filtered[key],     # y
                                          self.fit_parms[key][0], # r
                                          self.fs,                # fs
                                          self.fit_parms[key][2]) # gamma
        self.phase_space[key] = [p, m]

    def plot_phase_space(self, key='z'):
        self.plotter.phase_space(*self.phase_space[key])

    def __repr__(self):
        """Convert to formal string, for repr()."""
        time_string = datetime.datetime.isoformat(self._creation_time)
        s = "<TimeDate object>'%s'%s" %(self.filename, time_string)
        return s

    def __str__(self):
        "Convert to string, for str()."
        time_string = datetime.datetime.isoformat(self._creation_time)
        s = "<TimeDate object> of '%s' created %s" %(
                                        self.filename, time_string)
        return s
