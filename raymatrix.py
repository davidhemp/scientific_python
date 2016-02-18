def freespace(d):
	return [[1,d],[0,01]]

def flatrefraction(n1,n2):
	return [[1,0],[0,n1/n2]]

def curvedrefraction(n1,n2,R):
	return [[1,0],[(n1-n2)/(R*n2),n1*n2]]	


