import dielepy as dp
import matplotlib.pylab as plt
import numpy as np

plt.rcParams["figure.autolayout"] = True


def k_array(u, g, res=10000):
    """

    :param u:
    :param g:
    :param res:
    :return:
    """
    hs = np.linspace(0, 1, res)
    ks = np.zeros(res)
    for ii, h in enumerate(hs):
        ks[ii] = dp.k_thin(u, g, h)
    return hs, ks


def plot_modulus():
    for g in [2.5, 5, 7.5, 10, 12.5, 15, 17.5]:
        plt.plot(*k_array(20, g), label=f"d = {g} \u03BCm")
    plt.xlim([0, 1])
    plt.ylim([0, 1e-9])
    plt.xlabel('$h_{i}$ (\u03BCm)')
    plt.ylabel('$k_{i}$')
    plt.legend(loc='upper right')
    plt.title('Elliptic Integral Modulus for 20 \u03BCm unit cell')


def plot_ellint_ratio():
    fig, (ax1, ax2) = plt.subplots(1, 2)
    res = 100000
    scale = .5
    ks = np.linspace(0, scale, res)
    ratios = np.zeros(res)
    for ii, k in enumerate(ks):
        ratios[ii] = dp.ellint_ratio(k)
    ax1.plot(ks, ratios, label="using cmath K(k) function")
    res = 100
    ks = np.linspace(0, scale, res)
    ratios2 = np.zeros(res)
    for ii, k in enumerate(ks):
        ratios2[ii] = dp.ellint_ratio_approx(k)

    ax1.scatter(ks, ratios2, facecolors='none', edgecolors='r', label="using log based approximation")
    ax1.set_xlabel('$k$')
    ax1.set_ylabel('$\\frac{K(k)}{K(k^{\\prime})}$', rotation=0, labelpad=15)
    ax1.set_xlim([0, scale])
    ax1.set_ylim([0, 1])
    ax1.legend(loc='upper left')

    res = 10000
    scale = 1e-7
    ks = np.linspace(0, scale, res)
    ratios = np.zeros(res)
    for ii, k in enumerate(ks):
        ratios[ii] = dp.ellint_ratio(k)
    ax2.plot(ks, ratios, label="using cmath K(k) function")
    res = 100
    ks = np.linspace(scale/res, scale, res)
    ratios2 = np.zeros(res)
    for ii, k in enumerate(ks):
        ratios2[ii] = dp.ellint_ratio_approx(k)

    ax2.scatter(ks, ratios2, facecolors='none', edgecolors='r', label="using log based approximation")
    ax2.set_xlabel('$k$')
    ax2.set_ylabel('$\\frac{K(k)}{K(k^{\\prime})}$', rotation=0, labelpad=15)
    ax2.set_xlim([0, scale])
    ax2.set_ylim([0, .1])
    #ax2.legend(loc='upper left')

    fig.suptitle("Elliptic integral ratio")


if __name__ == "__main__":
    plot_ellint_ratio()
    plt.show()
