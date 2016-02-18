def divide(x,y):
	try:
		result = x/y
	except ZeroDivisionError:
		print "division by zero error"
		raise
	else:
		print "result is", result


