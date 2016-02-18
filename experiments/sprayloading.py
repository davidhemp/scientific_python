import tti
from time import sleep
from useful import countdown
siggen = tti.TG5011()
siggen.testconnect()
siggen.write('WAVE SINE')

amp = 10
freq = 175100
siggen.write('AMPL %f' %amp)
siggen.write('FREQ %f' %freq)

print "Heating, turn on heat gun"
sleep(110)
countdown()
n=5
while n>0: 
	print n
	print "Spray on"
	siggen.write('OUTPUT ON')
	sleep(20)
	countdown()
	print "Spray off, drying"
	sleep(110)
	countdown()
	n-=1
print "Turn off heat gun"
sleep(5)
siggen.release()
