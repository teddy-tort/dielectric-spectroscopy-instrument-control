"""
Created on Wed Aug 30 10:21:34 2017

@author: Teddy
"""
import numpy as np


def calculate_filling(c_bare, c_reference, c_loading, c_material, eps_substrate=4.8):
    """
    Calculates the %fill and dielectric constant of loaded material
    Inputs:
    c_bare - the bare capacitance in pF
    c_reference - the capacitance when the loading material is added
                  (e.g. benzene, perfluorhexane) in pF
    c_loading - the capacitance after loading the material in
                (e.g. perfluorohexane/GBA mix) in pF
    c_material - the capacitance after the volatile loading material
                 evaporates away in pF
    c_pp -  probe to probe capacitance (optional details...) in fF
    eps_substrate - dielectric constant of the substrate (4.8 for silica)
    """
    c_bare = c_bare
    c_geometric = c_bare / eps_substrate
    eps_reference = (c_reference - c_bare) / c_geometric + 1.
    eps_eff_air = (c_material - c_bare) / c_geometric + 1.
    eps_eff_load = (c_loading - c_bare) / c_geometric + 1.
    filling = 1 - (eps_eff_load - eps_eff_air) / (eps_reference - 1)
    eps_material = (eps_eff_air - 1 + filling) / filling
    print('Geometric capacitance = %.2f fF' % (c_geometric * 1000.))
    print('Dielectric constant of loading material = %.2f' % eps_reference)
    print('%% Filling = %.2f %%' % (filling * 100.))
    print('Dielectric constant of loaded material = %.2f' % eps_material)

    return eps_material, filling, eps_reference, c_geometric


def calculate_dielectric_constant(c_bare, c_material, eps_substrate=4.8):
    c_geometric = c_bare / eps_substrate
    eps_material = (c_material - c_bare) / c_geometric + 1.
    return eps_material


def calculate_Eb_and_tau0_from_fit(m, b, delm, delb):
    """assuming
    y = 1/Temperature
    x = ln(meausrement frequency)
    m = -(boltzmann constant)*(1K)/(activation energy)
    b = -ln(2pi*(activation time))*(boltzmann constant)*(1K)/(actiavtion energy)
    """
    kBT0 = 0.0019872  # in kcal/mol
    Eb = abs(kBT0 / m)
    tau0 = np.exp(-abs(b / m)) / (2 * np.pi) * 10 ** 15
    delEb = abs(kBT0 * delm / m ** 2)
    deltau0 = np.sqrt((tau0 / m * delb) ** 2 + (tau0 * b / m ** 2 * delm) ** 2)

    print('activation energy is (%.6g +/- %.2g) kcal/mol' % (Eb, delEb))
    print('activation time is (%.6g +/- %.2g) fs' % (tau0, deltau0))


def evaluate_sigfigs(delEb):
    if str(delEb)[0] == '0':
        print('got it')
        for ii, char in enumerate(str(delEb)[1:]):
            print(char)
            if char != '0' and char != '1' and char != '.':
                delEbdigit = float(char)
                delEorder = -ii
                break
            elif char == '1':
                try:
                    delEbdigit = 1. + 0.1 * float(str(delEb)[ii + 2])
                except IndexError:
                    delEbdigit = 1.
                delEorder = -ii
                break
    else:
        if str(delEb)[0] == '1':
            try:
                delEbdigit = 1. + 0.1 * float(str(delEb)[2])
            except ValueError:
                delEbdigit = 1.
        else:
            delEbdigit = float(str(delEb)[0])
        delEorder = 0
        e = False
        for ii, char in enumerate(str(delEb)):
            if char.lower() == 'e':
                e = True
                delEorder = int(str(delEb)[ii + 1:])
        if not e:
            delEorder = np.log10(delEb / delEbdigit)
    if str(delEbdigit)[1] == '.':
        sigfigs_pastdec = -delEorder + (str(delEbdigit)[2] != '0')
    else:
        raise ValueError('delEbdigit is not a digit: %s' % str(delEbdigit))
    delEbtemp = delEbdigit * 10 ** delEorder
    print(delEb)
    print(delEbtemp)
    print(sigfigs_pastdec)
