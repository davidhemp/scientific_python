import hameg
from time import sleep

supply = hameg.HMP4030()
supply.ask('*IDN?')
supply.write('*RST')
sleep(0.5)

supply.write('INST:SEL:OUTPUT1')
supply.write('APPLY 12.0,9.5')
#supply.write('SOUR:VOlT:AMPL 6')
#supply.write('SOUR:CURR:AMPL 0.2')
supply.write('OUTPUT:STATE ON')
supply.ask('APPLY?')

sleep (2)
supply.write('OUTPUT:STATE OFF')
suppy.write('APPLY 12.0,0.8')
supply.write('SYST:LOCAL')
