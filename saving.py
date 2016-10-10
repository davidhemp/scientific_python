#For loading and saving data
import logging
from collections import namedtuple
import unittest

class Loader(object):
	def __init__(self, level='INFO'):
		self.logger = logging.getLogger(__name__)
		try:
			level_value = eval('logging.%s' %level.upper())
		except AttributeError:
			print('Logging level not found, default to INFO')
			level_value = logging.INFO
		self.logger.setLevel(level_value)
		self.logger.addHandler(logging.StreamHandler())

	def generate_filename(self, ending = ".txt"):
		from datetime import datetime
		filename = datetime.now().strftime("%Y-%m-%d-%H_%M_%S") + ending
		self.logger.info("Genrating filename, %s" %filename)
		return filename

	## Saving Data ##

	def save_data(self, data, filename = "", comment = ""):
		from time import time
		if len(filename) == 0 or filename.endswith("/"):
			filename += self.generate_filename()
		self.logger.info("Saving data at %s" %filename)
		with open(filename,'w') as fw:
			if len(comment) > 0:
				fw.write(comment + "\n\n")
			for row in range(len(data[0])):
				line = ""
				for col in range(len(data)):
					line += "%s," %data[col][row]
				fw.write(line[:-1] + "\n")

	## Loading Data

	def load_data(self, filename,col = 2):
		"""Able to load all raw file types from LeCory or Tektronix as well as cvs files. A named tuple is returned with values: x, y, xpsd, ypsd."""
		# def simple_load(filename, delimiter = ','):
		# 	"""Loads the file as a csv using the csv module."""
		# 	import csv
		# 	with open(filename, 'rb') as f:
		# 		reader = csv.reader(f, delimiter=delimiter)
		# 		data = reader.readlines()
		# 	return data

		def load_ascii(filename):
			"""Loads any ascii file into a numpy array. It populates the array
			line by line as for large files, above 1 GB, the load all method
			ran into memory errors"""
			self.logger.info("Loading data from %s as ascii" %filename)
			from numpy import zeros
			with open(filename) as f:
				no_lines = 0
				for line in f:
					no_lines += 1

			data = zeros((col,no_lines))
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
			self.logger.info("Loading data from %s as raw" %filename)
			with open(filename, 'rb') as f:
				raw = f.read()
			try:
				x, y = InterpretWaveform(raw)
			except Exception as e:
				if "Length of waveform" in str(e):
					self.logger.error("Failed to load %s" %filename)
					x, y = '', ''
				else:
					raise
			return x, y

		from time import time
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
		self.logger.info("Loading took %i seconds" % int(endtime - startime))
		if len(data) == 2:
			names = ['x', 'y', 'xpsd', 'ypsd']
			data = namedtuple('data', names)(data[0], data[1], '', '')
		return data

	def file_list(self, folder="./", select="", repeats = 0):
		from os import listdir
		from os.path import isfile, join
		ret = namedtuple('file_list', ['include', 'exclude', 'chunked'])
		onlyfiles = [(folder + f) for f in listdir(folder) \
			if isfile(join(folder, f))]
		ret.include = sorted([k for k in onlyfiles if select in k])
		ret.exclude = sorted(list(set(onlyfiles) - set(ret.include)))
		_line = []
		for i in range(len(ret.include)/repeats):
			_line.append(ret.include[repeats*i:repeats*(i+1)])
		ret.chucked = _line
		return ret



_inst = Loader()
load_data = _inst.load_data
save_data = _inst.save_data
logger = _inst.logger
file_list = _inst.file_list
