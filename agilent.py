class DSO1052B:
	def __init__(self, address="/dev/usbtmc*"):
		import usbconnect
		self.address = address
		if not address.endswith('*'):
			self.connection = usbconnect.usbtmc(address)
		else:
			self.connection = usbconnect.usbtmc()
	def write(self,cmd):
		self.connection.write(cmd.upper())
	def read(self,l=-1):
		return self.connection.read(l)
	def ask(self,cmd):
		self.connection.ask(cmd.upper())
	def query(self,cmd):
		return self.connection.query(cmd.upper())
	def waitOPC(self):
		from time import sleep
		i=self.connection.query('*OPC?\n')
		while i == 0:
			sleep(0.1)
			i=self.connection.query('*OPC?\n')
		return

	def measure(self,cmd,channel=1):
		if cmd is 'VPP' or 'vpp':
			value = self.query(':MEAS:VPP? %f' %channel)
		return float(value)

	def waveform(self, channel, retake=True,points = 600,format='BYTE'):
		from time import sleep
		import numpy as np	
		self.waitOPC()	
		self.write(':WAVEFORM:SOURCE CHANNEL%u' % channel)
		self.write(':WAVEFORM:FORMAT %s' %format.upper())
		self.write(':WAVEFORM:POINTS:MODE RAW')
		self.write(':WAVEFORM:POINTS %s' %points)#8192')
		self.write(':WAVEFORM:DATA?')
		sleep(1)
		if format == 'ASCII':
			raw = self.read(250000)
		else:			
			raw = self.read(points+points*int(0.02))
		
		NN = int(raw[1])
		N = int(raw[2:2+NN])
		data = raw[2+NN:]
		if len(data) != N:
			raise Exception('Unable to read all data: %u of %u' % (len(data), N))

		i = np.array([ord(v) for v in data])
		if format == 'ASCII':
			y = raw
		else:
			print format
			y0 = float(self.query(':WAVEFORM:YORIGIN?'))
			dy = float(self.query(':WAVEFORM:YINCREMENT?'))
			yr = float(self.query(':WAVEFORM:YREF?'))
			y = (yr-i)*dy-y0

		t0 = float(self.query(':WAVEFORM:XORIGIN?'))
		dt = float(self.query(':WAVEFORM:XINCREMENT?'))
		t = np.arange(0,len(y)*dt,dt)
		return t,y

