#!/usr/bin/python
class HDO6104:
	def __init__(self, address='152.78.195.166'):
                self.address = address
                import vxi11
                self.connection = vxi11.Instrument(address)
                self.write = self.connection.write
                self.read  = self.connection.read
                self.ask   = self.connection.ask
                self.read_raw = self.connection.read_raw

        def raw(self, channel=1):
                self.waitOPC()
                self.write('COMM_FORMAT DEF9,WORD,BIN')
                self.write('C%u:WAVEFORM?' % channel)
                return self.read_raw()
        
        def data(self, channel=1):
                raw = self.raw(channel) # Grab waveform from scope
                return InterpretWaveform(raw)

        def waitOPC(self):
                from time import sleep
                self.write('WAIT')
                while not self.opc():
                        sleep(1)
                
        def opc(self):
                return self.ask('*OPC?')[-1] == '1'
