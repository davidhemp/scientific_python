#!/usr/bin/python
import pylab as pl
from numpy import array, log10, arange, abs, zeros
import matplotlib.pyplot as plt
from time import time

class plotter:
	def __init__(self,quiet=False):
		import saving
		self.quiet = quiet
		self.loader = saving.loader(quiet=self.quiet)

	def checkdata(self,filename=None,x=None,y=None):
		if  (x == None or y == None) and filename != None:
			x,y = self.loader.loaddata(filename)
		elif (x == None or y == None) and filename == None:
			raise IOError("Missing data or filename")
		return x,y

class empty:
	def fftplot(filename,x=None,y=None,average=50,maxx=300,windows=False):
		if x == None or y == None:
			x,y = loaddata(filename,windows=windows)
		print "Generating fft"
		starttime = time()
		A = pl.fft(y)
		print A
		dt = x[-1] - x[0]
		df = 1/dt
		N = len(x)
		f = df*arange(N)
		f = f[:N/2]
		A = A[:N/2]
		A = abs(A)
		endtime = time()
		print "fft data generating in %i seconds" %(endtime-starttime)
		savedata = str(filename[:-4]) + '.fft'
		fw = open(savedata,'a')
		for i in arange(0,len(A)):
			fw.write(str(f[i]) + ',' + str(A[i]) + '\n')
		fw.close()
		print "Data saved at %s" %savedata
		try:
			pl.figure(69)
			pl.plot(pl.movavg(f,average)/1e3,pl.movavg(20*log10(abs(A)),average))
			pl.xlim([0,maxx])
			pl.xlabel('Trap Frequency (kHz)')
			pl.ylabel('Power Spectral Density (dB)')
			imagefile = filename[:-4] + "fft.pdf"
			pl.savefig(imagefile)
			#pl.show()
			pl.close(69)
			print "Plot saved as %s" %imagefile
		except Exception as E:
			if str(E).find('TclError'):
				print 'No graph plotted, data still saved. Are you are using Scimitar?'
			else:
				raise E
		return f,A

	def func(x,alpha,f0,damp,noise):
		return alpha*damp/((f0**2-x**2)**2+((x*damp)**2))+noise


	def fftfit(filename,f=None,A=None):
		if f == None or A == None:
			f,A = fftplot(filename)
		from scipy.optimize import curve_fit
		print "Fitting curve"
		popt,pcov = curve_fit(func,f,A,p0=(10**13,55000,10**4,0.1))
		print "Fit complete, saving data"
		savefit = str(filename[:-4]) + '.fit'
		fw = open(savefit,'a')
		fw.write(str(popt[0])+'\n')
		fw.write(str(popt[1])+' Hz' + '\n')
		fw.write(str(popt[2])+'\n')
		fw.write(str(popt[3])+'\n')
		for i in arange(0,len(f)):
			fw.write(str(f[i]) + ',' + str(func(f[i],popt[0],popt[1],popt[2],popt[3])) + '\n')
		fw.close()
		print "Fit data saved to %s" %savefit


	def histplot(filename,data=None,nobins=100,maxx=300):
		print "generating histagram"
		if data == None:
			x,y = loaddata(filename,maxx)
		pl.hist(y,bins=100)
		pl.xlabel('Voltage')
		pl.ylabel('Counts')
		imagefile=filename[:-4]+"hist.pdf"
		pl.savefig(imagefile)
