class Debugger(object):
    def __init__(self, active=True):
        self.active = active
        
    def print_msg(self, msg):
        if self.active:
            print msg
