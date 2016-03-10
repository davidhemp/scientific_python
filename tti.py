class TG5011:
	def __init__(self,address='/dev/ttyACM*'):
		import usbconnect
		if not address.endswith('*'):
			self.siggen = usbconnect.ttyACM(address)
		else:
			self.siggen = usbconnect.ttyACM()

	def write(self,cmd):
		self.siggen.write(cmd.upper())
	def read(self):
		self.siggen.read()
	def ask(self,cmd):
		if not cmd.endswith('?'):
			cmd+='?'
		self.siggen.ask(cmd.upper())
	def query(self,cmd):
		if not cmd.endswith('?'):
			cmd+='?'
		return self.siggen.query(cmd.upper())
	def release(self):
		self.siggen.release()
	def setup(self,amp=0.1,freq=9.45*10**6,wave='SINE'):
		if wave.upper() == 'SIN':
			wave = 'SINE'

		self.siggen.write('WAVE %s' %wave)
		self.siggen.write('AMPL %f' %amp)
		self.siggen.write('FREQ %f' %freq)
	def amp(self,amp):
		self.siggen.write('AMPL %f' %amp)
	def freq(self,freq):
		self.siggen.write('FREQ %f' %freq)
	def on(self):
		self.siggen.write('OUTPUT ON')
	def off(self):
		self.siggen.write('OUTPUT OFF')



class QL335P:
	def __init__(self, address=None, name='TTI QL335P', mask='/dev/ttyUSB*'):
		import serial
		if address is None:
			from useful import SelectAddress
			address = SelectAddress(name, mask)

		self.address = address

	def write(self,cmd):
		if not cmd.endswith('\n'): cmd +='\n'
		import serial
		s = serial.Serial(self.address, baudrate = 19200)
		s.write(cmd)
		s.close()

	def read(self):
		import serial
		s = serial.Serial(self.address, baudrate = 19200)
		line = ' '
		while line[-1] != '\n':
			line+=s.read()
		line = line.strip()
		return line

	def ask(self,cmd):
		self.write(cmd)
		return self.read()
