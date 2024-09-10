"""
Class for creating and managing csv files

@author: Teddy Tortorici
"""

import os
import numpy as np
import time


class CSVFile:

    file_type = ".csv"

    def __init__(self, path: str, filename: str, comment: str = ""):
        """
        Create or open a csv file and manage it.
        :param path: file path to where you want to save the file
        :param filename: name of the file you wish to create or open
        :param comment: an optional comment to put in the file
        """

        """MAKE SURE THE FILE NAME IS VALID"""
        filename = filename.rstrip(CSVFile.file_type)
        filename = filename.replace(".", "")
        filename += CSVFile.file_type
        self.name = os.path.join(path, filename)

        """CHECK IF PATH TO FILE AND FILE EXIST"""
        # Check if path exists, if it doesn't, make all the directories necessary to make it
        if not os.path.isdir(path):
            os.makedirs(path)

        # Check if file exists, if it doesn't, make it
        if os.path.exists(self.name):
            self.new = False
        else:
            self.new = True
            self.create_file()

        """APPEND OPTIONAL COMMENT"""
        if comment:
            self.write_comment(comment)

    def __str__(self):
        return f"Opened file: {self.name}"

    def __len__(self):
        with open(self.name, 'r') as f:
            for counter, _ in enumerate(f):
                pass
        return counter + 1

    def write_row(self, row_to_write: list):
        """Turns a list into a comma delimited row to write to the csv file"""
        written = False
        while not written:
            try:
                with open(self.name, 'a') as f:
                    f.write(", ".join(row_to_write) + '\n')
                written = True
            except OSError:
                print(f"OSError: [Errno 22] Invalid argument: {self.name}")

    def write_comment(self, comment: str):
        """Writes a comment line in the csv file"""
        with open(self.name, "a") as f:
            f.write(f"# {comment}\n")

    def create_file(self):
        """Creates file by writing the first comment line"""
        with open(self.name, "w") as f:
            f.write(f"# This data file was created on {time.ctime(time.time())}\n")

    @staticmethod
    def load_data_np(filename: str, line_skip: int = 0, attempts: int = 10) -> tuple[np.ndarray, int]:
        """
        Load data from a csv file into a numpy array
        :param filename: path+name of file
        :param line_skip: will skip this many lines on first attempt. If it fails to load, it will repeat skipping one
                          more line until it succeeds.
        :param attempts: maximum times it will try to load
        :return: numpy array of data, int of how many lines were skipped
        """
        data = None
        lines_skipped = None
        for skip_amount in range(line_skip, attempts):
            try:
                data = np.loadtxt(filename, comments="#", delimiter=",", skiprows=skip_amount)
                lines_skipped = skip_amount
                break
            except ValueError:
                pass
        return data, lines_skipped

    @staticmethod
    def get_labels(filename: str, attempts: int = 10) -> list[str]:
        """
        Returns the column labels from the file
        :param filename: path + name for file
        :param attempts: how many rows to attempt to read from
        :return: list of labels
        """
        labels = None
        with open(filename, "r") as f:
            for attempt in range(attempts):
                row = f.readline()
                if row[0] != "#":
                    labels = [label.strip() for label in row.strip("\n").split(",")]
                    break
        return labels
