#!/usr/bin/python
import logging

from numpy import pi, sqrt, exp, square, mean, linspace
from numpy.random import normal

from saving import Loader

class Plotter(Loader):
    def __init__(self):
    	logging.basicConfig(level=logging.ERROR)
    	self.plotter_logger = logging.getLogger(__name__)

    def test_self(self):
        import pylab as p
        import numpy as np
        freq_f = 100000
        t = p.linspace(0, 1, 10**(6))
        A = p.zeros(10**(6))
        for i in xrange(len(t)):
            freq_f += 0.1*(p.random() - 0.5)
            A_f = 0.05 + (p.random()/2)*0.1
            A[i] = A_f*p.sin(t[i]*2*p.pi*freq_f)
        xpsd, ypsd = self.psd_ave([t, A])
        y_fit = self.func(xpsd,
                            alpha = 10**(8),
                            f0 = 100000,
                            damping = 200,
                            noise = 3*10**(-10))
        p.subplot(1, 2, 1)
        p.plot(t[:300], A[:300])
        p.subplot(1, 2, 2)
        p.semilogy(xpsd, ypsd)
        print(len(xpsd), len(y_fit))
        p.semilogy(xpsd, y_fit)
        p.xlim(0,200000)
        p.show()

    def checkdata(self, x, y, filename):
        if (len(x) == 0 or len(y) == 0) and len(filename) > 0:
            x, y = self.loaddata(filename)
        elif (len(x) == 0 or len(y) == 0) and len(filename) == 0:
            raise IOError("Missing data or filename")
        return x, y

    def psdplot(self, x=[], y=[], filename=""):
        from pylab import semilogy, show, xlabel, ylabel
        from numpy.random import randint
        xpsd, ypsd = self.psddata(x, y, filename)
        semilogy(xpsd, ypsd)
    	xlabel(r'Trap Frequency (kHz)')
    	ylabel(r'Power Spectral Density $\mathregular{(V^2/\sqrt{Hz})}$')
        show(randint(100))
        return

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

    def psddata(self, x, y, filename=""):
        from time import time
        from scipy.signal import welch
        x, y = self.checkdata(x, y, filename)
        self.plotter_logger.info("Generating PSD data")
        starttime = time()
        dt = x[1] - x[0]
        df = 1/dt
        f, Pxx_den = welch(y, fs=df, nperseg=len(y), window="hanning")
        #total_power = 4*3.14*sum(Pxx_den)
        #print "Total power: %s" %str(total_power)
        #print "Average Energy: %s" %str(total_power/df)
        self.plotter_logger.info("PSD data generated in %i seconds"
                                % (time()-starttime))
        return f, abs(Pxx_den)

    def func(self, x, alpha, f0, damping, noise=10**(-12), feedback=0):
        top = alpha*damping
        bottom = (f0**2 - x**2)**2 + (x**(2))*(damping + feedback)**2
        return top/bottom# + noise

    def sum_of_squares(self, x, y, parms):
        model = func(x, *parms)
        return sum(square(model/y - y/model))

    def fit(self, x, y, alpha, f0, damping, feedback=0, noise=10**(-12)):
        from scipy import optimize
        if feedback == 0 :
            init_guess = [alpha, f0, damping]
            bounds = [(10**(4), 10**(8)),
                        (f0/10, f0*10),
                        (0.1, 100)]

            self.plotter_logger.info("Without feedback")
            best_parms = self.full_solve(x, y, init_guess, bounds)
            print(best_parms)
        else:
            self.plotter_logger.info("With feedback")

        return best_parms

    def scatter_fit_errors(self, ret):
        plt.plot(ret.x, ret.fit_data, color='red')
        plt.fill_between(ret.x,
                        ret.fit_data + ret.fit_data_std,
                        ret.fit_data - ret.fit_data_std,
                        facecolor= "red",
                        alpha = 0.5)

        label = "%0.1f +/- %0.1f" %(ret.m, ret.m_std)
        plt.errorbar(ret.x,
                    ret.y,
                    yerr = ret.y_std,
                    xerr = ret.x_std
                    fmt = 'o',
                    label = label)


""" Create one instance and export its methods as module-level functions.
 This is with debug_on = True but for alot of things this is ok and can
 be changed by running myplots._inst.__init__(False)
 """

_inst = Plotter()
checkdata = _inst.checkdata
psdplot = _inst.psdplot
psddata = _inst.psddata
psd_ave = _inst.psd_ave
func = _inst.func
fit = _inst.fit
test_self = _inst.test_self

# 	def histplot(filename,data=None,nobins=100,maxx=300):
# 		print "generating histagram"
# 		if data == None:
# 			x,y = loaddata(filename,maxx)
# 		pl.hist(y,bins=100)
# 		pl.xlabel('Voltage')
# 		pl.ylabel('Counts')
# 		imagefile=filename[:-4]+"hist.pdf"
# 		pl.savefig(imagefile)
