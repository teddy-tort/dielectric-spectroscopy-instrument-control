"""
classes for communicating with AH2700A Capacitance Bridge

@author: Teddy Tortorici
"""

import time
import numpy as np
from communication.socket_client import Device


class Client(Device):

    default_units = "DS"
    valid_frequencies = np.array([50, 60, 70, 80, 100, 120, 140, 160, 200, 240, 300, 400, 500, 600, 700, 800,
                                  1000, 1200, 1400, 1600, 2000, 2400, 3000, 4000, 5000, 6000, 7000, 8000,
                                  10000, 12000, 14000, 16000, 20000], dtype=int)

    def __init__(self, silent: bool = True):
        """
        Only meant to be inherited to obtain all the methods
        :param averaging_setting:
        :param silent:
        """
        super(self.__class__, self).__init__("AH")

        self.silent = silent
        self.unit = self.read_loss_units()
        self.ave_setting = self.read_ave()
        self.frequency = self.read_frequency()
        # self.set_units(Client.default_units)
        # self.set_ave(averaging_setting)

    def clear(self):
        """
        Clears a partially entered command or parameter when used from the front panel.
        Aborts entry of a command from the serial device.
        """
        self.write('^U')
        if not self.silent:
            print('AH2700A cleared')

    def dcbias(self, setting):
        """
        Enables or disables a user-supplied DC bias voltage of up to ±100 VDC to be applied to the measured unknown. The
        external source is connected to the rear panel DC BIAS input. This command also selects the value of an internal
        resistor that is placed in series with the externally applied voltage source.
        :param setting: [OFF, LOW, HIGH]
        """
        if setting == 'OFF':
            msgout = "BIAS OFF"
            printmsg = "DC Bias off"
        elif setting == 'HIGH':
            msgout = "BIAS IHIGH"
            printmsg = "DC Bias set to high"
        elif setting == 'LOW':
            msgout = 'BIAS ILOW'
            printmsg = "DC Bias set to low"
        else:
            msgout = ""
            printmsg = "Invalid DC bias setting, should be in OFF, LOW, or HIGH"
        self.write(msgout)
        if not self.silent:
            print(printmsg)

    def reformat(self):
        self.raw("F")
        print("\n\nREFORMATTING\n\n")

    def format(self, notation: str = 'FLOAT', labeling: str = 'ON', ieee: str = 'OF', fwidth: str = 'FIX'):
        """Controls the format and numeric notation of results which are sent to serial or
        GPIB ports. Front panel results are not affected
        :param notation: specifies the type of numeric notation to be used for capacitance, loss, frequency, voltage and
                         cable results. The notation parameter can be set to FLOATing, SCI, or ENG.
        :param labeling: enables labels to be sent when set to ON and conversely disables labels when set to OFF.
        :param ieee: enables IEEE-488.2 compatible punctuation when set to ON and conversely disables labels when set to
                     OFf.
        :param fwidth: fixes field widths when set to FIXed. Or it varies with VARiable.
        """
        # capitalize entries
        notation = notation.upper()
        labeling = labeling.upper()
        ieee = ieee.upper()
        fwidth = fwidth.upper()
        # notation FLOAT for floating, SCI for scientific, ENG, for engineering
        self.write('FO NOTAT {}'.format(notation))
        time.sleep(0.01)
        # enables lables to be sent when set to ON
        self.write('FO LA {}'.format(labeling))
        time.sleep(0.01)
        # enables IEEE-488.2 compatible punctuation when set to ON
        self.write('FO IEE {}'.format(ieee))
        time.sleep(0.01)
        # fixes field widths when set to FIXED. Permitted values are FIXed and VARiable
        self.write('FO FW {}'.format(fwidth))
        print('AH2700A formatted')

    def local(self):
        """
        Activate Front Panel
        """
        self.write('LOC')

    def lockout(self, on: bool = True):
        """
        When on, locks out front panel entirely; resulting in pressing local on the panel not working
        :param on: Will lockout if True, and turn off if False.
        """
        if on:
            self.write('NL ON')
        else:
            self.write('NL OF')

    def meas_cont(self, on: bool = True):
        """
        Initiates measurements which are taken continuously, one after another
        :param on: Will measure continuous if True, and turn off if False.
        """
        if on:
            self.write('CO ON')
        else:
            self.write('CO OF')

    def read_ave(self) -> int:
        """
        Fetch averaging setting
        :return: the value of the averaging setting.
        """
        # msgout = self.query('SH AV').split('=')
        return int(self.query('SH AV'))

    def read_front_panel(self) -> tuple[str, str, str, str]:
        """
        Causes the bridge to execute a single measurement. If continuous readings were being taken then the Q command
        aborts them after taking another measurement. The result from the instrument looks like
        'F=  1200.0 Hz C= 843.31094 PF L= 0.00314 DS'
        :return: [frequency, capacitance, loss, voltage]
        """
        # data = [-1, -1, -1, -1]
        raw_msg = self.query('Q')
        # data = [raw_msg[:8].strip(), raw_msg[13:24].strip(), raw_msg[29:41].strip(), raw_msg[42:52].strip()
        # number_of_results = raw_msg.count("=")
        # msg = raw_msg.replace(" ", "")              # remove the spaces
        # if number_of_results < 2:
        #     data = [-1, -1, -1, -1]
        # else:
        #     data = [0] * number_of_results
        #     for ii, msg_part in enumerate(msg.split("=")[1:]):
        #         data[ii] = float("".join([digit for digit in msg_part if (not digit.isalpha() or digit == "E")]))
        # msg_list = raw_msg.replace('",', '').replace('"', '').split(',')
        # for ii in range(4):
        #     data[ii] = float(msg_list[ii])
        return raw_msg[0:8].strip(), raw_msg[13:25].strip(), raw_msg[30:42].strip(), raw_msg[43:52].strip()

    def read_front_panel_full(self) -> tuple[str, str, str, str, str]:
        """
        Will also return error
        :return: frequency, capacitance, loss tangent, voltage rms, error
        """
        raw_msg = self.query("Q")
        frequency = raw_msg[0:8].strip()
        capacitance = raw_msg[13:25].strip()
        loss_tangent = raw_msg[30:42].strip()
        voltage_rms = raw_msg[43:52].strip()
        try:
            error = raw_msg[53:].strip()
        except IndexError:
            error = "None"
        return frequency, capacitance, loss_tangent, voltage_rms, error



    def read_front_panel_after_write(self) -> tuple[str, str, str, str]:
        """
        Causes the bridge to execute a single measurement. If continuous readings were being taken then the Q command
        aborts them after taking another measurement. The result from the instrument looks like
        'F=  1200.0 Hz C= 843.31094 PF L= 0.00314 DS'
        :return: [frequency, capacitance, loss, voltage]
        """
        raw_msg = self.read()
        return raw_msg[0:8].strip(), raw_msg[13:25].strip(), raw_msg[30:42].strip(), raw_msg[43:52].strip()

    def read_frequency(self) -> float:
        """
        Fetch the value the measurement frequency is set to in Hertz.
        The return message looks something like:
        'FREQUENCY        1200.0 HZ'
        'FREQUENCY        1.000000E+03 HZ'
        "FREQUENCY        100.00 E+00 HZ'
        :return: measurement frequency setting in Hertz
        """
        # msg_back = self.query("SH FR")
        # msg_back = msg_back.lstrip("FREQUENCY").rstrip("HZ\n").replace(" ", "")
        # Should now be a string that can be converted to a float
        return float(self.query("SH FR"))

    def read_loss_units(self) -> str:
        """
        Fetch units for loss
        :return: Two character string representing loss unit setting
        """
        msgout = self.query('SH UN')
        # return msgout[-2:]
        return msgout

    def remote(self):
        """
        Places the bridge in the Serial Remote State. This state disables all front panel keys except the LOCAL key.
        """
        self.write('NREM')

    def set_ave(self, averaging: int, up: bool = False, down: bool = False):
        """
        Description: Set the approximate time used to make a measurement. Set a number between 0 and 15.
        See table A-1 in the Firmware manual on A-10 (pg 246 of the pdf)
        :param averaging: average time exponent parameter value is an integer from 0 to 15.
        :param up: Can set to True to change the averaging setting up to the next available voltage
        :param down: Can set to True to change the averaging setting down to the next available setting
        """
        if not up and not down:
            averaging = abs(int(averaging))
            if averaging > 15:
                averaging = 15
            self.write(f'AV {averaging}')
            to_print = f"Set averaging setting to {averaging}"
            self.ave_setting = averaging
        elif up and self.ave < 15:
            self.write('AV UP')
            self.ave_setting += 1
            to_print = "Pushed averaging setting setting up one notch"
        elif down and self.ave > 0:
            self.write('AV DO')
            self.ave_setting -= 1
            to_print = "Pushed averaging setting setting down one notch"
        else:
            to_print = "Did not change setting"
        if not self.silent:
            print(to_print)

    def set_frequency(self, in_hertz: float, up: bool = False, down: bool = False):
        """
        Description: Sets the test frequency at which measurements are to be taken.
        :param in_hertz: This parameter specifies the desired test frequency. The bridge will select the nearest
                         available frequency at which measurements can be taken (see Commands.valid_frequencies
        :param up: Can set to True to change the in_hertz setting up to the next available frequency
        :param down: Can set to True to change the in_hertz setting down to the next available frequency
        """
        success = True
        if not up and not down:
            differences_from_valid = abs(Client.valid_frequencies - in_hertz)
            frequency = Client.valid_frequencies[differences_from_valid.argmin()]
            self.write(f'FR {frequency}')
            to_print = f"Set measurement frequency to {frequency}"
            self.frequency = frequency
        else:
            current_index = np.where(Client.valid_frequencies == self.frequency)[0]
            if up:
                if current_index < len(Client.valid_frequencies) - 1:
                    self.write("FR UP")
                    self.frequency = Client.valid_frequencies[current_index + 1]
                    to_print = "Pushed measurement frequency setting up one notch"
                else:
                    success = False
            elif down:
                if current_index > 0:
                    self.write("FR DO")
                    self.frequency = Client.valid_frequencies[current_index - 1]
                    to_print = "Pushed measurement frequency setting down one notch"
                else:
                    success = False
        if not success:
            to_print = "Did not change frequency"
        if not self.silent:
            print(to_print)
        if success:
            wait_time = 2
            self.sleep(wait_time, f"Waiting {wait_time} seconds to allow frequency measurement to be set")

    def set_units(self, unit: str = 'DS'):
        """
        Description: Selects the units that will be used to report the loss component of the measurements.
        :param unit: NS: nanosiemens, DS: loss tangent, KO: series resistances in kOhms,
                     GO: Parallel R in GOhms, JP: G/omega
        """
        unit_choices = ["NS", "DS", "KO", "GO", "JP"]
        if unit not in unit_choices:
            raise ValueError(f"Invalid unit choice. Options are {unit_choices}")
        self.write(f"UN {unit}")
        self.unit = unit
        if not self.silent:
            print(f"Set loss units to {unit}")

    def set_voltage(self, v_rms: float = 15., up: bool = False, down: bool = False):
        """
        Description: Limits the amplitude of the test voltage applied by the bridge to the device under test.
        :param v_rms: This is the maximum AC voltage in volts RMS that the bridge will apply to the DUT. Any voltage may
                      be entered up to 15 Vrms, but the bridge will limit the maximum measurement voltage to a value
                      equal to or below the amount specified.
        :param up: Can set to True to change the v_rms setting up to the next available voltage
        :param down: Can set to True to change the v_rms setting down to the next available voltage
        """
        if v_rms > 15:
            v_rms = 15.
        if not up and not down:
            self.write(f'V {v_rms:.2f}')
            to_print = f"Set maximum RMS voltage to {v_rms:.2f}"
        elif up:
            self.write('V UP')
            to_print = "Pushed Maximum voltage setting up one notch"
        else:
            self.write('V DO')
            to_print = "Pushed Maximum voltage setting down one notch"
        if not self.silent:
            print(to_print)

    def sleep(self, time_to_wait: int, start_tag: str = '', end_tag: str = ''):
        """
        A custom sleep command that writes dots to console, so that you know what's going on
        :param time_to_wait: How long to sleep
        :param start_tag: An optional tag to print before dots
        :param end_tag: An optional tag to print after dots
        """
        if self.silent:
            time.sleep(time_to_wait)
        else:
            if start_tag:
                print(start_tag, end="")
            for second in range(int(time_to_wait)):
                print(".", end="")
                time.sleep(1)
            time.sleep(time_to_wait - int(time_to_wait))
            if end_tag:
                print(end_tag)

    def trigger(self):
        """Produces exactly the same result as the GPIB GET command. Provides a convenient way of initiating any
        operation with the bridge."""
        self.write('*TR')
        print('Triggered')
