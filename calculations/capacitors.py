import numpy as np
from scipy import special
from scipy import optimize
from decimal import Decimal

eps0 = 8.85e-6  # electric constant in nF/um
epsS = 3.9      # relative dielectric constant of silica
hS = 500        # [um] silica substrate thickness
N = 52          # number of fingers on capacitor
L = 1000        # [um] capacitor finger length
u = 20          # [um] gap-finger unit cell size


def sinhpi4(x: float, h: float) -> float:
    """
    Calculate sinh for pi*x/(4h)
    :param x: value in numerator
    :param h: value in denominator
    :return: sinh
    """
    return np.sinh(np.pi * x / (4 * h))


def k_air(g: float) -> float:
    """
    Calculates k for K(k) calculation for h -> inf
    :param g: gap size in micron
    :return: k for K(k)
    """
    return (u - g) / (u + g) * np.sqrt(2 * (u - g) / (2 * u - g))


def k_mat(g: float, h: float) -> float:
    """
    Calculates k for K(k) calculation down to 0.1 um material thickness
    :param g: gap size [um]
    :param h: thickness of film [um]
    :return: argument for elliptic integral
    """
    return sinhpi4(u - g, h) / sinhpi4(u + g, h) * np.sqrt((sinhpi4(3 * u - g, h) ** 2 - sinhpi4(u + g, h) ** 2)
                                                           / (sinhpi4(3 * u - g, h) ** 2 - sinhpi4(u - g, h) ** 2))


def elliptic_over_comp(k: float) -> float:
    """
    Calculate the elliptic integral of the first kind divided by the elliptic integral of the second kind
    :param k: the argument of the elliptic integral
    :return: K(k)/K'(k)
    """
    return special.ellipk(k ** 2) / special.ellipk(1 - k**2)


def bare_capacitance(g: float) -> float:
    """
    Calculate the capacitance of a capacitor with a certain gap size
    :param g: gap size in micron
    :return: capacitance in picofarads
    """
    ka = k_air(g)
    ks = k_mat(g, hS)
    return 2 * (N - 1) * L * eps0 * (elliptic_over_comp(ka) + (epsS - 1) * elliptic_over_comp(ks) / 2)


def elliptic_over_comp_small_k(k: float) -> float:
    """
    Small k approximation to the elliptic integral divided by its complement
    :param k: inputs of elliptic integrals calculated from k_ functions
    :return: approximation of elliptic integral divided by its compliment
    """
    ellip_integral = np.pi / 2 * (1 + k / 4 + 9 * k / 64)
    ellip_integral_comp = 5 / 2 * np.log(2) - np.log(k)
    return ellip_integral / ellip_integral_comp


def find_gap(bare_c_val: float) -> float:
    """
    Use a zero-finder to invert the bare capacitance calculation to calculate the gap size
    :param bare_c_val: capacitance in picofarads
    :return: gap size in micron
    """
    def func(g):
        return bare_capacitance(g) - bare_c_val
    return float(optimize.fsolve(func, np.array([10.]))[0])


def geometric_capacitance(g: float, h: float) -> float:
    """
    Calculates the geometric capacitance for an interdigital capacitor using the small k
    :param g: gap size in micron
    :param h: thickness of film in micron
    :return: C_geo value in picofarads
    """
    k = k_mat(h, g)
    return eps0 * (N - 1) * L * np.pi * (1 + k / 4) / (5 * np.log(2) - 2 * np.log(k))


def k_film(g: float, h: float) -> float:
    """
    Calculates k for K(k) calculation for thin films down to 60 nm
    :param g: gap size [um]
    :param h: thickness of film [nm]
    :return: argument for elliptic integral
    """
    h /= 1e3    # convert from nm to um
    part1 = sinhpi4(3 * u - g, h)
    part2 = sinhpi4(u + g, h)
    part3 = sinhpi4(3 * u - g, h)
    part4 = sinhpi4(u - g, h)
    outside_sqrt = part4 / part2
    inside_sqrt = float((Decimal(part1) ** 2 - Decimal(part2) ** 2) / (Decimal(part3) ** 2 - Decimal(part4) ** 2))
    return outside_sqrt * np.sqrt(inside_sqrt)


if __name__ == "__main__":
    # print(special.ellipk(0.1))
    # print(special.ellipk(0.2))
    # print(special.ellipk(0.3))

    import dielepy as dp
    print(bare_capacitance(10))
    print(dp.bare_interdigital(u, 10, hS, N, L, epsS), end="\n\n")
    print(k_mat(10, .08))
    print(dp.k_thin(u, 10, .08), end="\n\n")
    print(elliptic_over_comp(0.1))
    # print(dp.)


    # def comp_approx(k):
    #     ln2 = np.log(2)
    #     ln1_k = np.log(1-k)
    #     term1 = 2*ln2 - 0.5*ln1_k
    #     term2 = (0.5 * ln2 - 0.25 - 0.125 * ln1_k) * (1-k)
    #     term3 = 0.0234375 * (3*ln1_k-12*ln2+7)*(1-k)**2
    #     term4 = (15*5*ln1_k-60*5*ln2+37)*(1-k)**3 / 1536
    #     print(term1)
    #     print(term2+term1)
    #     print(term1+term2-term3)
    #     return term1 + term2 - term3 - term4
    # print(comp_approx(.999))
    # print(special.ellipk(.999))
