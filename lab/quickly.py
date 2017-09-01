'''
For when I don't want to use the whole Data class or I need to do something weird
'''

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
    '''
    Load and average the PSD data of a number of files

    Parameters
    ----------
    first_file : string
        Full file part of the first file
    count : int
        The total number of files (including first_file) to be loaded
    fs : int/float (optional)
        Override of the PSD sample Frequency (default is 10^6)

    Returns
    -------
    xpsd : array
        Frequency data
    ypsd : array
        Averaged amplitude data
    ypsd_std : array
        Standard diviation of the amplitude data

    ''''
    rgx = r"(.*?)\_([0-9]+)\.trc"
    path, start = re.search(rgx, first_file).groups()
    xpsd, ypsd = loadNpsd(first_file)
    count -= 1
    n = 1
    ypsd_list = [ypsd]
    while count > 0: # Fast fail.
        filename = "{}_{:05d}.trc".format(path, (int(start) + count))
        print(filename)
        try:
            _xpsd, _ypsd = loadNpsd(filename, fs)
            ypsd += _ypsd
            ypsd_list.append(_ypsd)
            n += 1
        except Exception as e:
            if "Length" in str(e):
                pass
            else:
                raise
        finally:
            count -= 1
    return xpsd, ypsd/n, np.std(ypsd_list, axis=0)

def loadNpsd(filename, fs=None):
    '''
    Load and generate PSD for the given file

    Parameters
    ----------
    filename : string
        Full file path to the file to be loaded
    fs : int/float (optional)
        Override for the PSD sample frequency

    Returns
    -------
    xpsd : array
        Frequency data
    ypsd : array
        PSD amplitude data
    ''''
    print(filename)
    x, y = loader.load_data(filename)
    if not fs:
        fs = len(x)/(2*x[-1])
    return processor.psd(x=x, y=y, fs=fs)

def plot_psd(x=None,y=None, filename=None):
    '''
    If a filename is given then load and PSD that file then plot the result,
    else try to plot x and y as a PSD. If neither x-y data or filename the
    function will error.

    Parameters
    ----------
    x : array
        Frequency data
    y : array
        PSD amplitude data
    filename : string
        Full file path to the file to be loaded

    Returns
    -------
        True
    '''

    if filename:
        plotter.plot_psd(*loadNpsd(filename))
    else:
        plotter.plot_psd(x,y)
    plt.show()

def load_AC_filter(filename, fs=None):
    '''
    Simple low pass filter at 1000 Hz to cut out AC noise sources.

    Parameters
    ----------
    filename : string
        File to be loaded and filtered
    fs : int/float (optional)
        Override for the PSD sample frequency

    Returns
    -------
    x : array
        Time data
    y : array
        Filtered amplitude
    '''
    
    x, y = loader.load_data(filename)
    if not fs:
        fs = len(x)/(2*x[-1])
    y_low, response = processor.butterworth_filter(y,
                                                fs,
                                                lowcut = 1000,
                                                btype = 'low')
    return x, y_low
