import datetime

import matplotlib.pyplot as plt

import saving
import process
import myplots

class Data(object):
    def __init__(self, filename, pressure=1e-5, feedback = False):
        self.filename = filename
        self.loader = saving.Loader()
        self.processer = process.Processer()
        self.plotter = myplots.Plotter()
        self.x, self.y = self.loader.load_data(self.filename)
        self.fs = len(self.x)/(2*self.x[-1])
        self.pressure = pressure
        self.feedback = feedback
        self._creation_time = datetime.datetime.now()
        self.xpsd = []
        self.ypsd = []
        self.centers = dict()
        self.cuts = dict()
        self.fit_parms = dict()
        self.fit_errors = dict()
        self.fit_data = dict()
        self.noise = 1e-12

    def psd(self):
        self.xpsd, self.ypsd = self.processer.psd(self.x, self.y, self.fs)

    def peak_cuts(self, bandwidth = 10000):
        cuts = dict()
        for key, center in self.centers.iteritems():
            self.cuts[key] = self.processer.cut_peak(self.centers[key],
                                                    self.xpsd,
                                                    self.ypsd,
                                                    bandwidth)

    def fit_to_psd(self):
        if len(self.cuts) == 0:
            self.peak_cuts()
        self.processer.pressure = self.pressure
        self.processer.noise = self.noise
        for key, center in self.centers.iteritems():
            self.fit_parms[key], self.fit_errors[key] = \
                    self.processer.psd_fit(
                                    xdata = self.cuts[key][0],
                                    ydata = self.cuts[key][1],
                                    freq_center = self.centers[key],
                                    feedback = self.feedback,
                                    mbar_fit_parms = self.fit_parms)
            self.fit_data[key] = self.processer.model(self.cuts[key][0],
                                                        *self.fit_parms[key])

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

    def filter(self, key = 'z'):
        f, r = self.processer.butterworth_filter(self.y,
                                        lowcut = self.centers[key] - 10000,
                                        highcut = self.centers[key] + 10000,
                                        fs = self.fs)
        self.filtered[key] = f
        self.filter_response[key] = r

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
