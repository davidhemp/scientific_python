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
	def set_voltage(self, voltage, port=1):
		self.write_opc("V%i %f" %(port, voltage)) #verify "V1V 1.0" doesn't work

	def set_current(self, current, port=1):
		self.write_opc("I%i %f" %(port, voltage))

	def read_voltage(self, port=1):
		return self.query('V%i?' %port)

	def read_current(self, port=1):
		return self.query('I%i?' %port)

	def local(self):
		self.write("LOCAL")

	def on(self, port=1):
		self.write_opc('OP%i 1' %port)

	def off(self, port=1):
		self.write_opc('OP%i 0' %port)
