#For loading and saving data
def loaddata(filename,windows=False):
	def loadascii(filename):
		print "loading data from %s as ascii" %filename
		starttime = time()
		import subprocess
		size = subprocess.check_output(['wc','-l',filename])
		size = size.split(' ')
		X = zeros(int(size[0])-5)
		Y = zeros(int(size[0])-5)
		f = open(filename)
		i=0
		with open(filename) as f:
			while f.readlines()
			for line in f:
				x,y = line.strip().split(',')
				X[i] = x
				Y[i] = y
				i+=1
			while i < len(X):
				X[i] = None
				Y[i] = None
				i+=1
		endtime = time()
		print "That took %i seconds" %int(endtime - starttime)
		return X,Y

	def loadraw(filename):
		startime = time()
		import JLeCroy
		print "Loading data from %s" %filename
		f = open(filename,'rb')
		raw = f.read()
		wave,t,x,Int = JLeCroy.InterpretWaveform(raw)
		endtime = time()
		print "That took %i seconds" %int(endtime - startime)
		return t,x

	def winload(filename):
		from pylab import float32
		print "Loading as windows"
		starttime = time()
		X=[]
		Y=[]
		with open(filename) as f:
			header = f.readlines(5)
			for line in f:
				x,y = line.strip().split(',')
				X.append(x)
				Y.append(y)
		endtime = time()
		print "Loaded data in %i seconds" %int(endtime - starttime)
		return X,Y

	if windows == True and (filename.endswith('.txt') or filename.endswith('.fft') or filename.endswith('.csv')):
		x,y = winload(filename)
	elif filename.endswith('.txt') or filename.endswith('.fft') or filename.endswith('.cvs'):
		x,y = loadascii(filename)
	elif filename.endswith('.trc') or filename.endswith('.raw'):
		x,y = loadraw(filename)
	else:
		print "Failed to load data, returned zeros"
		x = 0
		y = 0
	return x,y
