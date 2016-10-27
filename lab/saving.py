#For loading and saving data
from time import time
from datetime import datetime
import logging

class Loader(object):
	def __init__(self, level='DEBUG'):
		self.logger = logging.getLogger("Saving")
		try:
			level_value = eval('logging.%s' %level.upper())
		except AttributeError:
			print('Logging level not found, default to DEBUG')
			level_value = logging.DEBUG
		self.logger.setLevel(level_value)

		# create the logging file handler
		sh = logging.StreamHandler()
		format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
		formatter = logging.Formatter(format_string)
		sh.setFormatter(formatter)
		self.logger.setLevel(level_value)
		self.logger.addHandler(sh)

	def generate_filename(self, ending = ".txt"):
		filename = datetime.now().strftime("%Y-%m-%d-%H_%M_%S") + ending
		self.logger.debug("Genrating filename, %s" %filename)
		return filename

	## Saving Data ##

	def save_data(self, data, filename = "", comment = ""):
		if len(filename) == 0 or filename.endswith("/"):
			filename += self.generate_filename()
		self.logger.debug("Saving data at %s" %filename)
		with open(filename,'w') as fw:
			if len(comment) > 0:
				fw.write(comment + "\n\n")
			for row in range(len(data[0])):
				line = ""
				for col in range(len(data)):
					line += "%s," %data[col][row]
				fw.write(line[:-1] + "\n")

	## Loading Data

	def load_data(self, filename, col = 2, time_data = True):
		"""Able to load all raw file types from LeCory or Tektronix as well as
		 cvs files. A named tuple is returned with values: x, y, xpsd, ypsd."""

		def load_ascii(filename):
			"""Loads any ascii file into a numpy array. It populates the array
			line by line as for large files, above 1 GB, the load all method
			ran into memory errors"""
			self.logger.debug("Loading data from %s as ascii" %filename)
			from numpy import zeros
			with open(filename) as f:
				no_lines = 0
				for line in f:
					no_lines += 1

			data = zeros((col, no_lines))
			with open(filename) as f:
				for line, i in zip(f, range(no_lines)):
					linedata = line.strip().split(',')
					try:
						for j in range(min(col,len(linedata))):
							data[j][i] = linedata[j]
						i += 1
					except ValueError:
						pass
			return data

		def load_raw(filename):
			self.logger.debug("Loading data from %s as raw" %filename)
			with open(filename, 'rb') as f:
				raw = f.read()
				x, y = InterpretWaveform(raw)
			return x, y

		startime = time()
		if filename.endswith((".trc",".raw")):
			from LeCroy import InterpretWaveform
			data = load_raw(filename)
		elif filename.endswith('.isf'):
			from Tektronix import InterpretWaveform
			data = load_raw(filename)
		else:
			data = load_ascii(filename)

		endtime = time()
		self.logger.debug("Loading took %i seconds" % int(endtime - startime))
		return data
