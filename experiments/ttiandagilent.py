import tti
import numpy as np
from time import sleep
import agilent
import pylab as pl
from datetime import datetime

scope = agilent.DSO1052B()
#print(scope.ask("*IDN?"))

siggen = tti.TG5011()
#print(siggen.ask("*IDN?")) #test connection by outputting device info


#default settings.
def default():
	amp = 0.01
	freq = 9.6*10**6
	siggen.write('WAVE SINE')
	siggen.write('AMPL %f' %amp)
	siggen.write('FREQ %f' %freq)
	scope.write(":STOP")
	scope.write(':TRIG:EDGE:SOUR ACL')
	

default()
sleep(5)
#Below is the main program.

siggen.write('OUTPUT ON')
sleep(1)
y = []
x = np.arange(9,10,0.01)

for i in x:
	siggen.write('FREQ %f' %(i*10**6))
	print ('Running at %f MHz' %i)
	sleep(2)	
	siggen.write('AMPL 0.5')
	sleep(1)
	scope.write(":SINGLE")
	sleep(0.5)
	siggen.write('AMPL 0.01')
	sleep(2)
	y.append(scope.query(':MEAS:VPP? 1'))
	sleep(10)
	
siggen.write('OUTPUT OFF')
filename = datetime.now().strftime("%Y%m%d-%H%M%S")
filename = '/media/matterwave/David/rawdata/'+filename
fw = open(filename+'.txt','a')
for i in np.arange(0,len(x)):
	#print x[i],y[i]
	fw.write('%.3f,%.3f\n'%(float(x[i]),float(y[i])))
fw.close()

pl.plot(x,y)
pl.savefig(filename+'.pdf')

sleep(1)
default()
#release siggen back to local use
siggen.release()
