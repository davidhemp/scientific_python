#!/usr/bin/python
class MDO4104B:
	def __init__(self,address="tektronix.phys.soton.ac.uk"):
		import vxi11
		self.address = address
		self.con = vxi11.Instrument(address)
		self.write = self.con.write
		self.read  = self.con.read
		print self.query("*IDN?")

	def query(self,cmd):
		self.write(cmd)
		return(self.read())

	def save_waveform(self,filename,channel="ALL"):
		from time import sleep
		self.write("SAV:WAVE:FILEF INTERN")
		if channel != "ALL":
			if channel in range(1,5):
				channel = "CH" + channel
			else:
				raise Exception("Invalid channel number, 1-4 or all. %s given" %channel)
		cmd = ':SAVE:WAVEFORM %s, "%s"' %(channel,filename)
		self.write(cmd)
		sleep(1)
		while self.query("*OPC?") != '1':
			sleep(1)


def interpret_waveform(raw):
	from numpy import linspace
	from struct import unpack
	cutoff = raw.find("CURVE") #find the start of the curve data in file
	header = raw[:cutoff].split(";")# extract header information
	curvestartpoint = len(raw[cutoff:]) - int(header[0].split(" ")[1])*2 #Removing leading numbers from data
	curve = raw[cutoff + curvestartpoint:]	 #Data section

	xincr = float(header[10].split(" ")[1]) #Time data header information
	xzero = float(header[11].split(" ")[1])
	npoints = int(header[7].split(" ")[1])
	ptoff = int(header[12].split(" ")[1])
	x = linspace(0,xincr*(npoints-ptoff),npoints-ptoff) + xzero #Set up time data

	yzero = float(header[16].split(" ")[1]) #Amplitued data information
	ymulti = float(header[14].split(" ")[1])
	yoff = float(header[15].split(" ")[1])
	if header[5].split(' ')[1] == "MSB":
		fmt = ">" + str(npoints) + 'h'
	else:
		fmt = "<" + str(npoints) + 'h'
	integers = unpack(fmt,curve)
	y = [yzero + ymulti*(i) for i in integers]#Setup Amplitue data
	return x,y

class DPO2024B:
	def __init__(self, address="/dev/usbtmc*"):
		self.address = address
		import usbconnect
		if not self.address.endswith('*'):
			self.connection = usbconnect.usbtmc(self.address)
		else:
			self.connection = usbconnect.usbtmc()
	def write(self,cmd):
		self.connection.write(cmd)
	def read(self):
		self.connection.read()
	def ask(self,cmd):
		self.connection.ask(cmd)
	def query(self,cmd):
		return self.connection.query(cmd)

	def reconnect(self):
		import usbconnect
		if not self.address.endswith('*'):
			self.connection = usbconnect.usbtmc(address)
		else:
			self.connection = usbconnect.usbtmc()

	def raw(self, n=1, pts=1250000):
		self.write(':DATA:SOURCE CH%u\n' % n)
		self.write(':DATA:ENCDG RPB\n') # integers in range 0...255 (width = 1) or 0...65535 (width = 2)
		self.write(':DATA:WIDTH 1\n')
		self.write(':DATA:START 1\n')
		self.write(':DATA:STOP %u\n' % pts)
		tmp = self.query(':CURVE?\n')

		if 0:
			junk = self.read(1) # always says '#'
			n = int(self.read(1)) # integer telling us how many bytes remain in the header
			N = int(self.read(n)) # and this tells us how many bytes are in the data
			CURVE = self.read(N)
			junk = self.read(1) # and this is an end-of-line
		else:
			n = int(tmp[1])
			N = int(tmp[2:(2+n)])
			CURVE = tmp[(2+n):(2+n+N)]

		return CURVE

	def data(self, n=1, pts=125000):
		from time import sleep
		try:
			CURVE = self.raw(n, pts)
		except IOError as e:
			if "Errno 32" in str(e):
				print ("Problem reading from scope...")
				raw_input("Change port before continuing.")
				#self.reconnect()

		params = dict()
		for key in ['XIN', 'XZE', 'YMU', 'YOF']:
			sleep(1)
			params[key] = float(self.query("WFMPRE:%s?\n" % key).strip())
		from pylab import arange, array
		i = [ord(c) for c in CURVE]
		x = arange(0, len(i)) * float(params['XIN']) + float(params['XZE'])
		y = (array(i) - float(params['YOF'])) * float(params['YMU'])
		return (x, y, i)

	def waitOPC(self):
		from time import sleep
		wait = self.query('*OPC?').strip()
		while wait != '1':
			sleep(0.1)
			print wait
			wait = self.query('*OPC?').strip()
		return True
