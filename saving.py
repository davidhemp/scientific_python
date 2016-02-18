#For loading and saving data
class loader:
	def loaddata(self,filename,col=2):
		def isfloat(linedata):
			floatable = True
			for value in linedata:
				try:
					float(value)
				except ValueError:
					floatable = False
			return floatable

		def loadascii(filename):
			print "Loading data from %s as ascii" %filename
			starttime = time()

			#Count the number of lines in the file to be loaded.
			from platform import system
			from subprocess import check_output
			system = system()
			if system == "Windows":
			    size = check_output("type %s | find /c /v '~~~'" %filename)
			elif system == "Linux":
				size = check_output(['wc','-l',filename])
				size = size.split(' ')

			#Make and populate and empty array with the data
			from numpy import zeros
			data = zeros((col,int(size[0])))
			with open(filename) as f:
				i=0
				linedata = []
				for line in f:
					linedata = line.strip().split(',')
					if len(linedata) >= 2 and isfloat(linedata):
						for j in range(min(col,len(linedata))):
							data[j][i] = linedata[j]
						i+=1
			data = data[:,:i]#wc will often over overestimate the of lines
			endtime = time()
			print "That took %i seconds" %int(endtime - starttime)
			return data

		def loadLeCroyRaw(filename):
			startime = time()
			import JLeCroy
			print "Loading data from %s as raw" %filename
			f = open(filename,'rb')
			raw = f.read()
			wave,t,x,Int = JLeCroy.InterpretWaveform(raw)
			endtime = time()
			print "That took %i seconds" %int(endtime - startime)
			return t,x

		from time import time
		if filename.endswith('.trc') or filename.endswith('.raw'):
			data = loadLeCroyRaw(filename)
		else:
			data = loadascii(filename)
		return data
