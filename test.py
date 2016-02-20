from time import sleep, time
from progress import progressBar
from numpy import random

randomtimes = random.sample(100)
bar = progressBar()
starttime = time()
for i in range(100):
    bar.simpleBar(i,starttime)
    sleep(randomtimes[i])
