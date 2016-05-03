from time import sleep
import os

from fabric.api import *

import LeCroy
import saving

saving._inst.debug_mode = False

path = "/data/gradient_field/without/run#3/"
channels = [1,4]

for n in range(1000):
    sleep(0.5)
    for channel in channels:
        filename = saving.generatefilename(
                ending="_run%04i_CH%i.raw" %(n,channel))

        with settings(host_string='sabre.clients.soton.ac.uk'):
            run("fab LeCroy_save:filename=%s,channel=%s" %
                    (path+filename, channel))
