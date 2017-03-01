#!/usr/bin/python
from time import sleep

import usbconnect


class PM100USB(usbconnect.usbtmc):

	def setup(self, wave=1550):
		self.write('SENS:CORR:WAV %f' %wave)
		sleep(0.5)
		rwave = self.query('SENS:CORR:WAV?')
		print "Wavelength set to : %s" %rwave
		self.write('SENS:POW:RANG:AUTO 1')
		self.write('INIT')
		self.write('CONF:POW')

	def read_power(self):
		return float(self.query('READ?'))
