from timeit import Timer

t = Timer('prime.calculate(10000)', 'import prime')
reps = 10
print "Pure python: %0.3f" %(sum(t.repeat(repeat=reps, number=1)) / reps)

# t = Timer('c_prime.calculate(10000)', 'import c_prime')
# reps = 10
# print "Compile of python: %0.3f" %(sum(t.repeat(repeat=reps, number=1)) / reps)
#
# t = Timer('c_optimized_prime.calculate(10000)', 'import c_optimized_prime')
# reps = 10
# print "Optimized cython: %0.3f" %(sum(t.repeat(repeat=reps, number=1)) / reps)
