#!/usr/bin/python
def fftplot(filename):
	import pylab
	filename[0]="Z:/David/" + filename[0]
    data = array([[float(v) for v in line.strip().split(',')] for line in open(filename[0]).readlines()[5:]])
    data = data[:100000,:]
    dx = data[1,0]-data[0,0]
    N = data.shape[0]
    f = pylab.fftshift(fftfreq(N,dx))
    A = pylab.fftshift(fft(data[:,1]))
    pylab.plot(movavg(f,50)/1e3,movavg(20*log10(abs(A)),50),label=filename[1])
    #plot(movavg(f,5)/1e3,movavg(abs(A),5),label=filename[1])
	pylab.xlabel('Trap Frequency (kHz)')
	pylab.ylabel('Power Spectral Density (dB)')


