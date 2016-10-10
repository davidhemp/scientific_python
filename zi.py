import socket
from time import sleep

class HF2LI(object):
    def __init__(self, address="192.168.0.100", port=1251, dev="/DEV70/"):
        self.host = address
        self.port = port
        self.dev = dev
        self.connect()

    def connect(self):
        self.s = socket.socket()
        self.s.connect((self.host, self.port))

    def write(self, cmd):
        self.s.send(cmd + "\r\n")
        sleep(2)

    def demod_output_on(self, signal, demod):
        cmd = "%sSIGOUTS/%s/ENABLES/%s 1" %(self.dev,
                                            str(signal-1),
                                            str(demod-1))
        self.write(cmd)

    def demod_output_off(self, signal, demod):
        cmd = "%sSIGOUTS/%s/ENABLES/%s 0" %(self.dev,
                                            str(signal-1),
                                            str(demod-1))
        self.write(cmd)

    def close(self):
        self.write("!CLOSE!")
        self.s.close()

    def shutdown_server(self):
        self.write("!SERVER_OFF!")
        self.s.close()
