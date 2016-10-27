#!/usr/bin/python
import os

class Device(object):
	def __init__(self, name="Generic device", address='/dev/*', baudrate=19200):
		import serial
		if address.endswith('*'):
			from useful import SelectAddress
			address = SelectAddress(name, address)
		for i in range(3):
			try:
				self.conn = serial.Serial(address, baudrate=baudrate)
				break
			except IOError as e:
				if str(e).find('Permission denied:'):
					import os
					print "Connection failed, try %i" %i
					os.system("sudo chmod 777 " + address)

	def write(self,cmd):
		if not cmd.endswith('\n'): cmd += '\n'
		self.conn.write(cmd)

	def read(self):
		line = self.conn.readline()
		return line.strip()

	def ask(self,cmd):
		print self.query(cmd)

	def query(self,cmd):
		from time import sleep
		self.write(cmd)
		sleep(0.2)
		return self.read()

	def idn(self):
		self.ask("*IDN?")

	def opc(self):
		q = 0
		while q != 1:
			q = int(self.query("*OPC?"))

	def write_opc(self, cmd):
		try:
			self.write(cmd)
		finally:
			self.opc()

	def reset(self):
		self.write("*RST")

class ttyACM(Device):
	def __init__(self, name='Generic ttyACM', address='/dev/ttyACM*'):
		super(ttyACM, self).__init__(name, address)

	def release(self):
		self.conn.write('LOCAL\n')
		self.conn.close()


class ttyUSB(Device):
	def __init__(self, name="Generic ttyUSB device", address="/dev/ttyUSB*"):
		super(ttyUSB, self).__init__(name, address)


class usbtmc(Device):
	def __init__(self, name='Generic usbtmc device', address='/dev/usbtmc*'):
		self.ADDRESS = address
		if address.endswith('*'):
			from useful import SelectAddress
			self.ADDRESS = SelectAddress(name, address)
		for i in range(3):
			try:
				self.CONN = os.open(self.ADDRESS, os.O_RDWR)
				break
			except IOError as e:
				if str(e).find('Permission denied:'):
					os.system("sudo chmod 777 " + self.address)
			print "Connection failed, try %i" %i

	def write(self,cmd):
		os.write(self.CONN, cmd)

	def read(self, length=None):
		if length is None:
			length = 4000
		return os.read(self.CONN, length)
