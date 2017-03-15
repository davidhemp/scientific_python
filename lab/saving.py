#For loading and saving data
from time import time
from datetime import datetime
import logging


class Loader(object):
	def __init__(self, level = 'DEBUG', logger_name = "Saving"):
		self.logger = logging.getLogger(logger_name)
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

	def save_to_db(self, x, y, collection):
		from pymongo import MongoClient
		client = MongoClient()
		db = client['data']
		coll = db[collection]
		result = coll.insert_one({"x":x, "y":y, "date":datetime.now()})


	## Loading Data

	def load_data(self, filename, col = 2, time_data = True):
		"""Able to load all raw file types from LeCory or Tektronix as well as
		 cvs files. A named tuple is returned with values: x, y, xpsd, ypsd."""

		def load_ascii(filename='20160205-114220_fft.txt.txt'):
			"""Loads any ascii file into a numpy array. It populates the array
			line by line as for large files, above 1 GB, the load all method
			ran into memory errors"""
			self.logger.debug("Loading data from %s as ascii" %filename)
			from numpy import zeros
			import os
			length = os.path.getsize(filename)
			data = zeros((col, length))
			i = 0
			with open(filename) as f:
				for line in f:
					linedata = line.strip().split(',')
					try:
						for j in range(min(col,len(linedata))):
							data[j][i] = linedata[j]
					except ValueError:
						pass
					else:
						i += 1
			return data[0][:i], data[1][:i]

		def load_raw(filename):
			self.logger.debug("Loading data from %s as raw" %filename)
			with open(filename, 'rb') as f:
				raw = f.read()
				x, y = interpret_waveform(raw)
			return x, y

		startime = time()
		if filename.endswith((".trc",".raw")):
			from devices.lecroy import interpret_waveform
			data = load_raw(filename)
		elif filename.endswith('.isf'):
			from devices.tektronix import interpret_waveform
			data = load_raw(filename)
		else:
			data = load_ascii(filename)

		endtime = time()
		self.logger.debug("Loading took %i seconds" % int(endtime - startime))
		return data
