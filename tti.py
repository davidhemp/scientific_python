import usbconnect

class TG5011(usbconnect.ttyACM):
	def setup(self,amp=0.1,freq=9.45*10**6,wave='SINE'):
		if wave.upper() == 'SIN':
			wave = 'SINE'
		self.write('WAVE %s' %wave)
		self.write('AMPL %f' %amp)
		self.write('FREQ %f' %freq)

	def amp(self,amp):
		self.write('AMPL %f' %amp)

	def freq(self,freq):
		self.write('FREQ %f' %freq)

	def on(self):
		self.write('OUTPUT ON')

	def off(self):
		self.write('OUTPUT OFF')


class QL335P(usbconnect.ttyUSB):
	def idn(self):
		self.write("*IDN?")
