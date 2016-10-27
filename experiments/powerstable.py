from time import sleep, time

import matplotlib.pyplot as plt
import numpy as np

import tti
import thorlabs

meter = thorlabs.PM100USB()
meter.setup(1550)
siggen = tti.TG5011()
supply = tti.QL335P()

MAX_VOLTAGE = 0.07
SET_POINT = 1.6
TARGET_POINT = 0.03
integrator = 0
difference = 0

KP = 1.
KI = 2.
KD = 2.
siggen.dcoffset(3.0)
siggen.on()

print('Turn on laser')
x = []
y = []
p = []
n = 2*60*60/0.2
while n > 0:
    while n > (2*60*60/0.2 - 60/0.2):
        sleep(0.2)
        current_power = float(meter.read_power())

        # set_voltage = 0.12*np.sin(2*current_power/np.pi)
        set_voltage = 2*current_power
        if set_voltage > MAX_VOLTAGE:
            set_voltage = MAX_VOLTAGE
        supply.set_voltage(set_voltage)
        n -= 60/0.2
    if n == (2*60*60/0.2 - 60/0.2):
        siggen.dcoffset(SET_POINT)
        print('PID loop started')
    sleep(0.2)
    current_power = meter.read_power()
    error =  current_power - TARGET_POINT

    p_value = KP*error
    integrator = integrator + error
    i_value = -integrator*KI
    d_value = KD*(error - difference)

    pid = SET_POINT + p_value + i_value# + d_value
    print(current_power, pid, p_value, i_value)
    siggen.dcoffset(pid)
    x.append(time())
    y.append(current_power)
    p.append(pid)
    n -= 1

plt.plot(x, y, label='Power')
plt.plt(x, p, label='PID')
plt.show()
