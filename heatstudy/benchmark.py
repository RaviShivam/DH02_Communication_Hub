import os
import numpy as np
import threading


def calculatePrime():
    count = 3
    primes = [1,2]
    while True:
        bools = [count%i is not 0 for i in range(2, count)]
        if all(bools):
            primes.append(count)
        count += 1

def calculateMatMul():
    x = np.random.rand(800,800)
    y = np.random.rand(800,800)
    np.matmul(x, y)


threading.Thread(target=calculatePrime).start()
threading.Thread(target=calculateMatMul).start()

