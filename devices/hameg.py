class HMP4030:
	def __init__(self,address=None,name='Hameg HMP4030', mask='/dev/ttyUSB*'):
		if address is None:
			from useful import SelectAddress
			address = SelectAddress(name,mask)
		self.address = address
		import serial
		self.connection = serial.Serial(self.address, baudrate = 9600)

	def ask(self,cmd):
		self.write(cmd)
		print self.read()
	
	def query(self,cmd):
		self.write(cmd)
		line = self.read()
		return line.strip()	

	def write(self,cmd):
		if not cmd.endswith('\n'): cmd +='\n'
		self.connection.write(cmd)
	
	def read(self):

		line = ''
		c = ''
		while c != '\n':
			c = self.connection.read(1)
			line += c
		return line.strip()		
	
	def pulse(self,time=5):
		from time import sleep
		print 'Turning laser on'
		self.write('OUTPUT:STATE ON')
		sleep(time)
		self.write('OUTPUT:STATE OFF')
		print 'Laser now off'
