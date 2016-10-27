import datetime

class TimeData(object):
    def __init__(self, filename, x=[], y=[], fs=0,
        filtered=dict(), filter_response=[], pressure=1e-5, feedback = True):
        self.filename = filename
        self.x = x
        self.y = y
        self.fs = fs
        self.pressure = pressure
        self.feedback = feedback
        self.filtered = filtered
        self.filter_response = filter_response
        self._creation_time = datetime.datetime.now()
        if len(self.x) == 0:
            self.load_data()

    def __repr__(self):
        """Convert to formal string, for repr()."""
        time_string = datetime.datetime.isoformat(self._creation_time)
        s = "<TimeDate object>'%s'%s" %(self.filename, time_string)
        return s

    def __str__(self):
        "Convert to string, for str()."
        time_string = datetime.datetime.isoformat(self._creation_time)
        s = "<TimeDate object> of '%s' created %s" %(
                                        self.filename, time_string)
        return s

    def load_data(self):
        self.x, self.y = Loader.load_data(self)
        self.fs = len(self.x)/(2*self.x[-1])

class PSDData(object):
    def __init__(self, filename, xpsd=[], ypsd=[], centers = dict(),
                    pressure = 0, noise = 4*10**(-14)):
        self.filename = filename
        self.xpsd = xpsd
        self.ypsd = ypsd
        self.centers = centers
        self.cuts = dict()
        self.fit_parms = dict()
        self.fit_errors = dict()
        self.pressure = pressure
        self.noise = noise
