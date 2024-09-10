# -*- coding: utf-8 -*-
"""
Created on Fri Sep 29 16:45:11 2017

@author: Teddy
"""
import numpy as np


default_m = -6.7e-4
default_b = 0.01766
default_delm = 2.8e-6
default_delb = 2e-5


def calc2(T, f=(100., 1000., 10000.)):
    T = np.array(T)
    f = np.array(f)    
    inverseT = 1/T
    lnf = np.log(f)
    m, b = np.polyfit(lnf, inverseT, 1)
    kBT0 = 0.0019872 # in kcal/mol    
    Eb = abs(kBT0/m)
    tau0 = np.exp(-abs(b/m))/(2*np.pi) * 10**15
    return Eb, tau0, m, b


def calculate(m, b, delm, delb):
    """assuming 
    y = 1/Temperature
    x = ln(meausrement frequency)
    m = -(boltzmann constant)*(1K)/(activation energy)
    b = -ln(2pi*(activation time))*(boltzmann constant)*(1K)/(actiavtion energy)
    """
    kBT0 = 0.0019872 # in kcal/mol    
    Eb = abs(kBT0/m)
    tau0 = np.exp(-abs(b/m))/(2*np.pi) * 10**15
    delEb = abs(kBT0*delm/m**2)
    deltau0 = np.sqrt((tau0/m*delb)**2+(tau0*b/m**2*delm)**2)
    
    return Eb, tau0, delEb, deltau0


def peak_Temps(c1, c2, delc1, delc2):
    T = -c1/(2*c2)
    delT = np.sqrt((delc1/(2*c2))**2 + (c1*delc2/(2*c2**2))**2)
    return T, delT

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        m = sys.argv[1]
        b = sys.argv[2]
        delm = sys.argv[3]
        delb = sys.argv[4]
    else:
        m = default_m
        b = default_b
        delm = default_delm
        delb = default_delb
    Eb, tau0, delEb, deltau0 = calculate(m, b, delm, delb)        
    print('activation energy is (%.6g +/- %.2g) kcal/mol' % (Eb, delEb))
    print('activation time is (%.6g +/- %.2g) fs' % (tau0, deltau0))