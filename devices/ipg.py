#!/usr/bin/python
from time import sleep

import usbconnect


class IPG1550(usbconnect.Device):
    def __init__(self, name="IPG1550",address="/dev/serial/by-id/*"):
        super(IPG1550, self).__init__(name, address, baudrate=9600)

    def write(self,cmd):
        if not cmd.endswith("\r"):
            cmd += "\r"
    	self.conn.write(cmd)
        sleep(5)

    def read(self):
        line = ""
        while not line.endswith("\r"):
            line += self.conn.read()

        return line.strip("\r")
    def on(self,laserpower=-1):
        self.write("EMON")
        self.read()

    def off(self):
        self.write("EMOFF")
        self.read()

    def setlaserpower(self,laserpower):
        self.write("SPS %s" %laserpower)
        self.read()

    def readlaserpower(self):
        self.write("ROP")
        return self.read()

    def readlasersetpoint(self):
        return self.ask("RPS")
