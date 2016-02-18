import os,sys
import errno

class PM100USB:
	def __init__(self,address=None,name='THORLABS PM100USB', mask='/dev/usbtmc*'):
		if address is None:
			from useful import SelectAddress
			address = SelectAddress(name,mask)
		self.address = address

	def ask(self,cmd):
		self.write(cmd)
		print self.read()
	
	def query(self,cmd):
		self.write(cmd)
		line = self.read()
		return line.strip()

	def connect(self):
		try:
                	h = open(self.address, 'r+')
                except IOError as e:
			if str(e).find('Permission denied:'):
                                os.system("sudo chmod 777 " + self.address)
                                try:
                                        h = open(self.address, 'r+')
				except: 
					raise
			else:
				raise
		return h

	def write(self,cmd):
		h = self.connect()
		h.write(cmd)
		h.close()
	
	def read(self):
		h = self.connect()
		tmp =h.readline()
		h.close()
		return tmp
