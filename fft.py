#!/usr/bin/python2
import pylab as p
from sys import argv

def fft(txtfile):
    SmoothingBandwidth = 1e3
    print(txtfile)
    with open(txtfile) as h:
        lines = [line.strip() for line in h.readlines()[5:]]
    data = p.array([[float(v) for v in line.split(',')] for line in lines])
    F = p.fft(data[:,1])
    T = data[-1,0]-data[0,0]
    df = 1/T
    N = data.shape[0]
    f = df*p.arange(N)
    F = F[:N/2]
    f = f[:N/2]
    A = abs(F)

    movavgN = int(p.ceil(SmoothingBandwidth/df))

    f = p.movavg(f,movavgN)
    A = p.movavg(A,movavgN)
    fftfile = txtfile[:-3] + 'fft'
    with open(fftfile, 'w') as h:
#        h.write('\n'.join([','.join(['%g' % v for v in z]) for z in zip(f,abs(F),p.angle(F))]))
        h.write('\n'.join([','.join(['%g' % v for v in z]) for z in zip(f,A)]))
    
