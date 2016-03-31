from time import sleep
import os

import pylab as p
from fabric.api import *

import LeCroy
import saving
import IPG
import thorlabs

# scope = LeCroy.HDO6104("LCRY-matterwave.clients.soton.ac.uk")
loader = saving.loader(quiet = True)
laser = IPG.IPG1550()
pmeter = thorlabs.PM100USB()

path="/media/sabre-data/magnetic_heating/"
channels = [1]

powers = p.arange(1.8,4.4,0.05)

# ## power calibaration ##
# power_cal = []
# for power in powers:
#     laser.setlaserpower(power)
#     sleep(2)
#     measured_power = pmeter.read_power()
#     power_cal.append([power,measured_power])
# power_cal = p.array(power_cal).T
# loader.savedata(power_cal,filename="power_curve.txt",path=path)

## Main experiment ##
for power in powers:
    experiment_notes = []
    laptop_power_path = path + "laser%s" %str(power)
    if not os.path.exists(laptop_power_path):
        os.makedirs(laptop_power_path)
    sabre_power_path = "/data/magnetic_heating/laser%s/" %power
    laser.setlaserpower(power)
    for n in range(1000):
        # laser.setlaserpower(power)
        sleep(0.5)
        measured_power = pmeter.read_power()
        line = measured_power
        for channel in channels:
            filename = loader.generatefilename(
                    ending="_run%04i_CH%i.raw" %(n,channel))

            with settings(host_string='sabre.clients.soton.ac.uk'):
                run("fab LeCroy_save:savename=%s,channel=%s" %
                        (sabre_power_path+filename,channel))

        experiment_notes.append([measured_power,filename])
    experiment_notes = p.array(experiment_notes).T
    loader.savedata(experiment_notes, filename="powers.txt", path=laptop_power_path)
