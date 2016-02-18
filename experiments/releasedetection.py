# coding: utf-8
import tti
import agilent
scope = agilent.DSO1052B()
scope.ask('*OPC?')
siggen = tti.TG5011()
siggen.ask('*idn?')
siggen.setup(amp=0.01,freq=9.45*10**6,wave='SINE')
scope.write(':TIMEBASE:MAIN:SCALE 0.25')
scope.write(':STOP')
scope.write(':TRIG:EDGE:SOUR ACL')

def savedata(x,y):
	import numpy as np
	import pylab as pl
	from datetime import datetime
	filename = datetime.now().strftime("%Y%m%d-%H%M%S")
	filename = '/media/matterwave/David/rawdata/'+filename
	fw = open(filename+'.txt','a')
	for i in np.arange(0,len(x)):
		fw.write('%.3f,%.3f\n'%(float(x[i]),float(y[i])))
	fw.close()
	pl.plot(x,y*10**3)
	pl.ylim(-5,10)
	pl.savefig(filename +'.pdf')
	pl.show()

def pulse():
	siggen.write('OUTPUT ON')
	print "pulsing"
	from time import sleep
	sleep(1)
	scope.write(':SINGLE')
	sleep(0.5)
	siggen.write('AMPL 0.5')
	sleep(1)
	siggen.write('AMPL 0.01')
	sleep(1)
	siggen.write('OUTPUT OFF')
	sleep(5)
	print "Gathering data"
	x,y = scope.waveform(2,points=20000)
	savedata(x,y)
    
pulse()
