import pyvisa
import numpy as np


class Device:
    def __init__(self, port, addr):
        self.addr = addr
        self.rm = pyvisa.ResourceManager()
        self.dev = self.rm.open_resource(f"ASRL{port}::INSTR", read_termination="\r")

    def read(self) -> str:
        """Reads from the device connected to"""
        try:
            return self.dev.read()
        except pyvisa.errors.VisaIOError:
            return "timed out"

    def write(self, msg: str):
        """Write to the device connected to"""
        try:
            self.dev.write(msg)
            return "sent"
        except pyvisa.errors.VisaIOError:
            return "timed out"

    def query(self, msg: str) -> str:
        """Write to the device and then read its response"""
        try:
            return self.dev.query(msg)
        except pyvisa.errors.VisaIOError:
            return "timed out"


class Pressure(Device):
    def __init__(self):
        super(Pressure, self).__init__(3, 253)

    def start_logging(self):
        self.write(f"@{self.addr}DLC!START;FF")

    def download(self):
        return self.query(f"@{self.addr}DL?;FF")

    def get_pressure(self) -> float:
        self.start_logging()
        return float(self.download().split(";")[1])


class ThicknessMonitor(Device):
    def __init__(self):
        super(ThicknessMonitor, self).__init__(3, 2444)
        self.rm.baud_rate = 19200
        self.rm.read_termination = ""

    def write2(self, msg):
        full_message = "!{length}{msg}".format(length=self.length_char(msg), msg=msg)
        crc = self.calc_crc(full_message)
        self.write("{msg}({low})({high})".format(msg=full_message, low=self.crc_low(crc), high=self.crc_high(crc)))

    def query2(self, msg):
        full_message = "!{length}{msg}".format(length=self.length_char(msg), msg=msg)
        crc = self.calc_crc(full_message)
        full_message = "{msg}{low}{high}".format(msg=full_message, low=self.crc_low(crc), high=self.crc_high(crc))
        print(full_message)
        return self.query(full_message)

    @staticmethod
    def length_char(msg: str) -> str:
        return chr(len(msg) + 34)

    @staticmethod
    def calc_crc(char_array: str) -> int:
        # crc = 0
        length = 1 + ord(char_array[1]) - 34
        # length = ord(char_array[1]) - 34       # number of characters following the length char
        # if length >= 0:
        # set 14 bit CRC to all ones: 11111111111111
        crc = 16383
        for char in range(1, length + 1):
        # for char in range(1, len(char_array)):
            # XOR current character with CRC
            crc = crc ^ ord(char_array[char])
            # Go through lower 8 bits of CRC
            for _ in range(8):
                # Save CRC before bit shift
                tmp_crc = crc
                # Shift right one bit
                crc = crc >> 1
                if tmp_crc & 1 == 1:
                    # If LSB is 0 (before shift), XOR with 0x2001
                    crc = crc ^ 8193
            # Be sure we still have 14 bits
            crc = crc & 16383
        return crc

    @staticmethod
    def crc_high(crc: int) -> int:
        return chr(((crc >> 7) & 127) + 34)

    @staticmethod
    def crc_low(crc: int) -> int:
        return chr((crc & 127) + 34)


if __name__ == "__main__":
    import time
    # d = Pressure()
    # for ii in range(10):
    #     d.start_logging()
    #     print(d.download())
    #     print(d.get_pressure())
    t = ThicknessMonitor()
    print(t.query2("@"))
    print(t.write2("@"))
    print(t.dev.query("!#@O7"))
    # t.write2("L1?")
    # crc = t.calc_crc("!%L1?")
    # print(crc)
    # print(t.crc_low(crc))
    # print(t.crc_high(crc))

    # t.write2("@")
    # crc = t.calc_crc("!#@")
    # print(crc)
    # print(t.crc_low(crc))
    # print(t.crc_high(crc))
