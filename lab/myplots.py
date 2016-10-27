#!/usr/bin/python
from time import time

import numpy as np
import matplotlib.pyplot as plt

class Plotter(object):
    def __init__(self, level='DEBUG'):
        pass

    def plot_psd(self, xpsd, ypsd, fig_name = 'PSD data'):
        plt.figure(fig_name)
        plt.semilogy(xpsd/1000, ypsd)
        plt.xlim(0, 300)
    	plt.xlabel(r'Trap Frequency (kHz)')
    	plt.ylabel(r'Power Spectral Density $\mathregular{(V^2/\sqrt{Hz})}$')
        return

    def psd_with_fit(self):
        def taylor_damping(r):
            d = 364e-12
            viscosity = 18.6e-6
            density = 2650
            kb = 1.38e-23
            top = 0.619*9*np.pi*viscosity*d**2
            bottom = np.sqrt(2)*density*kb*300
            return (self.pressure*100*top)/(r*bottom)

        def model_psd(x, r, w0, gamma, feedback = 0, deltaw0 = 0):
            w0 = w0*2*np.pi
            x = x*2*np.pi
            deltaw0 = deltaw0*2*np.pi
            mass = 2650*(4./3)*np.pi*r**3
            damping = taylor_damping(r)
            top = 1.38*10**-(23)*300*damping/(np.pi*mass)
            bottom = ((w0 + deltaw0)**2 - x**2)**2 + (x*(damping + feedback))**2
            return gamma**2*top/bottom + self.noise

        plt.figure('PSD with fits for %s' %self.filename)
        for key in self.fit_parms.keys():
            xpsd = self.cuts[key][0]
            plt.semilogy(self.cuts[key][0]/1000, self.cuts[key][1])
            ypsd_fit = model_psd(self.cuts[key][0], *self.fit_parms[key])
            plt.semilogy(self.cuts[key][0]/1000, ypsd_fit, label=key)
        plt.xlim(0, 300)
    	plt.xlabel(r'Trap Frequency (kHz)')
    	plt.ylabel(r'Power Spectral Density $\mathregular{(V^2/\sqrt{Hz})}$')
        plt.show()
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

"""
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
"""
