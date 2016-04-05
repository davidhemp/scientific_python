#For loading and saving data
import sys, getopt
from debug import Debugger

class Loader(Debugger):
	def __init__(self,debug_mode=True):
		Debugger.__init__(self, debug_mode)

	def generatefilename(self, ending=".txt"):
		from datetime import datetime
		filename = datetime.now().strftime("%Y%m%d-%H%M%S") + ending
		return filename

	## Saving Data ##

	def savedata(self, data, filename="", comment=""):
		from time import time
		starttime = time()
		if len(filename) == 0 or file.endswith("/"):
			filename += self.generatefilename()
		self.print_msg("Saving data at %s" %filename)
		with open(filename,'w') as fw:
			if len(comment)>0:
				fw.write(comment + "\n\n")
			for row in range(len(data[0])):
				line = ""
				for col in range(len(data)):
					line += "%s," %data[col][row]
				fw.write(line[:-1] + "\n")

	def simplesave(self,raw,filename=None,ending=".txt",path="./",savename=None):
		if len(filename) == 0 or file.endswith("/"):
			filename += self.generatefilename()
		self.print_msg("Saving data to %s" %filename)
		with open(savename, 'w') as fw:
			fw.write(raw)

	## Loading Data

	def simpleload(self,filename):
		from numpy import array
		data = []
		with open(filename) as f:
			for line in f:
				loadline = line.strip().split(',')
				data.append(loadline)
		return array(data).T

	def loaddata(self,filename,col=2):

		def loadascii(filename):
			self.print_msg("Loading data from %s as ascii" %filename)

			#Count the number of lines in the file to be loaded.
			from platform import system
			from subprocess import check_output
			system = system()
			if system == "Windows":
			    size = check_output("type %s | find /c /v '~~~'" %filename)
			elif system == "Linux":
				rows = int(check_output(['wc', '-l', filename]).split(' ')[0])

			#Make and populate and empty array with the data
			from numpy import zeros
			data = zeros((col,rows))
			with open(filename) as f:
				i=0
				linedata = []
				for line in f:
					linedata = line.strip().split(',')
					try:
						for j in range(min(col,len(linedata))):
							data[j][i] = linedata[j]
						i+=1
					except ValueError:
						pass
			data = data[:, :i]#wc will often over overestimate the of lines

			return data

		def loadraw(filename):
			self.print_msg("Loading data from %s as raw" %filename)
			with open(filename, 'rb') as f:
				raw = f.read()
			x, y = InterpretWaveform(raw)
			return x, y

		from time import time
		startime = time()
		if any(i in filename.split("/")[-1] for i in [".trc",".raw"]):
			from LeCroy import InterpretWaveform
			data = loadraw(filename)
		elif any(i in filename for i in [".isf"]):
			from Tektronix import InterpretWaveform
			data = loadraw(filename)
		else:
			data = loadascii(filename)
		endtime = time()
		self.print_msg("Loading took %i seconds" \
									%int(endtime - startime))
		return data

	def filelist(self,folder="./",select=""):
		from os import listdir
		from os.path import isfile, join
		onlyfiles = [(folder + f) for f in listdir(folder) \
			if isfile(join(folder, f))]
		include = [k for k in onlyfiles if select in k]
		exclude = list(set(onlyfiles) - set(include))
		return include,exclude
