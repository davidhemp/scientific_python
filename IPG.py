class IPG1550:
    def __init__(self, name="IPG1550",address="/dev/serial/by-id/*"):
        if address.endswith("*"):
            from useful import SelectAddress
            address = SelectAddress(name, address)
        try:
                self.connection = open(address, 'r+')
        except IOError as e:
                if str(e).find('Permission denied:'):
                    import os
                    os.system("sudo chmod 777 " + address)
                    self.connection = open(address, 'r+')
                else:
                    raise

    def write(self,cmd):
        if not cmd.endswith("\r"):
            cmd += "\r"
    	self.connection.write(cmd)

    def read(self):
        from time import sleep
        reply = self.connection.read()
        while not reply.endswith('\r') or reply == "":
            sleep(1)
            reply = self.connection.read()
    	return reply

    def ask(self,cmd):
    	self.write(cmd)
        reply = self.read()
        print reply
        return reply

    def query(self,cmd):
        self.connection.write(cmd)
        sleep(1)
    	return self.connection.read()

    def on(self,laserpower=-1):
        if laserpower == -1:
            self.write("EMON")
            self.read()
        else:
            self.write("")

    def off(self):
        self.write("EMOFF")
        self.read()

    def setlaserpower(self,laserpower):
        if laserpower in (int, float):
            return self.ask("SPS %s" laserpower)

    def readlaserpower(self):
        return self.ask("ROP")

    def readlasersetpoint(self):
        return self.ask("RPS")
