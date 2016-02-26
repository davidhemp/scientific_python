# coding: utf-8
from time import sleep, time
from datetime import datetime

import thorlabs
import IPG
import progress

laser = IPG.IPG1550()
pmeter = thorlabs.PM100USB()

wave = 1550
pmeter.write('SENS:CORR:WAV %f' %wave)
rwave = pmeter.query('SENS:CORR:WAV?')
print "Wavelength set to : %s" %rwave
pmeter.write('SENS:POW:RANG:AUTO 1')
power = 1
pbar = progress.progressBar()

while power < 7:
    with open('/home/david/powerscan/powerscan_%sw.txt' %power, 'wb') as fw:
        laser.setlaserpower(power)
        sleep(10)
        stime = ctime = time()
        mtime = 60*60
        while ctime - stime < (mtime):
            pbar.simpleBar(int((ctime - stime) * 100/mtime), stime)
            measuredPower = (pmeter.query('READ?'))
            savetime = datetime.now().strftime("%Y%m%d-%H%M%S")
            fw.write(str(savetime) + ',' + str(float(measuredPower))+ "\n")
            sleep(1)
            ctime = time()
            pbar.simpleBar(int((ctime - stime) * 100/mtime), stime)
    print "\n"
    power += 1
laser.off()
