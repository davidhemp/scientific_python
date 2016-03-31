# coding: utf-8
from time import sleep, time

import pylab as p

import tti
import Tektronix
import saving
import progress

loader = saving.loader(quiet=True)
siggen = tti.TG5011()
scope = Tektronix.DPO2024B()
pbar = progress.progressBar()

scope.write("ACQUIRE:STATE STOP")
scope.write("ACQUIRE:STOPAFTER SEQuence")

amp = 0.1
siggen.amp(amp)
fresponce = []
start = 300000
end = 500
freqRange = p.arange(start,end,-500)
starttime = time()
siggen.on()
for i in freqRange:
    pbar.simpleBar(int(100*end/i),starttime)
    siggen.freq(i)
#    scope.write("HORIZONTAL:SCALE %f" %(1./i))
    scope.waitOPC()
    timeBase = float(scope.query("HORIZONTAL:SCALE?"))
    scope.write("ACQUIRE:STATE RUN")
    sleep(20*timeBase+1)
    x,y,integers = scope.data()
    loader.savedata(data=(x,y), path="/home/david/freqResponse/", \
        comment="comment: %f Volt, %f Hz" %(amp,i))
    fresponce.append(p.mean(y))
siggen.off()
