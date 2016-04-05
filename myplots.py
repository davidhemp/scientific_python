#!/usr/bin/python
from saving import Loader

class Plotter(Loader):
    def __init__(self, debug_mode=True):
        self.debug_mode = debug_mode
        Loader.__init__(self, debug_mode)

    def debug_toggle(self):
        self.active = not self.active

    def func(x, alpha, f0, damp, noise):
        return alpha*damp/((f0**2-x**2)**2+((x*damp)**2))+noise

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

    def psddata(self, x=[], y=[], filename=""):
        from time import time
        from scipy.signal import welch
        x, y = self.checkdata(x, y, filename)
        self.print_msg("Generating PSD data")
        starttime = time()
        dt = x[1] - x[0]
        df = 1/dt
        f, Pxx_den = welch(y, fs=df, nperseg=len(y), window="hanning")
        #total_power = 4*3.14*sum(Pxx_den)
        #print "Total power: %s" %str(total_power)
        #print "Average Energy: %s" %str(total_power/df)
        self.print_msg("PSD data generated in %i seconds"
                                % (time()-starttime))
        return f, abs(Pxx_den)

# Create one instance and export its methods as module-level functions.
# This is with debug_on = True but for alot of things this is ok and can
# be changed by running myplots._inst.__init__(False)

_inst = Plotter()
checkdata = _inst.checkdata
psdplot = _inst.psdplot
psddata = _inst.psddata
debug_toggle = _inst.debug_toggle

# class empty:
#
#
# 	def fftfit(filename,f=None,A=None):
# 		if f == None or A == None:
# 			f,A = fftplot(filename)
# 		from scipy.optimize import curve_fit
# 		print "Fitting curve"
# 		popt,pcov = curve_fit(func,f,A,p0=(10**13,55000,10**4,0.1))
# 		print "Fit complete, saving data"
# 		savefit = str(filename[:-4]) + '.fit'
# 		fw = open(savefit,'a')
# 		fw.write(str(popt[0])+'\n')
# 		fw.write(str(popt[1])+' Hz' + '\n')
# 		fw.write(str(popt[2])+'\n')
# 		fw.write(str(popt[3])+'\n')
# 		for i in arange(0,len(f)):
# 			fw.write(str(f[i]) + ',' + \
#                str(func(f[i],popt[0],popt[1],popt[2],popt[3])) + '\n')
# 		fw.close()
# 		print "Fit data saved to %s" %savefit
#
#
# 	def histplot(filename,data=None,nobins=100,maxx=300):
# 		print "generating histagram"
# 		if data == None:
# 			x,y = loaddata(filename,maxx)
# 		pl.hist(y,bins=100)
# 		pl.xlabel('Voltage')
# 		pl.ylabel('Counts')
# 		imagefile=filename[:-4]+"hist.pdf"
# 		pl.savefig(imagefile)
