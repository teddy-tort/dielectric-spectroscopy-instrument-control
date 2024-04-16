"""
Classes for creating and managing data files for dielectric experiments

@author: Teddy Tortorici
"""

import time
import datetime
from communication.devices.ah2700 import Client as BridgeAH
from communication.devices.hp4275 import Client as BridgeHP
from communication.devices.lakeshore import Client as Lakeshore
from files.csv import CSVFile
from calculations.calibration import Calibration
from calculations.capacitors import geometric_capacitance


class DielectricSpec(CSVFile):

    labels = ('Time [s]', 'Temperature A [K]', 'Temperature B [K]',
              'Capacitance [pF]', 'Loss Tangent', 'Voltage [V]', 'Frequency [Hz]')

    def __init__(self, path: str, filename: str, frequencies: list,
                 bridge: str = 'AH', ls_model: int = 331, comment: str = "", lj_chs: list = None):
        """
        Create data file, and instances of the Bridge and Lakeshore for communication.
        :param path: path you want to save the file.
        :param filename: name of the file.
        :param frequencies: list of ints. frequencies to measure at. Will remove duplicates and reverse sort them
                            so measurements are made from the highest frequency to the lowest frequency.
        :param bridge: "AH" or "HP" to select which bridge to use.
        :param ls_model: integer value of the lakeshore model number.
        :param comment: Will write the comment after opening the file with the # header so that is ignored.
        :param lj_chs: Not currently supported.
        """
        super(self.__class__, self).__init__(path, filename, comment)
        unique_frequencies = list(set(frequencies))         # remove repeated entries
        unique_frequencies.sort()                           # sort the list
        self.unique_frequencies = unique_frequencies

        self.bridge_type = bridge.upper()
        if self.bridge_type[0:2] == 'AH' or self.bridge_type == 'FAKE':
            self.bridge = BridgeAH()
        elif self.bridge_type[0:2] == 'HP':
            self.bridge = BridgeHP()
        self.ls_model = ls_model
        self.ls = Lakeshore(model_num=ls_model)

        self.lj_chs = lj_chs
        # if len(lj_chs) > 0:
        #     self.lj = LabJack.LabJack()
        #     print('imported LabJack')
        # else:
        #     self.lj = None
        #     print('did not import LabJack')

        self.labels = [""] * len(self.__class__.labels) * len(self.unique_frequencies)
        if self.new:
            self.write_labels()
        self.start_time = time.time()

    def initiate_devices(self, voltage_rms: float = None, averaging_setting: int = None, dc_setting: str = None):
        """
        Initiate the bridge by setting its formatting, units, and the following options
        :param voltage_rms: This is the maximum AC voltage in volts RMS that the bridge will apply to the DUT. Any
                            voltage may be entered, but the bridge will limit the maximum measurement voltage to a value
                            equal to or below the amount specified.
                            0-15.
        :param averaging_setting: Set the approximate time used to make a measurement. Set a number between 0 and 15.
                                  See table A-1 in the Firmware manual on A-10 (pg 246 of the pdf)
                                  0-15.
        :param dc_setting: Enables or disables a user-supplied DC bias voltage of up to ±100 VDC to be applied to the
                           measured unknown. The external source is connected to the rear panel DC BIAS input. This
                           command also selects the value of an internal resistor that is placed in series with the
                           externally applied voltage source.
                           [OFF, LOW, HIGH]
        """
        if self.bridge_type == "AH":
            # self.bridge.format(notation="ENG")
            # self.bridge.set_units("DS")
            if voltage_rms is not None:
                self.bridge.set_voltage(voltage_rms)
            if averaging_setting is not None:
                self.bridge.set_ave(averaging_setting)
            if dc_setting is not None:
                self.bridge.dcbias(dc_setting)
        elif self.bridge_type == "HP":
            self.bridge.set_dispA(self.bridge.dispA)
            self.bridge.set_dispB(self.bridge.dispB)
            self.bridge.write('C1')  # set to auto circuit mode (C1: auto, C2: series, C3: parallel)
            self.bridge.write('H1')  # turn on high res mode (H0: off, H1: on)
            self.bridge.set_ave(averaging_setting)

    def write_labels(self):
        """
        Uses DataFile.labels to construct labels for each individual measurement frequency and then writes them to the
        data file
        """
        for ff, frequency in enumerate(self.unique_frequencies):
            if frequency < 1e3:
                f_label = f"{int(frequency):d} Hz"
            elif frequency < 1e6:
                f_label = f"{int(frequency / 1e3):d} kHz"
            elif frequency < 1e9:
                f_label = f"{int(frequency / 1e6):d} MHz"
            elif frequency < 1e12:
                f_label = f"{int(frequency / 1e9):d} GHz"
            elif frequency < 1e15:
                f_label = f"{int(frequency / 1e12):d} THz"
            else:
                f_label = f"{int(frequency / 1e15):d} PHz"
            for ll, label in enumerate(self.__class__.labels):
                self.labels[ll + ff * len(self.__class__.labels)] = f"{label:s} ({f_label:s})"
            # if type(self.lj_chs) == list:
            #     for ii, ch in enumerate(self.lj_chs):
            #         self.labels.extend(['LJ {} [V] ({})'.format(ch, f), 'LJ StdDev {} [V] ({})'.format(ch, f)])
        self.write_row(self.labels)

    def measure_at_frequency_old(self, frequency: int, attempts: int = 3, silent: bool = True):  # , amp=1, offset=0):
        """
        Just measure at one frequency
        :param frequency: The frequency to measure at in Hz
        :param attempts: how many times to attempt to get data after failed attempts
        :param silent: if silent, then it doesn't print anything
        """
        if not silent:
            print('Starting measurement')

        # data = [0] * len(self.__class__.labels)

        """Set the frequency"""
        self.bridge.set_frequency(frequency)

        if not silent:
            print(f'Frequency set to {frequency} Hz')

        if self.bridge.dev_id == 'HP':
            time.sleep(1)

        """Make attempts to read from the bridge"""
        f, c, l, v = self.bridge.read_front_panel()
        # for _ in range(attempts):
        #     bridge_data = self.bridge.read_front_panel()
        #     if bridge_data[-1] != -1:
        #         break

        if not silent:
            print('read front panel')

        """Read temperatures from lakeshore"""
        t_a, t_b = self.ls.read_front_panel()

        if not silent:
            print('read temperatures')

        # data[0] = time.time()
        # data[1:3] = temperatures
        # data[3:6] = bridge_data[1:]     # capacitance, loss, voltage
        # data[6] = bridge_data[0]        # frequency

        return [time.time(), t_a, t_b, c, l, v, f]

    def measure_at_frequency(self, frequency: int, attempts: int = 3):
        """
        Just measure at one frequency
        :param frequency: The frequency to measure at in Hz
        :param attempts: how many times to attempt to get data after failed attempts
        :param silent: if silent, then it doesn't print anything
        """
        """Set the frequency"""
        self.bridge.set_frequency(frequency)

        """Read temperatures from lakeshore"""
        t_a = self.ls.query("KRDG? A")[1:]
        t_b = self.ls.query("KRDG? B")[1:]

        """Initiate bridge measurement"""
        self.bridge.write("Q")

        """Make attempts to read from the bridge"""
        raw_msg = self.bridge.read()
        f = raw_msg[0:8].strip()
        c = raw_msg[13:25].strip()
        l = raw_msg[30:42].strip()
        v = raw_msg[43:52].strip()

        return [time.time(), t_a, t_b, c, l, v, f]

    def sweep_frequencies(self):  # , amp=1, offset=0):
        """
        Repeat measurements at each frequency in self.unique_frequencies
        """
        len_labels = len(self.__class__.labels)
        full_data = [0] * len_labels * len(self.unique_frequencies)     # initiate list of data
        try:
            for ff, frequency in enumerate(self.unique_frequencies):
                start_index = ff * len_labels       # figure out where to start indexing data in the list
                end_index = (ff + 1) * len_labels
                partial_data = self.measure_at_frequency(frequency)     # get a report back from the bridge

                """Print partial data to terminal"""
                now = str(datetime.datetime.fromtimestamp(partial_data[0]))
                now = now.split(' ')[1].split('.')[0]
                partial_data[0] = str(partial_data[0])
                print_list = [now,
                              f"{partial_data[1]:s} K".rjust(10),
                              f"{partial_data[2]:s} K".rjust(12),
                              f"{partial_data[3]:s} pF".rjust(15),
                              f"{partial_data[4]:s}".rjust(13),
                              f"{partial_data[5]:s} V".rjust(10),
                              f"{partial_data[6]:s} Hz".rjust(12)]
                print(", ".join(print_list))

                """place partial data in the full data list"""
                full_data[start_index:end_index] = partial_data
            [float(number) for number in full_data]
        except ValueError:
            print("error")
            self.bridge.reformat()
            for ii in range(len(self.unique_frequencies)):
                full_data[ii+3:ii+7] = ["-1", "-1", "-1", "-1"]
            # full_data = [-1] * len_labels * len(self.unique_frequencies)
            # print(full_data)
        self.write_row(full_data)
        return full_data


class DielectricConstant(DielectricSpec):

    labels = ('Time [s]', 'Temperature A [K]', 'Temperature B [K]',
              'Capacitance [pF]', 'Loss Tangent', 'Voltage [V]',
              'Re[dielectric constant]', 'Im[dielectric constant]', 'Frequency [Hz]')

    def __init__(self, path: str, filename: str, frequencies: list, film_thickness: float,
                 capacitor_calibration: Calibration,
                 bridge: str = 'AH', ls_model: int = 331, comment: str = "", lj_chs: list = None):
        """
        Data file for measuring a well characterized sample after calibrating the bare capacitor.
        :param path: file path where you want to write the file.
        :param filename: name of the file.
        :param frequencies: list of int. frequencies to measure at.
        :param film_thickness: measured film thickness in [um].
        :param capacitor_calibration: calibration for the capacitor being use.
        :param bridge: 'AH' or 'HP': Two character string signifying which bridge to use.
        :param ls_model: integer value of the lakeshore model number.
        :param comment: optional comment to append to datafile when started.
        :param lj_chs: not supported currently.
        """
        super(self.__class__, self).__init__(path, filename, frequencies,
                                             bridge, ls_model, comment, lj_chs)
        self.calibration = capacitor_calibration
        gap_width = self.calibration.gap_estimate()
        self.geometric_cap = geometric_capacitance(gap_width, film_thickness)

    def measure_at_frequency(self, frequency: int, attempts: int = 3, silent: bool = True):  # , amp=1, offset=0):
        """
        Just measure at one frequency
        :param frequency: The frequency to measure at in Hz
        :param attempts: how many times to attempt to get data after failed attempts
        :param silent: if silent, then it doesn't print anything
        """
        if not silent:
            print('Starting measurement')

        # data = [0] * len(self.__class__.labels)

        """Set the frequency"""
        self.bridge.set_frequency(frequency)
        frequency = self.bridge.frequency

        if not silent:
            print(f'Frequency set to {frequency} Hz')

        if self.bridge.dev_id == 'HP':
            time.sleep(1)

        """Make attempts to read from the bridge"""
        if attempts < 1:
            attempts = 1
        for _ in range(attempts):
            bridge_data = self.bridge.read_front_panel()
            if bridge_data[-1] != -1:
                break
        data_frequency = bridge_data[0]
        data_capacitance = bridge_data[1]
        data_loss = bridge_data[2]
        data_volt = bridge_data[3]

        if not silent:
            print('read front panel')

        """Read temperatures from lakeshore"""
        temperature_a, temperature_b = self.ls.read_front_panel()

        if not silent:
            print('read temperatures')

        bare_capacitance = self.calibration.bare_capacitance(temperature=temperature_a, frequency=frequency)
        bare_loss = self.calibration.bare_loss(temperature=temperature_a, frequency=frequency)

        re_eps = 1 + (data_capacitance - bare_capacitance) / self.geometric_cap
        im_eps = (data_loss * data_capacitance - bare_loss * bare_capacitance) / self.geometric_cap

        return [time.time(), temperature_a, temperature_b, data_capacitance,
                data_loss, data_volt, re_eps, im_eps, data_frequency]
