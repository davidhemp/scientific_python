''' experimental '''

import os

import pylab as p
from scipy.optimize import basinhopping

import myplots as mp
import saving

# loaddir = "/media/lazarus/David/rawdata/re-heating/"
# os.chdir(loaddir)

class feedback(object):
    def __init__(self, data):
        self.data = data

    def sum_of_squares(self, parms):
        model = mp.func(self.cut_xpsd, *parms)
        return sum(p.square(model/self.cut_ypsd - self.cut_ypsd/model))

    def xpsdrange(self):
        xpsd, ypsd = mp.psd_ave(self.data, chucks=5)
        self.cut_xpsd = xpsd[5100:6100]
        self.cut_ypsd = ypsd[5100:6100]

    def fitting(self):
        self.xpsdrange()
        alpha = 30e3
        f0 = 56399
        damping = 6
        ret = basinhopping(self.sum_of_squares, [alpha, f0, damping])
        print(zip(ret.x,['alpha', 'f0', 'damping']))
        self.y_fit = mp.func(self.cut_xpsd, *ret.x)

    def plot(self):
        self.fitting()
        p.semilogy(self.cut_xpsd, self.cut_ypsd)
        p.semilogy(self.cut_xpsd, self.y_fit)

def run(filename):
    def with_feedback(data):
        x = data[0][:len(data[0])*1/10]
        x = x - x[0]
        y = data[1][:len(data[1])*1/10]
        return [x, y]

    def without_feedback(data):
        x = data[0][len(data[0])*9/10:]
        x -=x[0]
        y = data[1][len(data[1])*9/10:]
        return [x, y]

    p.subplot(1,2,1)

    data = with_feedback(saving.loaddata(filename))
    _inst = feedback(data)
    _inst.plot()

    p.subplot(1,2,2)
    _inst.data = without_feedback(saving.loaddata(filename))
    _inst.plot()
    p.show()

if __name__ == "__main__":
    run("C1_00000.trc")
