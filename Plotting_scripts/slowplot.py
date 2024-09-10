import matplotlib.pylab as plt
from datetime import datetime
import os
import numpy as np
import re
import time


class SubPlot:
    def __init__(self, plot_num, x_data, y_data, label):
        self.plot_num = plot_num
        self.x = x_data
        self.y = y_data
        self.label = label

    def plot(self):
        plt.figure(self.plot_num)
        if self.label == None:
            plt.plot(self.x, self.y)
        else:
            plt.plot(self.x, self.y, label=self.label)

    def plot_date(self):
        #time_format = '%ddd %MMM %d %H:%M:%S %yyyy'
        ## '%Y-%m-%d %H:%M:%S.%f'
        #times_str = [time.ctime(t) % t for t in self.x]
        #times = [datetime.strptime(i, time_format) for i in times_str]
        #if self.label == None:
        #    plt.plot_date(times, self.y)
        #else:
        #    plt.plot_date(times, self.y, label=self.label)
        plt.figure(self.plot_num)
        if self.label == None:
            plt.plot((self.x - self.x[0]) / 60, self.y)
        else:
            plt.plot((self.x - self.x[0]) / 60, self.y, label=self.label)


class Plot:
    def __init__(self, plot_num, title='', axes_labels=['', ''], legend_loc=1, axes_limits=None):
        self.plot_num = plot_num
        self.title = title
        self.x_label = axes_labels[0]
        self.y_label = axes_labels[1]
        self.legend_loc = legend_loc
        if not axes_limits == None:
            self.x_limits = axes_limits[0]
            self.y_limits = axes_limits[1]
        self.subplots = []

    def add_subplot(self, x, y, label=''):
        self.subplots.append(SubPlot(self.plot_num, x, y, label))

    def show(self):
        plt.figure(self.plot_num)
        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.legend(loc=self.legend_loc)
        try:
            plt.x_limit(self.x_limits)
            plt.x_limit(self.x_limits)
        except AttributeError:
            pass


class Plotter:
    def __init__(self, path, data_file):
        data = np.loadtxt(os.path.join(path, data_file[0]), comments='#', delimiter=',', skiprows=3)
        if len(data_file) > 1:
            for ii, f in enumerate(data_file[1:]):
                data_temp = np.loadtxt(os.path.join(path, f), comments='#', delimiter=',', skiprows=3)
                try:
                    data = np.append(data, data_temp, axis=0)
                except ValueError:
                    data = np.append(data, np.array([data_temp]), axis=0)
        self.good_points = np.where(data[:, 4] > 1.2)
        temp_var = re.findall(r'\d+', data_file[0])
        temp_str = '%s.%s' % (temp_var[-2], temp_var[-1])
        self.time_data_taken = float(temp_str)
        self.time = data[:, 0][self.good_points]
        self.temperature1 = data[:, 1][self.good_points]
        self.temperature2 = data[:, 2][self.good_points]
        self.frequency = data[:, 3][self.good_points]
        self.frequencies = np.sort(np.unique(self.frequency))
        self.freq_locs = {}
        for freq in self.frequencies:
            self.freq_locs[str(freq)] = np.where(self.frequency == freq)
        self.capacitance = data[:, 4][self.good_points]
        self.loss = data[:, 5][self.good_points]
        self.plots = []
        self.plot_count = len(self.plots)

    def add_plot(self, title, axes_labels, legend_loc=1):
        self.plots.append(Plot(self.plot_count, title, axes_labels, legend_loc))
        self.plot_count += 1

    def append_plot(self, plot_num, x, y, label='', date=False):
        self.plots[plot_num].add_subplot(x, y, label)
        if date:
            self.plots[plot_num].subplots[len(self.plots[plot_num].subplots) - 1].plot_date()
        else:
            self.plots[plot_num].subplots[len(self.plots[plot_num].subplots) - 1].plot()

    def plot_Y_v_X(self, X, Y, title='', labels=['', ''], legend_loc=1):
        if 'time' in labels[0].lower():
            date = True
        else:
            date = False
        self.add_plot("%s %s" % (title, time.ctime(self.time_data_taken)),
                      labels, legend_loc=legend_loc)
        temp_plot_count = self.plot_count
        self.append_plot(temp_plot_count - 1, X, Y, label=None, date=date)

    def plot_Y_v_X_freq(self, X, Y, title='', labels=['', ''], legend_loc=1):
        if 'time' in labels[0].lower():
            date = True
        else:
            date = False
        self.add_plot("%s %s" % (title, time.ctime(self.time_data_taken)),
                      labels, legend_loc=legend_loc)
        temp_plot_count = self.plot_count
        for ii, freq in enumerate(self.frequencies):
            x = X[self.freq_locs[str(freq)]]
            y = Y[self.freq_locs[str(freq)]]
            self.append_plot(temp_plot_count - 1, x, y, str(int(freq)) + 'Hz', date=date)
            self.add_plot("%s %s\n @ Frequency: %dHz"
                          % (title, time.ctime(self.time_data_taken), freq),
                          labels, legend_loc)
            self.append_plot(temp_plot_count + ii, x, y, str(int(freq)) + 'Hz', date=date)

    def plot_cap_v_temp(self):
        self.plot_Y_v_X_freq(self.temperature1, self.capacitance, "Capacitance vs Temperature",
                             ['Temperature [K]', 'Capacitance [pF]'], legend_loc=2)

    def plot_cap_v_time(self):
        self.plot_Y_v_X_freq(self.time, self.capacitance, "Capacitance vs Time",
                             ['Time [min]', 'Capacitance [pF]'], legend_loc=1)

    def plot_loss_v_temp(self):
        self.plot_Y_v_X_freq(self.temperature1, self.loss, "Loss vs Temperature",
                             ['Temperature [K]', 'Loss Tangent'], legend_loc=2)

    def plot_loss_v_time(self):
        self.plot_Y_v_X_freq(self.time, self.loss, "Loss vs Time",
                             ['Time [min]', 'Loss Tangent'], legend_loc=1)

    def plot_temp_v_time(self):
        self.plot_Y_v_X(self.time, self.temperature1, "Temperature vs Time",
                        ['Time [min]', 'Temperature [K]'])


    def show(self):
        for plot in self.plots:
            plot.show()
        plt.show()


if __name__ == "__main__":
    import sys;

    sys.path.append('..')
    import GPIB.get as get

    filepath = os.path.join(get.google_drive(), 'Dielectric_data', 'Teddy')
    filenames = ['Temp_sweep_1464811905_09.csv', 'Hysteresis_Check_1464971562_48.csv']
    plotters = []
    for filename in filenames:
        plotters.append(Plotter(os.path.join(filepath, filename)))
    for plotter in plotters:
        plotter.plot_loss_v_temp()
        # plotter.plot_loss_v_time()
        plotter.show()
