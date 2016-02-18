#For loading and saving data
class loader:
	def __init__(self,quiet=False):
		self.quiet = quiet

	def generatefilename(self):
		return "testing.txt"

	def savedata(self,data,filename=None,path="./"):
		from time import time
		from numpy import shape
		starttime = time()
		if filename == None:
			filename = self.generatefilename()
		savename = path + filename
		if not self.quiet:
			print "Saving data at %s" %savename
		with open(savename,'w') as fw:
			if not self.quiet:
				fw.write(\
					raw_input("Please write any comments you have:") + "\n")
			for i in range(len(data[0])):
				line = ""
				for j in range(len(shape(data))):
					line += "%s," %data[j][i]
				fw.write(line[:-1] + "\n")

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
			if not self.quiet:
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
			if not self.quiet:
				print "That took %i seconds" %int(endtime - starttime)
			return data

		def loadRaw(filename):
			startime = time()
			if not self.quiet:
				print "Loading data from %s as raw" %filename
			f = open(filename,'rb')
			raw = f.read()
			if filename.endswith(".trc") or filename.endswith(".raw"):
				from JLeCroy import InterpretWaveform
				wave,x,y,Int = InterpretWaveform(raw)
			if filename.endswith(".isf"):
				from Tektronix import InterpretWaveform
				x,y = InterpretWaveform(raw)
			endtime = time()
			if not self.quiet:
				print "That took %i seconds" %int(endtime - startime)
			return x,y

		from time import time
		if any(i in filename for i in [".trc",".raw",".isf"]):
			data = loadRaw(filename)
		else:
			data = loadascii(filename)
		return data
