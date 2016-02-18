import thorlabs
from time import sleep

#init and clear any old data
pmeter = thorlabs.PM100USB('/dev/usbtmc0')

pmeter.ask('*IDN?')
pmeter.write('*RST')
sleep(1)

#calibration

wave = 1550

pmeter.write('SENS:CORR:WAV %f' %wave)
rwave = pmeter.query('SENS:CORR:WAV?')
print "Wavelength set to : %s" %rwave
pmeter.write('SENS:POW:RANG:AUTO 1')

#begin measurements

pmeter.write('INIT')
pmeter.write('CONF:POW')

power = 0

while True:

	power = (pmeter.query('READ?'))
	print power
	sleep(0.5)


