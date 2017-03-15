import re

import saving
import process
import myplots

loader = saving.Loader()
processor = process.Processor()
plotter = myplots.Plotter()
plt = myplots.plt
np = process.np

def loadNave(first_file, count=10, fs=None):
    rgx = r"(.*?)\_([0-9]+)\.trc"
    path, start = re.search(rgx, first_file).groups()
    xpsd, ypsd = loadNpsd(first_file)
    count -= 1
    n = 0
    while count > 0:
        filename = "{}_{:05d}.trc".format(path, (int(start) + count))
        try:
            _xpsd, _ypsd = loadNpsd(filename, fs)
            ypsd += _ypsd
            n += 1
        except Exception as e:
            if "length" in str(e):
                pass
            else:
                raise
        finally:
            count -= 1
    return xpsd, ypsd/n

def loadNpsd(filename, fs=None):
    x, y = loader.load_data(filename)
    if not fs:
        fs = len(x)/(2*x[-1])
    return processor.psd(x=x, y=y, fs=fs)

def plot_psd(x=None,y=None, filename=None):
    if filename:
        plotter.plot_psd(*loadNpsd(filename))
    else:
        plotter.plot_psd(x,y)
    plt.show()

def load_AC_filter(filename, fs=None):
    x, y = loader.load_data(filename)
    if not fs:
        fs = len(x)/(2*x[-1])
    y_low, response = processor.butterworth_filter(y,
                                                fs,
                                                lowcut = 1000,
                                                btype = 'low')
    return x, y_low
