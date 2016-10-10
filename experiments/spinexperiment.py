from time import sleep
import sys
from select import select

from numpy import arange

import LeCroy
import IPG
import tti
import zi

# scope = LeCroy.HDO6104()
scope = LeCroy.HDO4022("152.78.195.6")
zibox = zi.HF2LI()
power = tti.QL335P()
#laser = IPG.IPG1550()

power.on()

def ave_save():
    scope.write("CLSW") # Clear averages
    sleep(0.01*10*1000*2) #wait for 1000+ averages
    scope.write("STORE SpecAn,FILE")
    scope.waitOPC()

for i in arange(0,1,0.01):
    scope.write("TRIG_MODE AUTO")
    #Voltage loop
    power.set_voltage(0)
    sleep(5)
    print "Background scan"
    ave_save()

    power.set_voltage(i)
    sleep(5)
    print "Scan %i" %(i*100 + 1)
    ave_save()

    #warm up loop
    scope.write("STOP")
    sleep(1)
    timeout = 3
    print("Moving to re-thermalisation scans")
    print("Press return at any time to pause.")
    for j in xrange(20):
        rlist, _, _ = select([sys.stdin], [], [], timeout)
        if rlist:
            s = ""
            while s != "run":
                s = raw_input("Please type 'run' to continue. ")
                if s == "stop":
                    zibox.close()
                    break
                sleep(2)
        print("Re-thermalisation scan %i" %j)
        scope.write("ARM")
        sleep(0.5)
        zibox.demod_output_off(1,2)
        sleep(10)
        scope.write("STORE C1,FILE")
        scope.write("STORE C2,FILE")
        zibox.demod_output_on(1,2)
        sleep(5)

    scope.write("BUZZ BEEP")
zi.shutdown_server()
zi.close()
# power.off()
