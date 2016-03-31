class sabre:
    def LeCroy_save(self,channels,filename,path):
    	import LeCroy
    	try:
    		scope = LeCroy.HDO6104("LCRY-matterwave.clients.soton.ac.uk")
    	except:
    		raise
    	for channel in channels:
            raw = scope.raw(channel)
            filename = loader.generatefilename(ending="_CH%i.raw" %channel)
            loader.simple_save(raw,filename=filename,path=path)

if __name__ == "__main__":
    import sys
    import getopt
    if len(sys.argv)>1:
        import saving
        loader = saving.loader()
        argv = sys.argv[1:]
        filename = loader.generatefilename()
        path = "/home/david/"
        channels = [1]
        device = None
        try:
            opts, args = getopt.getopt(argv,"hlo:p:",["outputfile=","path="])
        except getopt.GetoptError:
            print 'test.py -l -c <channels> -o <outputfile> -p <path>'
            print '<channel> should be a list in square brackets, e.g. [1,2]'
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print 'test.py <device> -o <outputfile> -p <path>'
                print 'Device: -l for LeCroy'
                sys.exit()
            elif opt in ("-l", "--lecroy", "--LeCroy"):
                device = "lecroy"
            elif opt in ("-c","--channels"):
                channels = arg
            elif opt in ("-o", "--ofile"):
                filename = arg
            elif opt in ("-p", "--path"):
                if not arg.endswith("/"):
                    arg += "/"
                path = arg
        if device == "lecroy":
            sabre = sabre()
            sabre.LeCroy_save(channels, filename, path)
        elif device == None:
            print "Device not given, -l for LeCroy"
