#!/usr/bin/python
import pylab as pl
from numpy import array, log10, arange, abs, zeros
import matplotlib.pyplot as plt
from time import time

def loaddata(filename,windows=False):	
	def loadascii(filename):
		print "loading data from %s as ascii" %filename
		starttime = time()
		import subprocess
		size = subprocess.check_output(['wc','-l',filename])
		size = size.split(' ')
		X = zeros(int(size[0])-5)
		Y = zeros(int(size[0])-5)
		f = open(filename)
		i=0
		with open(filename) as f:
			header1 = f.readline()
			header2 = f.readline()
			header3 = f.readline()
			header4 = f.readline()
			header5 = f.readline()
			print header1
			print header2
			print header3
			print header4
			print header5
			for line in f:
				x,y = line.strip().split(',')
				X[i] = x
				Y[i] = y
				i+=1			
			while i < len(X):
				X[i] = None
				Y[i] = None
				i+=1
		endtime = time()
		print "That took %i seconds" %int(endtime - starttime)
		return X,Y

	def loadraw(filename):
		startime = time()
		import JLeCroy
		print "Loading data from %s" %filename
		f = open(filename,'rb')
		raw = f.read()
		wave,t,x,Int = JLeCroy.InterpretWaveform(raw)
		endtime = time()
		print "That took %i seconds" %int(endtime - startime)
		return t,x
	
	def winload(filename):
		from pylab import float32
		print "Loading as windows"
		starttime = time()
		X=[]
		Y=[]
		with open(filename) as f:
			header = f.readlines(5)
			for line in f:
				x,y = line.strip().split(',')
				X.append(x)
				Y.append(y)
		endtime = time()
		print "Loaded data in %i seconds" %int(endtime - starttime)
		return X,Y

	if windows == True and (filename.endswith('.txt') or filename.endswith('.fft') or filename.endswith('.csv')):
		x,y = winload(filename)
	elif filename.endswith('.txt') or filename.endswith('.fft') or filename.endswith('.cvs'):
		x,y = loadascii(filename)
	elif filename.endswith('.trc') or filename.endswith('.raw'):
		x,y = loadraw(filename)
	else:
		print "Failed to load data, returned zeros"
		x = 0
		y = 0
	return x,y

def plotdata(filename,x=None,y=None,windows=False):
	if windows == True:
		x,y = loaddata(filename,windows=True)
	if x == None or y == None:
		x,y = loaddata(filename)
	pl.plot(x,y)
	imagename = filename[:-4]+ '.pdf'
	pl.savefig(imagename)
	pl.show()

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
	
def maketex(filename,f=None,A=None):
	if f == None:
		data = loaddata (filename,300)
		f,A = fftplot(filename,data)
	outputfile=filename
	outputfile=outputfile[:-4]+".tex"
	fw=open(outputfile,'wb')
	fw.write('\\begin{figure} %Curve for constant C\n')
	fw.write('\\begin{center}\n')
	fw.write('\\begin{tikzpicture}\n')
	fw.write('\\begin{axis}[xlabel=Angle (N.A.), ylabel=Constant C]\n')
	fw.write('\\addplot[color=red] coordinates {\n')
	length=len(f)
	for i in arange(0,length,1):
		out='('+str(f[i])+','+str(A[i].real)+')\n'
		fw.write(str(out))
	fw.write('};\n')
	fw.write('\\end{axis}\n')
	fw.write('\\end{tikzpicture}\n')
	fw.write('\\caption{Curve for constant C}\n')
	fw.write('\\label{2ndlaserpower}\n')
	fw.write('\\end{center}\n')
	fw.write('\\end{figure}\n')
	fw.close()
		
print "Current programs, loaddata(filename), plotdata(filename,*x,*y), fftplot(filename,*x,*y,*average,*maxx), histplot(filename,*data,*nobins,*maxx)"
