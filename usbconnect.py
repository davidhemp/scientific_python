#!/usr/bin/python
class usbtmc:
	def __init__(self, address=None, name='Generic USBtmc', mask='/dev/usbtmc*'):
		if address is None:
			from useful import SelectAddress
			address = SelectAddress(name, mask)
		self.address = address

	def connect(self):
                try:
                        h = open(self.address, 'r+')
                except IOError as e:
                        if str(e).find('Permission denied:'):
                        	import os
                                os.system("sudo chmod 777 " + self.address)
                                try:
                                        h = open(self.address, 'r+')
                                except:
                                        raise
                        else:
                                raise
                return h

	def write(self, cmd):
		h = self.connect()
		if not cmd.endswith('\n'): cmd += '\n'
		h.write(cmd)
		h.close()

	def read(self,l=-1):
		h = self.connect()
		if l<0:
			line = h.readline()
		elif l > 0:
			line = h.read(l)
		h.close()
		return line.rstrip('\n')

	def ask(self, cmd):
		self.write(cmd)
		print self.read()

	def query(self,cmd):
		self.write(cmd)
		line=self.read()
		return line.strip()

class ttyACM:
	def __init__(self,device=None,name='Generic ttyACM',mask='/dev/ttyACM*'):
		import serial
		if device is None:
			from useful import SelectAddress
			address = SelectAddress(name,mask)
		try:
			self.device = serial.Serial(address)
		except IOError as e:
			if str(e).find('Permission denied:'):
				import os
				os.system("sudo chmod 777 " + address)
				try:
					self.device = serial.Serial(address)
				except:
					raise
			else:
				raise

	def release(self):
		self.device.write('LOCAL\n')
		self.device.close()

	def write(self,cmd):
		if not cmd.endswith('\n'): cmd += '\n'
		self.device.write(cmd)

	def read(self):
		#line = self.device.readline()
		line = ""
		while not line.endswith("\r") or not line.endswith("\n"):
			line += self.device.read()
		return line.strip()

	def ask(self,cmd):
		self.write(cmd)
		print self.read()

	def query(self,cmd):
		self.write(cmd)
		return self.read()
