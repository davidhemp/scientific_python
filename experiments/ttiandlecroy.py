import tti
import numpy as np
from time import sleep
import LeCroy

scope = LeCroy.HDO6104(address='152.78.195.166')
print(scope.ask("*IDN?"))

siggen = tti.TG5011('/dev/ttyACM0'')  #conect to TTI TG5011 50MHz function generator over u
siggen.testconnect() #test connection by outputting device info


#default settings.
def default():
	amp = 0.4
	freq = 5*10**6

	siggen.write('WAVE SINE')
	siggen.write('AMPL %f' %amp)
	siggen.write('FREQ %f' %freq)
	scope.write("STORE_SETUP (C1,HDD)(,AUTO,OFF)(,TYPE,ASCII)")

#Below is the main program.
for i in np.arange(4,7,0.01):
	freq = i*10**6
	siggen.write('FREQ %f' %freq)
	scope.write("STOP")
	sleep(3)
	scope.write("ARM")
	scope.write("STORE C2,FILE")
	print "%.f Hz" %freq
	
default()
#release siggen back to local use
siggen.release()
