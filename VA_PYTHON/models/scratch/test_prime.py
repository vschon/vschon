def calculate(limit):
    primes = []
    divisor = 0
    for current in xrange(limit):
        previous = []
        for divisor in xrange(2, current):
            if current % divisor == 0:
                break
        if divisor == current - 1:
            primes.append(current)
    return primes
