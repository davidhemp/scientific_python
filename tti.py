class TG5011:
	def __init__(self,address='/dev/ttyACM*'):
		import usbconnect
		if not address.endswith('*'):
			self.connection = usbconnect.ttyACM(address)
		else:
			self.connection = usbconnect.ttyACM()

	def write(self,cmd):
		self.connection.write(cmd.upper())
	def read(self):
		self.connection.read()
	def ask(self,cmd):
		if not cmd.endswith('?'):cmd+='?'
		self.connection.ask(cmd.upper())
	def query(self,cmd):
		if not cmd.endswith('?'):cmd+='?'
		return self.connection.query(cmd.upper())
	def release(self):
		self.connection.release()
	def setup(self,amp=0.1,freq=9.45*10**6,wave='SINE'):		
		siggen = self.connection		
		if wave.upper() == 'SIN':
			wave = 'SINE'
		
		siggen.write('WAVE %s' %wave)
		siggen.write('AMPL %f' %amp)
		siggen.write('FREQ %f' %freq)




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
