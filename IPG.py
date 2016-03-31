class IPG1550:
    def __init__(self, name="IPG1550",address="/dev/serial/by-id/*"):
        import usbconnect
        from time import sleep
        self.sleep = sleep
        self.connection = usbconnect.ttyACM(mask = address)

    def write(self,cmd):
        if not cmd.endswith("\r"):
            cmd += "\r"
    	self.connection.write(cmd)

    def read(self):
        return self.connection.read()

    def ask(self,cmd):
        reply = self.query(cmd)
        print reply
        return reply

    def query(self,cmd):
        self.connection.write(cmd)
        self.sleep(1)
    	return self.connection.read()

    def on(self,laserpower=-1):
        self.write("EMON")
        self.sleep(5)

    def off(self):
        self.write("EMOFF")
        self.sleep(5)

    def setlaserpower(self,laserpower):
        self.write("SPS %s" %laserpower)
        self.sleep(5)

    def readlaserpower(self):
        self.write("ROP")
        return self.read()

    def readlasersetpoint(self):
        return self.ask("RPS")
