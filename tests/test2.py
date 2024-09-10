from random import random
from time import perf_counter
import numpy as np
import dielepy as dp
import calculations as cc
from scipy.special import factorial2, factorial

COUNT = 500000  # Change this value depending on the speed of your computer
DATA = [(random() + 0.05) for _ in range(COUNT)]


def ellipK1(k):
    ans = 1.
    term = 1.
    for n in range(1, 150):
        n_part = (1. - 0.5 / n)
        term = term * n_part * n_part * k * k
        ans = ans + term
    return 0.5 * np.pi * ans


def ellipK2(k):
    n = np.arange(150)
    terms = (factorial2(2 * n - 1) * k ** n / (factorial(n) * 2 ** n)) ** 2
    terms[np.where(terms == np.inf)] = 0
    return np.sum(terms) * 0.5 * np.pi


def test(fn, name):
    start = perf_counter()
    result = fn(DATA)
    duration = perf_counter() - start
    print('{} took {:.3f} seconds\n\n'.format(name, duration))


if __name__ == "__main__":
    print('Running benchmarks with COUNT = {}'.format(COUNT))
    # for th in [0.08, 0.1, .2, .3, .4, .5]:
    #     print("Python k = {:.8e}".format(cc.k_mat(10, th)))
    #     print("C++    k = {:.8e}".format(dp.k_thin(20, 10, th)))
    print("Python k = {:.8e}".format(cc.k_air(10)))
    print("C++    k = {:.8e}".format(dp.k_thick(20, 10)))

    test(lambda d: [cc.k_air(10) for x in d], '[k_air(20, 10, x) for x in d] (Python implementation)')
    test(lambda d: [dp.k_thick(20, 10) for x in d], '[dp.k_thick(20, 10, x) for x in d] (C++ implementation)')

    # test(lambda d: [k(20, 10, x) for x in d], '[k(20, 10, x) for x in d] (Python implementation)')
    # test(lambda d: [dp.k_thin(20, 10, x) for x in d], '[dp.k_thin(20, 10, x) for x in d] (C++ implementation)')

    # test(lambda d: [cc.geometric_capacitance(10, x) for x in d],
    #     '[cc.geometric_capacitance(10, x) for x in d] (Python implementation)')
    # test(lambda d: [dp.geometric_capacitance(20, 10, x, 50, 1000) for x in d],
    #     '[dp.geometric_capacitance(10, x) for x in d] (C++ implementation)')

    test(lambda d: [dp.ellint_ratio(x) for x in d],
         '[cc.geometric_capacitance(10, x) for x in d] (Python implementation)')
    test(lambda d: [dp.ellint_ratio_approx(x) for x in d],
         '[dp.geometric_capacitance(10, x) for x in d] (C++ implementation)')

    print("Python C = {:.8e}".format(cc.bare_capacitance(10)))
    print("C++    C = {:.8e}".format(dp.capacitance_bare(20, 10, 500, 52, 1000, 3.9)))
    test(lambda d: [cc.bare_capacitance(10+x) for x in d],
        '[cc.bare_capacitance(10, x) for x in d] (Python implementation)')
    test(lambda d: [dp.capacitance_bare(20, 10+x, 500, 52, 1000, 3.9) for x in d],
        '[dp.bare_interdigital(10, x) for x in d] (C++ implementation)')
