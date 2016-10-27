import datetime
from time import time
import logging


class Loader(object):
    def __init__(self, level='DEBUG'):
        self.logger = logging.getLogger("Saving")
        try:
            level_value = eval('logging.%s' %level.upper())
        except AttributeError:
            print('Logging level not found, default to DEBUG')
            level_value = logging.DEBUG
        self.logger.setLevel(level_value)

        # create the logging file handler
        sh = logging.StreamHandler()
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(format_string)
        sh.setFormatter(formatter)
        self.logger.setLevel(level_value)
        self.logger.addHandler(sh)

    def generate_filename(self, ending = ".txt"):
        filename = datetime.now().strftime("%Y-%m-%d-%H_%M_%S") + ending
        self.logger.debug("Genrating filename, %s" %filename)
        return filename

    ## Saving Data ##

    def save_data(self, data, filename = "", comment = ""):
        if len(filename) == 0 or filename.endswith("/"):
            filename += self.generate_filename()
        self.logger.debug("Saving data at %s" %filename)
        with open(filename,'w') as fw:
            if len(comment) > 0:
                fw.write(comment + "\n\n")
            for row in range(len(data[0])):
                line = ""
                for col in range(len(data)):
                    line += "%s," %data[col][row]
                    fw.write(line[:-1] + "\n")

## Loading Data

    def load_data(self):
        """Able to load all raw file types from LeCory or Tektronix as well as
        cvs files. A named tuple is returned with values: x, y, xpsd,
        ypsd."""

        def load_ascii():
            """Loads any ascii file into a numpy array. It populates the array
            line by line as for large files, above 1 GB, the load all method
            ran into memory errors"""
            self.logger.debug("Loading data from %s as ascii" %filename)
            from numpy import zeros
            with open(filename) as f:
                no_lines = 0
                for line in f:
                    no_lines += 1

            x = y = zeros(no_lines)
            with open(filename) as f:
                for line, i in zip(f, range(no_lines)):
                    x[i], y[i] = line.strip().split(',')
            return x, y

        def load_raw():
            self.logger.debug("Loading data from %s as raw" %self.filename)
            with open(self.filename, 'rb') as f:
                raw = f.read()
                try:
                    x, y = InterpretWaveform(raw)
                except Exception as e:
                    if "Length of waveform" in str(e):
                        self.logger.error("Failed to load %s" %self.filename)
                    else:
                        raise
            return x, y

        startime = time()
        if self.filename.endswith((".trc",".raw")):
            from LeCroy import InterpretWaveform
            x, y = load_raw()
        elif self.filename.endswith('.isf'):
            from Tektronix import InterpretWaveform
            x, y = load_raw()
        else:
            x, y = load_ascii()

        endtime = time()
        self.logger.debug("Loading took %i seconds" % int(endtime - startime))
        return x, y
