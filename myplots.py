#!/usr/bin/python
import logging
from time import time

import numpy as np
import matplotlib.pyplot as plt

from process import Processer

class Plotter(Processer):
    def __init__(self, level='DEBUG'):
        self.logger = logging.getLogger("Myplots")
        try:
            level_value = eval('logging.%s' %level.upper())
        except AttributeError:
            print('Logging level not found, default to DEBUG')
            level_value = logging.DEBUG
        self.logger.setLevel(level_value)

    	# create the logging file handler
    	sh = logging.StreamHandler()
    	format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    	formatter = logging.Formatter(format_string)
    	sh.setFormatter(formatter)
    	self.logger.setLevel(level_value)
    	self.logger.addHandler(sh)

    def psd_plot(self, psd_data):
        plt.figure('PSD data for %s' %psd_data.filename)
        plt.semilogy(psd_data.xpsd/1000, psd_data.ypsd)
        plt.xlim(0, 300)
    	plt.xlabel(r'Trap Frequency (kHz)')
    	plt.ylabel(r'Power Spectral Density $\mathregular{(V^2/\sqrt{Hz})}$')
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

    def psd_with_fit(self, psd_data):
        def taylor_damping(r):
            d = 364e-12
            viscosity = 18.6e-6
            density = 2650
            kb = 1.38e-23
            top = 0.619*9*np.pi*viscosity*d**2
            bottom = np.sqrt(2)*density*kb*300
            return (self.pressure*top)/(r*bottom)

        def model_psd(x, r, w0, gamma, feedback = 0, deltaw0 = 0):
            w0 = w0*2*np.pi
            x = x*2*np.pi
            deltaw0 = deltaw0*2*np.pi
            mass = 2650*(4./3)*np.pi*r**3
            damping = taylor_damping(r)
            top = 1.38*10**-(23)*300*damping/(np.pi*mass)
            bottom = ((w0 + deltaw0)**2 - x**2)**2 + (x*(damping + feedback))**2
            return gamma**2*top/bottom + self.noise

        self.pressure = psd_data.pressure*100
        self.noise = psd_data.noise
        plt.figure('PSD with fits for %s' %psd_data.filename)
        for key in psd_data.fit_parms.keys():
            xpsd = psd_data.xpsd[psd_data.cuts[key]]
            plt.semilogy(xpsd/1000, psd_data.ypsd[psd_data.cuts[key]])
            ypsd_fit = model_psd(xpsd, *psd_data.fit_parms[key])
            plt.semilogy(xpsd/1000, ypsd_fit, label=key)
        plt.xlim(0, 300)
    	plt.xlabel(r'Trap Frequency (kHz)')
    	plt.ylabel(r'Power Spectral Density $\mathregular{(V^2/\sqrt{Hz})}$')
        return

    def scatter_fit_errors(self, ret):
        plt.figure('Scatter with errors')
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
                    xerr = ret.x_std,
                    fmt = 'o',
                    label = label)

    def hist2d(self, x, y, res=100, sigma=1.5):
        from scipy.ndimage.filters import gaussian_filter
        start_time = time()
        x_max, x_min = max(x), min(x)
        y_max, y_min = max(y), min(y)
        xx = linspace(x_min, x_max, res)
        yy = linspace(y_min, y_max, res)
        zz = zeros((res, res))
        for xx_index in range(res-1):
            n_list = []
            for n,i in enumerate(x):
                if i >= xx[xx_index] and i <= xx[xx_index + 1]:
                    n_list.append(n)
            n_list = list(set(n_list))
            y_values = [y[i] for i in n_list]
            for ii in range(len(y_values)-1):
                for n,i in enumerate(yy):
                    if i >= y_values[ii] and i <= y_values[ii + 1]:
                        zz[xx_index, n] += 1
        zz = gaussian_filter(zz, sigma)
        self.logger.info("2d hist generated in %i seconds"
                                % (time()-start_time))
        return xx, yy, zz

    # def filterplot():
    #     if verbosity == 1:
    #     fig1 = _plt.figure()
    #     ax = fig1.add_subplot(111)
    #     ax.plot(freqList, GainArray, '-', label="Specified Filter")
    #     ax.set_title("Frequency Response")
    #     if SampleFreq == 2*_np.pi:
    #         ax.set_xlabel(("$\Omega$ - Normalized frequency "
    #                        "($\pi$=Nyquist Frequency)"))
    #     else:
    #         ax.set_xlabel("frequency (Hz)")
    #     ax.set_ylabel("Gain (dB)")
    #     ax.set_xlim([0, SampleFreq/2.0])
    #     fig2 = _plt.figure()
    #     ax = fig2.add_subplot(111)
    #     ax.plot(freqList, PhaseDiffArray, '-', label="Specified Filter")
    #     ax.set_title("Phase Response")
    #     if SampleFreq == 2*_np.pi:
    #         ax.set_xlabel(("$\Omega$ - Normalized frequency "
    #                        "($\pi$=Nyquist Frequency)"))
    #     else:
    #         ax.set_xlabel("frequency (Hz)")
    #
    #     ax.set_ylabel("Phase Difference")
    #     ax.set_xlim([0, SampleFreq/2.0])
    #     _plt.show()

""" Create one instance and export its methods as module-level functions.
 This is with debug_on = True but for alot of things this is ok and can
 be changed by running myplots._inst.__init__(False)
 """

_inst = Plotter()
psd_plot = _inst.psd_plot
scatter_fit_errors = _inst.scatter_fit_errors
psd_ave = _inst.psd_ave
hist2d = _inst.hist2d
psd_with_fit = _inst.psd_with_fit
# 	def histplot(filename,data=None,nobins=100,maxx=300):
# 		print "generating histagram"
# 		if data == None:
# 			x,y = loaddata(filename,maxx)
# 		pl.hist(y,bins=100)
# 		pl.xlabel('Voltage')
# 		pl.ylabel('Counts')
# 		imagefile=filename[:-4]+"hist.pdf"
# 		pl.savefig(imagefile)

    # def test_self(self):
    #     import pylab as p
    #     import numpy as np
    #     freq_f = 100000
    #     t = p.linspace(0, 1, 10**(6))
    #     A = p.zeros(10**(6))
    #     for i in xrange(len(t)):
    #         freq_f += 0.1*(p.random() - 0.5)
    #         A_f = 0.05 + (p.random()/2)*0.1
    #         A[i] = A_f*p.sin(t[i]*2*p.pi*freq_f)
    #     xpsd, ypsd = self.psd_ave([t, A])
    #     y_fit = self.func(xpsd,
    #                         alpha = 10**(8),
    #                         f0 = 100000,
    #                         damping = 200,
    #                         noise = 3*10**(-10))
    #     p.subplot(1, 2, 1)
    #     p.plot(t[:300], A[:300])
    #     p.subplot(1, 2, 2)
    #     p.semilogy(xpsd, ypsd)
    #     print(len(xpsd), len(y_fit))
    #     p.semilogy(xpsd, y_fit)
    #     p.xlim(0,200000)
    #     p.show()
