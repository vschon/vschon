def calculate(long limit):
    cdef long current
    cdef long divisor
    primes = []
    divisor = 0
    for current from 0 <= current < limit:
        previous = []
        for divisor from 2 <= divisor < current:
            if current % divisor == 0:
                break
        if divisor == current - 1:
            primes.append(current)
    return primes
