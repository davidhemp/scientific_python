from time import sleep
import tti
import hameg

psupply = hameg.HMP4030() #Connect to power supply
psupply.ask("*IDN?")

siggen = tti.TG5011()  #conect to TTI TG5011 50MHz function generator over u
siggen.ask('*IDN?')

#default settings.
def default():
	amp = 0.7	#Signal Generator
	#freq = 40.37*10**3
	#freq = 40.11*10**3 # at 0.3 amps
	#freq = 39.86*10**3 #at 0.5 amps
	freq = 39.63*10**3 #at 0.7 amps
	siggen.write('WAVE SINE')
	siggen.write('AMPL %f' %amp)
	siggen.write('FREQ %f' %freq)
	
	psupply.write('*RST') #Laser power supply
	sleep(0.5)
	psupply.write('INST:SEL:OUTPUT1')
	psupply.write('APPlY 12.0,9.5')
	sleep(1)
default()

#Below is the main program.
psupply.write('OUTPUT:STATE ON')
siggen.write('OUTPUT ON')
sleep(5)
siggen.write('OUTPUT OFF')
psupply.write('OUTPUT:STATE OFF')
sleep(1)

#restore defaults and release siggen back to local use
default()
siggen.release()
