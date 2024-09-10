"""
GPIB using a prologix controller

@author: Teddy Tortorici
"""

import os
import serial


class Device:

    comment = "#"

    def __init__(self, address: int, serial_port, termination: str = "\r\n",
                 baudrate: int = 921600, timeout=0.25, silent: bool = True):

        self.silent = silent
        self.address = address
        self.eos = termination

        if not timeout:
            timeout = 2

        self.dev = serial.Serial(serial_port, baudrate=baudrate, timeout=timeout)
        # self.dev.write(b"++eoi 1")
        # self.dev.write(b"++eos 2")
        self.write_raw("++mode 1")
        self.write_raw("++auto 1")
        self.write_raw(f"++addr {self.address}")
        self.write_raw("++addr {}".format(self.address))
        print(self.write_raw("++ver"))

        # version = self.query("++ver")
        # print(f"Established connection with Prologix with version: {version}")

    def write_raw(self, message: str):
        self.dev.write(f"{message}{self.eos}".encode())

    def query(self, message: str) -> str:
        self.write_raw(f"++addr {self.address}")
        if self.do_print:
            print(f"Querying with {message}")
        self.write_raw(message)

        while True:
            print("trying")
            message_back = self.dev.readlines()
            if message_back:
                if self.do_print:
                    print("Got response")
                break
        return message_back[0].decode().rstrip("\r\n")

    def read(self) -> str:
        self.write_raw(f"++addr {self.address}")
        self.write_raw("++read")
        while True:
            message_back = self.dev.readlines()
            if message_back:
                if self.do_print:
                    print("Got response")
                break
        return message_back.rstrip("\n\r")

    def write(self, message):
        self.write_raw(f"++addr {self.address}")
        self.write_raw(message)

    def get_id(self):
        return self.query("*IDN?")


if __name__ == "__main__":
    ls = Device(13, "COM4", do_print=True)
    # print(ls.query("KRDG? A"))

