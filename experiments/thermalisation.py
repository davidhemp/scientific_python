from time import sleep, strftime, localtime, time
from sys import stdout
import os

import zi
import LeCroy
import ITR90Pressure

def save_pressure(filename, start_pressure, end_pressure):
    stamp = strftime('%Y-%m-%d_%H-%M-%S', localtime(time()))
    print("\tPressure range %0.2e - %0.2e mbar" %(start_pressure,
    end_pressure))
    with open(log_filename, "a") as logfile:
        logfile.write(','.join(str(i) for i in (stamp,
                                                "%05i" %filename,
                                                "%0.3e" %start_pressure,
                                                "%0.3e" %end_pressure)))
        logfile.write('\n')
    return

def countdown(string, time):
    wait_count = 0
    while wait_count <= time:
        sleep(1)
        stdout.write("\r\t%s: %i seconds" %(string, (time - wait_count)))
        stdout.flush()
        wait_count += 1

scope = LeCroy.HDO6104()
zibox = zi.HF2LI(address="192.168.0.100", port=1251)

path = '/media/lazarus/David/rawdata/efield/1/reheating'
runs = 200
channels = [1,3]
wait = 10

print "Channels %s will be saved to %s" % (','.join(str(c) for c in channels),
path)

#The first pressure measurements are normally junk so they are junked
_ = ITR90Pressure.measuredPressure()
_ = ITR90Pressure.measuredPressure()

for voltage in [0, 5]:
    log_filename = path + '/%i/pressure.log' %voltage
    raw_input('Set to %s Volts and change save folder' %voltage)
    for run_count in range(runs):
        start_pressure = ITR90Pressure.measuredPressure()
        for _ in ['STOP', 'ARM', 'FORCE_TRIGGER']:
            scope.write(_)
            sleep(0.5)
        sleep(2)
        zibox.demod_output_off(signal=1, demod=2)
        countdown("Acquiring data for %i" %run_count, wait)
        zibox.demod_output_on(signal=1, demod=2)
        stdout.write("\r\tData acquired for run %i             \n" %run_count)
        stdout.flush()
        end_pressure = ITR90Pressure.measuredPressure()
        save_pressure(run_count, start_pressure, end_pressure)
        sleep(2)
        for channel in channels:
            scope.write("STORE C%s,FILE" %channel)
            countdown("Saving channel %s" %channel, 60)
            filename = path + "/%i/C%i_%05i.trc" %(voltage, channel, run_count)
            if not os.path.isfile(filename):
                stdout.write('\n')
                stdout.flush()
                raw_input("File not found, perform manual save.")
        stdout.write("\r\tChannel %s saved                    \n" %channel)
        print("Data saved for run %i" %run_count)
zibox.close()
