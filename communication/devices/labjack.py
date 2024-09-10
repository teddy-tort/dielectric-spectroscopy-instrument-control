import u6
# import LabJackPython
import time
import numpy as np
import struct
from communication.socket_client import Device as DeviceClient
# import sys
# import threading


"""Driver for using labjack for this experiment specifically"""


# Refer to Section 6 of AH 2700 Firmware 02 Manual.pdf in Manuals and pg 285 on

class LabJack:
    DAC_PIN_DEFAULT = 0
    DAC_ADDRESS = 0x12
    EEPROM_ADDRESS = 0x50

    def __init__(self):
        self.devicename = 'LJ'
        self.lj = u6.U6()
        self.dacPin = LabJack.DAC_PIN_DEFAULT
        self.sclPin = self.dacPin
        self.sdaPin = self.sclPin + 1
        self.getCalConstants()

    def get_pressure(self):
        """Returns the voltage reading from the pressure gauge (10mV=1Torr)... Use AIN0"""
        return self.lj.getAIN(0)

    def get_v(self, ch):
        return self.lj.getAIN(ch)

    def get_voltages(self, chs=4):
        voltages = [0] * chs
        for ii in range(chs):
            voltages[ii] = self.lj.getAIN(ii)
            time.sleep(0.01)
        return voltages

    def get_v_ave(self, ch, aves=50):
        measurements = np.zeros(aves)
        for ii in range(aves):
            measurements[ii] = self.get_v(ch)
            # time.sleep(0.000001)
        average = sum(measurements) / aves
        sigma = np.sqrt(sum((measurements - average) ** 2) / (aves - 1))
        return average, sigma

    def get_voltages_ave(self, chs=range(4), aves=50):
        data = [0] * len(chs)
        for ii, ch in enumerate(chs):
            volt, sigma = self.get_v_ave(ch)
            data[ii] = (volt, sigma)
        return data

    def set_dc_voltage(self, volt, amp=1.):
        """set the dc voltage to volt. If an amplifier is used, set the 'amp' to the amplification value,
        and the voltage you want in the end... Use DAC0"""
        voltage = volt / amp
        self.lj.getFeedback(u6.DAC0_8(self.lj.voltageToDACBits(voltage, dacNumber=0, is16Bits=False)))

    def get_dc_voltage(self, amp=1.):
        return self.lj.getAIN(1) * amp

    def set_dc_voltage2(self, volt, amp=1.):
        voltage = float(volt) / float(amp)
        self.lj.i2c(LabJack.DAC_ADDRESS, [48, int(((voltage * self.aSlope) + self.aOffset) / 256),
                                          int(((voltage * self.aSlope) + self.aOffset) % 256)],
                    SDAPinNum=self.sdaPin, SCLPinNum=self.sclPin)

    # def update_LJTickDAC(self, voltageB):
    #    """Changes DCCA and DACB to the amounts specified by the user"""
    #    # Determine pin numbers
    #    sclPin = self.dacPin
    #    sdaPin = sclPin + 1
    #
    #    # Get voltage for DACA
    #    try:
    #        voltageA = float(self.dacAEntry.get())
    #    except:
    #        print "Invalid entry", "Please enter a numerical value for DAC A"
    #        return
    #
    #    # Get voltage DACB
    #    try:
    #        voltageB = float(self.dacBEntry.get())
    #    except:
    #        print "Invalid entry", "Please enter a numerical value for DAC B"
    #        return
    #
    #    # Make requests
    #    try:
    #        self.lj.i2c(LabJack.DAC_ADDRESS, [48, int(((voltageA*self.aSlope)+self.aOffset)/256),
    #                                              int(((voltageA*self.aSlope)+self.aOffset) % 256)],
    #                        SDAPinNum=sdaPin, SCLPinNum=sclPin)
    #        self.lj.i2c(LabJack.DAC_ADDRESS, [49, int(((voltageB*self.bSlope)+self.bOffset)/256),
    #                                              int(((voltageB*self.bSlope)+self.bOffset) % 256)],
    #                        SDAPinNum=sdaPin, SCLPinNum=sclPin)
    #    except:
    #        print "I2C Error", "Whoops! Something went wrong when setting the LJTickDAC. " \
    #                           "Is the device detached?\n\nPython error:" + str(sys.exc_info()[1])
    #        #self.showSetup()

    def getCalConstants(self):
        """Loads or reloads the calibration constants for the LJTic-DAC. See datasheet"""
        # make a request
        data = self.lj.i2c(LabJack.EEPROM_ADDRESS, [64], NumI2CBytesToReceive=36, SDAPinNum=self.sdaPin,
                           SCLPinNum=self.sclPin)
        response = data['I2CBytes']

        self.aSlope = toDouble(response[0:8])
        self.aOffset = toDouble(response[8:16])
        self.bSlope = toDouble(response[16:24])
        self.bOffset = toDouble(response[24:32])

        if 255 in response:
            self.showErrorWindow("Pins",
                                 "The calibration constants seem a little off. Please go into settings and make sure the pin numbers are correct and that the LJTickDAC is properly attached.")


def toDouble(buffer):
    """
    Name: toDouble(buffer)
    Args: buffer, an array with 8 bytes
    Desc: Converts the 8 byte array into a floating point number.
    """
    right, left = struct.unpack("<Ii", struct.pack("B" * 8, *buffer[0:8]))
    return float(left) + float(right) / (2 ** 32)


class Client(DeviceClient):
    def __init__(self, port):
        super(self.__class__, self).__init__('LJ', port)

    def read_id(self):
        return 'LabJack U6'

    def reset(self):
        print('One cannot simply reset a LabJack with a command')


if __name__ == '__main__':
    lj = LabJack()
    lj.set_dc_voltage2(0)
    # x = np.arange(-5, 5, 1)
    # x = np.concatenate((x, x[::-1]))
    # for volt in x:
    #    lj.set_dc_voltage2(volt)
    #    print lj.get_dc_voltage()
    #    time.sleep(1)
