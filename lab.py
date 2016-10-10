import saving
import myplots
import logging

class Data(object):
    def __init__(self):
        self.x = []
        self.y = []
        self.xpsd = []
        self.ypsd = []
        self._loader = saving.Loader()
        self._plotter = myplots.Plotter()

    def info_off(self):
        self._loader.saving_logger.setLevel("WARNING")

    def info_on(self):
        self._loader.saving_logger.setLevel("INFO")

    def load_time_data(self, filename):
        self.x, self.y = self._loader.loaddata(filename)

    def load_psd_data(self, filename=""):
        self.xpsd, self.ypsd = self._plotter.psddata(self.x, self.y, filename)


class Exp(object):
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self._exp_logger = logging.getLogger(__name__)
        self.data = Data()

    def info_off(self):
        self.data.info_off()

    def info_on(self):
        self.data.info_on()

    def psdplot(self, filename=""):
        from pylab import semilogy, show, xlabel, ylabel
        from numpy.random import randint
        if len(self.data.xpsd) == 0:
            self.data.load_psd_data(filename)
        semilogy(self.data.xpsd, self.data.ypsd)
    	xlabel(r'Trap Frequency (kHz)')
    	ylabel(r'Power Spectral Density $\mathregular{(V^2/\sqrt{Hz})}$')
        show(randint(100))
        return

exp = Exp()
