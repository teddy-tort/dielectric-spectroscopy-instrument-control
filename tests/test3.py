import matplotlib.pylab as plt
import numpy as np
import dielepy as dp


# eps_0 = 8.85418781762e-6
#
# thicknesses = np.linspace(0, 5, 500)
# ellint = np.zeros(500)
# pp = np.zeros(500)
#
# for ii, x in enumerate(thicknesses):
#     k = dp.k_thin(20, 10, x)
#     bare = dp.bare_interdigital(20, 10, 500, 50, 1000, 3.9)
#     ellint[ii] = bare + eps_0 * 49000. * dp.ellint_over_comp(k)
#     pp[ii] = bare + eps_0 * 49000 * dp.ellint_over_comp_approx(k)

ks = np.linspace(0, 1e-7, 500)
exacts = np.zeros(500)
aproxs = np.zeros(500)
aprox2 = np.zeros(500)

for ii, k in enumerate(ks):
    exacts[ii] = dp.ellint_over_comp(k)
    aproxs[ii] = dp.ellint_over_comp_approx(k)
    aprox2[ii] = np.pi*(1/np.log(16/k/k)+0.1*0.1/(2*np.log(16/k/k)**2))

if __name__ == "__main__":
    # plt.plot(thicknesses, ellint)
    # plt.plot(thicknesses, pp)
    plt.plot(ks, exacts, 'x')
    plt.plot(ks, aproxs, 'o')
    plt.plot(ks, aprox2, '.')
    plt.show()
