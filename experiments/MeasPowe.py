import thorlabs
import hameg
import pylab as pl
from time import sleep, ctime


#init and clear any old data
pmeter = thorlabs.PM100USB('/dev/usbtmc0')
supply = hameg.HMP4030('/dev/ttyUSB0')

pmeter.ask('*IDN?')
pmeter.write('*RST')

supply.ask('*IDN?')
supply.write('*RST')

sleep(1)

#calibration

wave = 976
voltage = 12.0
current = 0.01

pmeter.write('SENS:CORR:WAV %f' %wave)
rwave = pmeter.query('SENS:CORR:WAV?')
print "Wavelength set to : %s" %rwave
pmeter.write('SENS:POW:RANG:AUTO 1')

supply.write('INST:SEL:OUTPUT1')
supply.write('APPLY %f,%f' %(voltage,current))
supply.ask('APPLY?')

#being measurements

supply.write('OUTPUT:STATE ON')
pmeter.write('INIT')
pmeter.write('CONF:POW')

power = 0
ydata =[]
xdata =[]

fw = open('/media/matterwave/David/tempdata/powerscan.txt','wb')
fw.write(str(ctime())+'\r\n')
fw.write('976 nm laser James borrowed\r\n')
fw.write('Powered using Hameg HMP4030 from sussex\r\n')
fw.write('Measured with Thorlabs PM100USB\r\n')
fw.write('Voltage,Current,Power\r\n')
while current < 3:
	current +=0.01
	supply.write('APPLY %f,%f' %(voltage,current))
	power = (pmeter.query('READ?'))
	print power
	settings = supply.query('APPLY?')
	fw.write(str(settings) + ',' + str(power))
	ydata.append(power)
	xdata.append(current)
	sleep(0.1)
	
fw.close()
sleep(0.5)
supply.write('OUTPUT:STATE: OFF')
supply.write('SYST:LOCAL')


pl.plot(xdata,ydata)
pl.show()
