import time

def withappend():
	startime = time.time()
	Y=[]
	X=[]
	f = open('C1qcal00001.fft')
	for line in f:
		x,y = line.strip().split(',')
		X.append(x)
		Y.append(y)
	endtime = time.time()
	return endtime - startime #119 seconds

def withwc():
	startime = time.time()
	import subprocess
	import numpy as np
	size = subprocess.check_output(['wc','-l','C1qcal00001.fft'])
	size = size.split(' ')
	Y = X = np.zeros(int(size[0]))
	f = open('C1qcal00001.fft')
	i=0
	for line in f:
		x,y = line.strip().split(',')
		X[i]=x
		Y[i]=y
		i+=1
	endtime = time.time()
	return endtime - startime #102
