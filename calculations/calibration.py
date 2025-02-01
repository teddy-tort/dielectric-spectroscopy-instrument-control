import numpy as np
from files.csv import CSVFile
from calculations.capacitors import find_gap

# unicodes = ["\u2070", "\u00B9", "\u00B2", "\u00B3", "\u2074", "\u2075", "\u2076", "\u2077", "\u2078", "\u2079"]
superscripts = ["", " T", " T\u00B2", " T\u00B3", " T\u2074", " T\u2075",
                " T\u2076", " T\u2077", " T\u2078", " T\u2079"]


class Calibration:
    def __init__(self, filename: str, capacitance_fit_order: int = 2, loss_fit_order: int = 1):
        cal_data, _ = CSVFile.load_data_np(filename)
        labels = CSVFile.get_labels(filename)

        temperature_indices = []    # indices for temperatures
        capacitance_indices = []    # indices for capacitance
        loss_indices = []           # indices for loss tangent
        frequency_indices = []      # indices for frequency

        """FIND INDICES FOR DIFFERENT COLUMNS"""
        for ii, label in enumerate(labels):
            if 'temperature' in label.lower() and 'B' not in label:
                temperature_indices.append(ii)
            elif 'capacitance' in label.lower():
                capacitance_indices.append(ii)
            elif 'loss tangent' in label.lower():
                loss_indices.append(ii)
            elif 'frequency' in label.lower():
                frequency_indices.append(ii)

        self.capacitance_fit_parameters = {}
        self.loss_fit_parameters = {}

        # Get the frequencies then use those as keys for the fits
        self.frequencies = np.zeros(len(frequency_indices), dtype=int)
        for ii, f_index in enumerate(frequency_indices):
            frequency = int(cal_data[:, f_index][0])
            self.frequencies[ii] = frequency
            self.capacitance_fit_parameters[frequency] = np.polyfit(cal_data[:, temperature_indices[ii]],
                                                                    cal_data[:, capacitance_indices[ii]],
                                                                    capacitance_fit_order)[::-1]
            self.loss_fit_parameters[frequency] = np.polyfit(cal_data[:, temperature_indices[ii]],
                                                             cal_data[:, loss_indices[ii]],
                                                             loss_fit_order)[::-1]

    def bare_capacitance(self, temperature: float, frequency: int) -> float:
        """
        Get the capacitance at a given temperature and frequency
        :param temperature: temperature you wish to know the capacitance
        :param frequency: will take the nearest valid frequency from the one given
        :return: capacitance in pF
        """
        frequency = self.frequencies[np.argmin(abs(self.frequencies - frequency))]
        return self.bare_fit(temperature, self.capacitance_fit_parameters[frequency])

    def bare_loss(self, temperature: float, frequency: int):
        """
        Get the loss at a given temperature and frequency
        :param temperature: temperature you wish to know the loss
        :param frequency: will take the nearest valid frequency from the on given
        :return: loss tangent as tan(delta)
        """
        frequency = self.frequencies[np.argmin(abs(self.frequencies - frequency))]
        return self.bare_fit(temperature, self.loss_fit_parameters[frequency])

    @staticmethod
    def bare_fit(temperature: float, fit_params: np.ndarray) -> float:
        """
        Get the capacitance at a given temperature and frequency
        :param temperature: temperature you wish to know the capacitance
        :param fit_params: [a0, a1, a2, ...]
        :return: capacitance in pF
        """
        output = 0.
        for ii, a in enumerate(fit_params):
            output += a * temperature ** ii
        return output

    def capacitance_room_temperature(self) -> float:
        """
        Get the room temperature capacitance nearest 2 kHz
        :return: capacitance at room temperature in pF
        """
        temperature = 297.
        return self.bare_capacitance(temperature, 2000)

    def gap_estimate(self) -> float:
        """
        Use calculations.capacitors.find_gap() to estimate the gap size in um
        :return: gap width in um
        """
        return find_gap(self.capacitance_room_temperature())

    def __str__(self) -> str:
        """
        What gets printed when you print the object
        :return: prints this
        """
        string_to_print = ""
        for frequency in self.frequencies:
            if frequency < 1e3:
                string_to_print += f"{frequency:4} Hz"
            elif frequency < 1e6:
                string_to_print += f"{int(frequency/1e3):3} kHz"
            elif frequency < 1e9:
                string_to_print += f"{int(frequency/1e6):3} MHz"
            else:
                string_to_print += f"{int(frequency/1e9):3} GHz"
            string_to_print += " :: C = "
            cap_params = self.capacitance_fit_parameters[frequency]
            function = [f"{a:.3e}{x}" for a, x in zip(cap_params, superscripts[:len(cap_params)])]
            string_to_print += " + ".join(function)
            string_to_print += f"\n{'':7} :: L = "
            loss_params = self.loss_fit_parameters[frequency]
            function = [f"{a:.3e}{x}" for a, x in zip(loss_params, superscripts[:len(loss_params)])]
            string_to_print += " + ".join(function)
            string_to_print += "\n"
        return string_to_print


if __name__ == "__main__":
    import time

    def test(target, args=()):
        start = time.perf_counter()
        response = target(*args)
        print(time.perf_counter() - start)
        return response

    filename = "D:\\Google Drive\\My Drive\\Dielectric_data\\Teddy-2\\1-Calibrations\\2021\\" \
               "calibrate_TT10-05-08_ah_40K_05-21_16-33.csv"
    cal = Calibration(filename)
    for ii in range(10):
        print(test(cal.bare_capacitance, args=(200+ii, 400)))
