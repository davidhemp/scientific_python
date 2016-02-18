def factor(n):
	i=2
	while i * i < n:
		while n%i == 0:
			n = n / i
		i = i + 1
		print i
	return n

def get_primes(maxvalue):
	current = 2
	while current<maxvalue:
		print next(gen_primes(current))
		current +=1
	
def gen_primes(number):
	while True:
		if is_prime(number):
			yield number
		number+=1

def is_prime(number):
    from numpy import sqrt
    if number > 1:
	if number == 2:
	    return True
	if number % 2 == 0:
	    return False
	for current in range(3, int(sqrt(number) + 1), 2):
	    if number % current == 0: 
	        return False
	return True
    return False
