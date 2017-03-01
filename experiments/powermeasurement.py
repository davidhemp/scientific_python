from time import sleep, time
import matplotlib.pyplot as plt
import numpy as np

import thorlabs
import tti

meter = thorlabs.PM100USB()
supply = tti.QL335P()

supply.idn()
meter.idn()

MAX_VOLTAGE = 0.07

x = []
y = []
start_time = time()
n = 10000
while n > 0:
    sleep(0.5)
    current_power = float(meter.read_power())
    x.append(time())
    y.append(current_power)

    set_voltage = 0.12*np.sin(2*current_power/np.pi)**2
    if set_voltage > MAX_VOLTAGE:
        set_voltage = MAX_VOLTAGE
    supply.set_voltage(set_voltage)
    print(n, current_power, set_voltage)
    n -= 1

plt.plot(x, y)
plt.show()
