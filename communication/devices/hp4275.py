import sys
import time
import numpy as np
from communication.socket_client import Device


class Client(Device):

    valid_frequencies = {10e3: 'F11', 20e3: 'F12', 40e3: 'F13', 100e3: 'F14', 200e3: 'F15',
                         400e3: 'F16', 1e6: 'F17', 2e6: 'F18', 4e6: 'F19', 10e6: 'F20'}
    to_meas_A = {'L': 'A1', 'C': 'A2', 'R': 'A3', 'Z': 'A4'}
    to_meas_B = {'D': 'B1', 'Q': 'B2', 'ESRG': 'B3', 'XB': 'B4', 'LC': 'B5'}

    def __init__(self):
        super(self.__class__, self).__init__("HP")
        self.frequency = 0
        self.set_frequency(10e6)
        self.aves = 1
        self.measure_volt = 1
        self.dispA = "C"
        self.dispB = "D"

    def clear(self):
        """Clears a partially entered command or parameter when used from the front panel.
        Aborts entry of a command from the serial device."""
        self.write('DC1')
        print('Cleared HP bridge')

    def read_front_panel(self):
        """fetch frequency [Hz], capacitance [pF], loss [default is tan(delta)], and voltage [V]"""
        caps = np.zeros(self.aves)
        losses = np.zeros(self.aves)
        msg = self.read()
        while not msg.strip(' ')[2:4] == 'NC':
            print('waiting for measurement')
            time.sleep(1)
            msg = self.read()
        for ii in range(self.aves):
            msgBack = self.read().split(',')
            caps[ii] = float(msgBack[0][msgBack[0].index('C')+1:])
            losses[ii] = float(msgBack[1][msgBack[1].index('D')+1:])
        cap = sum(caps) / self.aves * 1e12          # put it in pF
        loss = sum(losses) / self.aves
        msgout = [self.frequency, cap, loss, self.measure_volt]
        return msgout

    def set_ave(self, msg):
        self.aves = int(msg)

    def set_dispA(self, to_meas='C'):
        if to_meas.upper() in self.to_meas_A.keys():
            self.write(self.to_meas_A[to_meas])
            self.dispA = to_meas
        else:
            print('invalid display A message (L, C, R, Z)')

    def set_dispB(self, to_meas='D'):
        if to_meas.upper() in self.to_meas_B.keys():
            self.write(self.to_meas_B[to_meas])
            self.dispB = to_meas
        else:
            print('invalid display B message (D, Q, ESRG, XB, LC)')

    def set_frequency(self, inHertz):
        """Sets the frequency on capacitor
        give inHertz None or False and give 'UP' or 'DO' to adjust frequency by one "notch"
        otherwise, just give a number for inHertz in.. Hertz"""
        valid_freqs = list(self.valid_frequencies.keys())
        try:
            freq = float(inHertz)
            """find differences between given inHertz and valid frequencies"""
            difs = [abs(valF - freq) for valF in valid_freqs]
            """find smallest difference to find 'nearest' valid frequency"""
            self.frequency = valid_freqs[difs.index(min(difs))]
        except ValueError:
            if inHertz[0].lower() == 'u':
                msg = 'UP'
                if self.frequency < 10e6:
                    self.frequency = valid_freqs[valid_freqs.index(self.frequency) + 1]
            elif inHertz[0].lower() == 'd':
                msg = 'DO'
                if self.frequency > 10e3:
                    self.frequency = valid_freqs[valid_freqs.index(self.frequency) - 1]
            else:
                raise ValueError('Please enter a number, or "up" or "down"')
        self.write(self.valid_frequencies[self.frequency])
        if self.frequency < 25e3:
            print('wait 60 s')
            time.sleep(60)
        else:
            time.sleep(2)

    def set_voltage(self, volt=1):
        """set the voltage of the sine wave the AH uses to make measurements"""
        self.measure_volt = volt

    def sleep(self, time_to_wait, tag1='', tag2=''):
        """A custom sleep command that writes dots to console so you know what's going on"""
        sys.stdout.write(tag1)
        sys.stdout.flush()
        for second in range(int(time_to_wait)):
            sys.stdout.write('..')
            sys.stdout.flush()
            time.sleep(1)
        time.sleep(time_to_wait - int(time_to_wait))
        sys.stdout.write(' {}\n'.format(tag2))
        sys.stdout.flush()

    def trigger(self):
        """Need to trigger to initiate"""
        self.write('*TR')
        print('HP bridge Triggered')
