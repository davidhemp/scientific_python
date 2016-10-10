from time import sleep
import logging

import zi
import LeCroy

scope = LeCroy.HDO6104()
zibox = zi.HF2LI(address="192.168.0.100", port=1250)
logging.basicConfig(level=logging.INFO)

path = "/media/lazarus/David/rawdata/warm up/feedback/efield/"
runs = xrange(200)
channels = [1,2]

scope.write('STOP')

for voltage in [0, 10]:
    raw_input('Set to %s Volts' %voltage)
    for i in runs:
        scope.write('STOP')
        sleep(0.5)
        scope.write('ARM')
        logging.debug('Scope triggered')
        sleep(2)
        zibox.demod_output_off(signal=1, demod=2)
        sleep(10)
        zibox.demod_output_on(signal=1, demod=2)
        # for channel in channels:
        logging.info('Save %s' %i)
        scope.write("STORE C1,FILE")
        sleep(10)
        scope.write("STORE C2,FILE")
        sleep(10)
            # filename = "C%s_%02iV%05i.trc" %(channel, voltage, i)
            # logging.debug('Acquiring data')
            # raw = scope.raw(channel=channel)
            # logging.debug('Data acquired')
            # with open(path + filename, 'w') as fw:
            #     logging.info('Saving data to %s' %filename)
            #     fw.write(raw)
zibox.close()
