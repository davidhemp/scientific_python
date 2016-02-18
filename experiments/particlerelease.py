import numpy as np
from time import sleep
import tti
import hameg

psupply = hameg.HMP4030('/dev/ttyUSB0') #Connect to power supply
psupply.ask("*IDN?")

siggen = tti.TG5011('/dev/ttyACM0')  #conect to TTI TG5011 50MHz function generator over u
siggen.ask('*IDN?')


#default settings.
def default():
	amp = 0.25	#Signal Generator
	freq = 40.49*10**3
	siggen.write('WAVE SINE')
	siggen.write('AMPL %f' %amp)
	siggen.write('FREQ %f' %freq)
	
	psupply.write('*RST') #Laser power supply
	sleep(0.5)
	psupply.write('INST:SEL:OUTPUT1')
	psupply.write('APPlY 12.0,1.0')
	sleep(1)
default()

#Below is the main program.
x = np.arange(0.1,0.3,0.05)
for i in x:
	print "Power changed to %f Amps" %i
	siggen.write('AMPL %f' %i)
	print "Laser on"
	psupply.write('OUTPUT:STATE ON')
	sleep(1)
	siggen.write('OUTPUT ON')
	sleep(5)
	siggen.write('OUTPUT OFF')
	psupply.write('OUTPUT:STATE OFF')
	print "Laser off"
	sleep(5)



#restore defaults and release siggen back to local use
default()
siggen.release()
