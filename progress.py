import time
import sys

class progressBar:

	def simpleBar(self,currentPercent,starttime):
		from sys import stdout
		from time import time

		progressBar = "[" #writes the simple bar, e.g. "[===   ] 50%"
		for j in range(currentPercent):
			progressBar += "="
		for j in range(currentPercent,100):
			progressBar += " "
		progressBar = progressBar + "] "
		sys.stdout.write("\r%s%d%%" %(progressBar,currentPercent))

		currentduration = time() - starttime #Calculate time to finish.
		try:
			finishtime = (currentduration/(currentPercent)) * 100
		except ZeroDivisionError:
			finishtime = 9999
		timeremaining = finishtime - currentduration
		sys.stdout.write(' %d:%02d / %d:%02d Time remaining     ' \
			% (finishtime / 60, finishtime % 60, \
				timeremaining / 60, timeremaining % 60)) #Write time remaining
		sys.stdout.flush() #Output to screen
