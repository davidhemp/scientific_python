#!/usr/bin/python
import matplotlib.pyplot as plt

class Plotter(object):
    def __init__(self, level='DEBUG'):
        pass

    def plot_psd(self, xpsd, ypsd, fig_name = 'PSD data', args=''):
        '''
        Plot of z,x,y peaks.

        Parameters
        ----------
        xpsd : array of floats
            Frequnecy data, assumed to be in Hz
        ypsd : array of floats
            Amplitude data.
        fig_name : string (optional)
            Figure name
        args : string/list
            Additional arguments to pass to matplotlib

        Return
        ------
            True
        '''
        plt.figure(fig_name)
        plt.semilogy(xpsd/1000, ypsd, args)
        plt.xlim(0, 300)
        plt.ylim(1e-14, 1e-4)
    	plt.xlabel(r'Trap Frequency (kHz)')
    	plt.ylabel(r'Power Spectral Density $\mathregular{(V^2/Hz)}$')
        return

    def psd_with_fit(self):
        '''
        Designed to work with the Data class to plot the PSD and the fits
        '''
        def taylor_damping(r):
            d = 364e-12
            viscosity = 18.6e-6
            density = 2650
            kb = 1.38e-23
            top = 0.619*9*3.14*viscosity*d**2
            bottom = 3.14*density*kb*300*2**(0.5)
            return (self.pressure*100*top)/(r*bottom)

        def model_psd(x, r, w0, gamma, feedback = 0, deltaw0 = 0):
            w0 = w0*2*3.14
            x = x*2*3.14
            deltaw0 = deltaw0*2*3.14
            mass = 2650*(4./3)*3.14*r**3
            damping = taylor_damping(r)
            top = 1.38*10**-(23)*300*damping/(3.14*mass)
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
        # plt.show()
        return

    def phase_space(self, x, y):
        '''
        Simple 2d scatter plots of phase space

        Parameters
        ----------
        x : array of floats
            Position data
        y : array of floats
            Momentum data (although often in units of position)

        Returns
        -------
            True
        '''
        plt.plot(x[1000::10], y[1000::10], 'x')
        plt.xlim(-1000, 1000)
        plt.ylim(-1000, 1000)
    	plt.xlabel('Position, nm')
    	plt.ylabel('Momentum, nm')
        plt.show()

    def filtered_plot(self, x, filtered, filtered_psd, filter_response):
        '''
        Plots 1) the filted time data, 2) the filter response, and 3) the PSD after filtering

        Parameters
        ----------
        x : array
            Time series data
        filtered : array
            Filtered time data
        Filtered_psd : 2d array
            Filtered PSD data, [0] is frequency and [1] is amplitude
        filter_response: 2d array
            Filter response, [0] is frequency and [1] is amplitude reduction.

        Returns
        -------
            True
        '''
        fig, ax = plt.subplots(1,3)
        ax[0].plot(x[1000:2000], filtered[1000:2000])
        ax[1].plot(filter_response[0], filter_response[1])
        ax[1].set_xlim((0,300000))
        ax[2].semilogy(filtered_psd[0], filtered_psd[1])
        plt.show()
