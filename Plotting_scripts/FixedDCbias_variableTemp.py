"""Code for plotting presentation quality plots"""

import numpy as np
import matplotlib.pylab as plt
import data_files
import os
import datetime
import calendar
from matplotlib.pylab import rcParams
import csv
import sys;
sys.path.append('../GPIB')
import get

date = str(datetime.date.today()).split('-')
yearstr = date[0]
monthstr = date[1]
daystr = date[2]
year = int(yearstr)
month = int(monthstr)
day = int(daystr)

#print "%s/%s/%s" % (monthstr, daystr, yearstr)

# input parameters for easy tweaking
# bounds for good data
scrub = True
cap_bounds = [1., 1.45]
loss_bounds = [-0.1, 0.2]
temp_bounds = [6, 410]

# where to cut off time plot
start_time = 2.8
end_time = None

start_temp = 120
end_temp = 410


time_axis = 'hr'

if 'min' in time_axis.lower():
    time_factor = 60
elif 'hr' in time_axis.lower():
    time_factor = 60 * 60
else:
    time_axis = 'min'
    time_factor = 60

# store inputs
titles = ['Capacitance vs Time',
          'Capacitance vs Temperature',
          'Loss vs Time',
          'Loss vs Temperature',
          'Capacitance and Loss vs Time',
          'Capacitance and Loss vs Temperature',
          'Log2 omega vs inverse T of Loss Peak']
axes_labelss = [['Time [%s]' % time_axis, 'Capacitance [pF]', 'Temperature [K]'],
                ['Temperature [K]', 'Capacitance [pF]'],
                ['Time [%s]' % time_axis, 'Loss Tangent', 'Temperature [K]'],
                ['Temperature [K]', 'Loss Tangent'],
                ['Time [%s]' % time_axis, 'Loss Tangent', 'Capacitance [pF]'],
                ['Temperature [K]', 'Loss Tangent', 'Capacitance [pF]'],
                ['1/T [1/K]', 'Log2(omega)']]
#legend_locs = [0, 2, 0, 2, 0, 2]
legend_locs = ['best', 'best', 'best', 'best', 'best', 'best', 'best']

plot_ranges = [[False, False], [False], [False, False], [False], [False, False], [False, False], [False, False]]
#plot_ranges = [[[start_cap, end_cap], [start_temp, end_temp]],
#               [[start_cap, end_cap]],
#               [[start_loss, end_loss], [start_temp, end_temp]],
#               [[start_loss, end_loss]],
#               [[start_cap, end_cap], [start_loss, end_loss]],
#               [[start_cap, end_cap], [start_loss, end_loss]]]


if len(sys.argv) >= 2:
    datemsg = sys.argv[1].split('-')
    if len(datemsg) == 2:
        month = int(datemsg[0])
        day = int(datemsg[1])
        monthstr = datemsg[0]
        daystr = datemsg[1]
    elif len(datemsg) == 3:
        year = int(datemsg[2])
        month = int(datemsg[0])
        day = int(datemsg[1])
        yearstr = datemsg[2]
        monthstr = datemsg[0]
        daystr = datemsg[1]
    elif len(datemsg) == 1:
        try:
            day = int(datemsg[0])
            daystr = datemsg[0]
        except ValueError:
            pass
if len(daystr) == 1:
    daystr = '0' + daystr
if len(monthstr) == 1:
    monthstr = '0' + monthstr
if len(yearstr) == 2:
    yearstr = '20' + yearstr

print "%d/%d/%d" % (month, day, year)
print "%s/%s/%s" % (monthstr, daystr, yearstr)

if len(sys.argv) >= 3:
    try:
        timemsg = sys.argv[2].strip('[').strip(']').split(',')
        start_time = timemsg[0]
        end_time = timemsg[1]
        print end_time
    except IndexError:
        print 'index error'
        pass
if len(sys.argv) >= 4:
    if sys.argv[3].lower() == 'off':
        scrub = False
    else:
        scrub = True
        scrubmsg = sys.argv[3].strip('[').strip(']').split(',')
        cap_bounds = [scrubmsg[0], scrubmsg[1]]
        loss_bounds = [scrubmsg[2], scrubmsg[3]]
print end_time

def load_data(file_path, file_names, scrub=True, cap_bounds=[1.2, 1.3], loss_bounds=[-0.5, 1]):
    data = {}
    print file_names
    for ii, f in enumerate(file_names):
        with open(os.path.join(file_path, f), 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for ii, row in enumerate(csvreader):
                if ii > 1:
                    break
                if ii == 1:
                    voltage = row[-1]
        loop = True
        while loop:
            if voltage == '':
                voltage = 0
                loop = False
            try:
                voltage = float(voltage)
                loop = False
            except ValueError:
                voltage = voltage[:-1]
        data_temp = np.loadtxt(os.path.join(file_path, f), comments='#', delimiter=',', skiprows=4)
        if scrub:
            data_temp = scrub_data(data_temp, cap_bounds, loss_bounds)
        data[str(voltage)] = data_temp
    return data


def scrub_data(data_old, cap_bounds=[1.2, 1.3], loss_bounds=[-0.5, 1]):
    cap_bounds = sorted(cap_bounds)
    loss_bounds = sorted(loss_bounds)
    # print np.shape(data_old)
    good_cap_data = np.where(np.logical_and(data_old[:, 4] > cap_bounds[0], data_old[:, 4] <= cap_bounds[1]))
    data_temp = data_old[good_cap_data]
    # print np.shape(data_temp)
    good_loss_data = np.where(np.logical_and(data_temp[:, 5] > loss_bounds[0], data_temp[:, 5] <= loss_bounds[1]))
    data_temp2 = data_temp[good_loss_data]
    # print np.shape(data_new)
    good_temper_data = np.where(np.logical_and(data_temp2[:, 1] > temp_bounds[0], data_temp2[:, 1] <= temp_bounds[1]))
    data_new = data_temp2[good_temper_data]
    return data_new


def plot(x, y, plot_range=None, marker='b-', label='', ax='L'):
    """Plots y vs x; marker: search 'pyplot.plot' at http://matplotlib.org/api/pyplot_api.html"""
    plot_num = len(plotlist)
    if 'L' in ax.upper():
        #plot_num = len(plotlistL)
        p, = axL.plot(x, y, marker, label=label, linewidth=3)
        if plot_range:
            axL.ylim(plot_range)
        #plotlistL.append(p)
        if len(axes_labels) == 3:
            if 'cap' in axes_labels[2].lower():
                z = [capacitance[2]]
            elif 'temp' in axes_labels[2].lower():
                z = [temperature1[2]]
            if 'time' in axes_labels[0].lower():
                w = [timestamps[0]]
            elif 'temp' in axes_labels[0].lower():
                w = [temperature1[0]]
            # print z
            axR.plot(w, z, marker, label=label, linewidth=3)
    elif 'R' in ax.upper():
        #plot_num = len(plotlistR)
        p, = axR.plot(x, y, marker, label=label, linewidth=3)
        if plot_range:
            axL.ylim(plot_range)
        #plotlistR.append(p)
    plotlist.append(p)


def plot_sep_freq(x, y, freqs, plot_range, label='', ax='L'):
    """plot something separating frequencies"""
    if 'L' in ax.upper():
        pen = ['k-', 'r-', 'b-', 'm-', 'y-', 'g-']
        #pen = ['ko', 'ro', 'bo', 'mo', 'yo', 'go']
    elif 'R' in ax.upper():
        pen = ['k--', 'r--', 'b--', 'm--', 'y--', 'g--']
        #pen = ['kv', 'rv', 'bv', 'mv', 'yv', 'gv']
    frequencies_unique = np.sort(np.unique(freqs))
    if frequencies_unique[0] == -1:
        frequencies_unique = np.delete(frequencies_unique, 0)
    freq_locs = {}
    for freq in frequencies_unique:
        freq_locs[str(freq)] = np.where(freqs == freq)
    for ii, freq in enumerate(frequencies_unique):
        #if 'L' in ax:
        #    plot_num = len(plotlistL)
        #elif 'R' in ax:
        #    plot_num = len(plotlistR)
        plot_num = len(plotlist)
        plot(x[freq_locs[str(freq)]], y[freq_locs[str(freq)]], plot_range=plot_range,
             marker=pen[ii], label='%s %d Hz' % (label, freq), ax=ax)
        #if 'L' in ax:
        #    plotlistL[plot_num].freqs = freqs
        #elif 'R' in ax:
        #    plotlistR[plot_num].freqs = freqs

def plot_peaks(temperature, loss, omega):
    """plot log2(omega) vs 1/T of the loss peak."""
    cut = np.where(temperature < 180)
    temperature = temperature[cut]
    loss = loss[cut]
    omega = omega[cut]
    frequencies_unique = np.sort(np.unique(omega))
    freq_locs = {}
    for freq in frequencies_unique:
        freq_locs[str(freq)] = np.where(omega == freq)
    loss_peaks = np.array([])
    temperature_peaks = np.array([])
    for freq in frequencies_unique:

        temp_loss_peak = np.amax(loss[freq_locs[str(freq)]])
        np.append(loss_peaks, temp_loss_peak)
        loss_peak_loc = np.where(loss == temp_loss_peak)
        np.append(temperature_peaks, temperature[loss_peak_loc])
    plot(1./temperature_peaks, np.log2(loss_peaks), None, 'ro')



if 1:
#try:
    filepath = os.path.join(get.google_drive(), 'Dielectric_data', 'Teddy', yearstr, monthstr, daystr)
    filenames = data_files.file_name(monthstr, daystr, yearstr)
    #print 'blah'
    #print filenames[0]
    #print 'blah'
    data = load_data(filepath, filenames[0], scrub, cap_bounds, loss_bounds)
    #print 'hahahahaha'
#except:
#    filepath = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')
#    filenames = data_files.file_name(month, day, year)
#
#    print filenames[0]
#
#    data = load_data(filepath, filenames[0], scrub, cap_bounds, loss_bounds)
print np.shape(data)

for ii, key in enumerate(data.keys()):

    timestamps = (data[key][:, 0] - data[key][0, 0]) / time_factor
    temperature1 = data[key][:, 1]
    temperature2 = data[key][:, 2]
    freqs = data[key][:, 3]
    capacitance = data[key][:, 4]
    loss = data[key][:, 5]


    #start_trim = np.argmax(timestamps > 0)
    try:
        end_trim = len(timestamps) - np.argmax(timestamps[::-1] < int(end_time))
    except TypeError:
        end_trim = None
    start_trim = np.argmax(timestamps > int(start_time))

    #end_trim = None
    time_trims = [[start_trim, end_trim],
             [start_trim, end_trim],
             [start_trim, end_trim],
             [start_trim, end_trim],
             [start_trim, end_trim],
             [start_trim, end_trim],
             [start_trim, end_trim]]
    plot_ratio = np.array([6, 4])
    if 'linux' in sys.platform:
        plot_ratio[0] += 0.5
    plot_size = plot_ratio*1.8
    # if on mac, make plots bigger
    # if sys.platform == 'darwin':
    #     plot_size *= 1.75
    rcParams['figure.figsize'] = plot_size[0], plot_size[1]

    font = {'size': 20, 'color': 'k'}

    # titles = titles[:1]
    # axes_labelss = axes_labelss[:1]



    for title, axes_labels, time_trim, legend_loc, plot_range in \
            zip(titles, axes_labelss, time_trims, legend_locs, plot_ranges):
        start_trim = int(time_trim[0])
        end_trim = time_trim[1]
        # generate graphic
        fig, axL = plt.subplots()
        fig.set_size_inches(plot_size[0], plot_size[1], forward=True)

        # set title
        fig.suptitle(title + '; DC bias = %sV' % key, fontsize=font['size'], color=font['color'])

        # set axes labels
        axL.set_xlabel(axes_labels[0], fontsize=font['size'], color=font['color'])
        axL.set_ylabel(axes_labels[1], fontsize=font['size'], color=font['color'])

        # edit tick labels
        for tl in axL.get_yticklabels():
            tl.set_color(font['color'])
            tl.set_fontsize(font['size'])

        for tl in axL.get_xticklabels():
            tl.set_color(font['color'])
            tl.set_fontsize(font['size'])

        # generate 2nd y axis if 3 axes_labels given
        if len(axes_labels) > 2:
            axR = axL.twinx()
            axR.set_ylabel(axes_labels[2], fontsize=font['size'], color=font['color'])
            for tl in axR.get_yticklabels():
                tl.set_color(font['color'])
                tl.set_fontsize(font['size'])
            axR.get_yaxis().get_major_formatter().set_useOffset(False)
        axL.get_xaxis().get_major_formatter().set_useOffset(False)
        axL.get_yaxis().get_major_formatter().set_useOffset(False)
        # seed plotlists
        #plotlistL = []
        #plotlistR = []
        plotlist = []

        if title == 'Capacitance vs Time':
            plot_sep_freq(timestamps[start_trim: end_trim], capacitance[start_trim: end_trim], freqs[start_trim: end_trim],
                          plot_range[0])
            plot(timestamps[start_trim: end_trim], temperature1[start_trim: end_trim], plot_range[1],
                 marker='r--', label='Stage A Temperature', ax='R')
            plot(timestamps[start_trim: end_trim], temperature2[start_trim: end_trim], plot_range[1],
                 marker='b--', label='Stage B Temperature', ax='R')
        elif title == 'Capacitance vs Temperature':
            plot_sep_freq(temperature1[start_trim: end_trim], capacitance[start_trim: end_trim],
                          freqs[start_trim: end_trim], plot_range[0])
        elif title == 'Loss vs Time':
            plot_sep_freq(timestamps[start_trim: end_trim], loss[start_trim: end_trim], freqs[start_trim: end_trim],
                          plot_range[0])
            plot(timestamps[start_trim: end_trim], temperature1[start_trim: end_trim], plot_range[1],
                 marker='r--', label='Stage A Temperature', ax='R')
            plot(timestamps[start_trim: end_trim], temperature2[start_trim: end_trim], plot_range[1],
                 marker='b--', label='Stage B Temperature', ax='R')
        elif title == 'Loss vs Temperature':
            plot_sep_freq(temperature1[start_trim: end_trim], loss[start_trim: end_trim], freqs[start_trim: end_trim],
                          plot_range[0])
        elif title == 'Capacitance and Loss vs Time':
            plot_sep_freq(timestamps[start_trim: end_trim], capacitance[start_trim: end_trim],
                          freqs[start_trim: end_trim], plot_range[0], label='Capacitance', ax='R')
            plot_sep_freq(timestamps[start_trim: end_trim], loss[start_trim: end_trim],
                          freqs[start_trim: end_trim], plot_range[1], label='Loss')
        elif title == 'Capacitance and Loss vs Temperature':
            plot_sep_freq(temperature1[start_trim: end_trim], capacitance[start_trim: end_trim],
                          freqs[start_trim: end_trim], plot_range[0], label='Capicatance', ax='R')
            plot_sep_freq(temperature1[start_trim: end_trim], loss[start_trim: end_trim],
                          freqs[start_trim: end_trim], plot_range[1], label='Loss')
        #elif title == 'Log2(omega) vs 1/T of Loss Peak':
        #    plot_peaks(temperature1[start_trim: end_trim], loss[start_trim: end_trim], freqs[start_trim: end_trim])
        print title
        print axes_labels
        print time_trim
        print legend_loc

        if'linux' in sys.platform.lower():
            plt.legend(handles=plotlist, loc=legend_loc)
        else:
            plt.legend(loc=legend_loc)

        plt.tight_layout()
        fig.subplots_adjust(top=0.9)

        #turn on grid lines
        axL.grid(True)

        ticklines = axL.get_xticklines() + axL.get_yticklines()
        gridlines = axL.get_xgridlines() + axL.get_ygridlines()

        for line in ticklines:
            line.set_linewidth(3)

        for line in gridlines:
            line.set_linestyle('-')

        if len(str(month)) == 1:
            m = '0' + str(month) + '_'
        else:
            m = str(month) + '_'

        path_to_save = os.path.join(get.google_drive(), 'Dielectric_data', 'Graphs', str(year), m + calendar.month_name[month],
                                    str(day))

        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)

        plt.savefig(os.path.join(path_to_save, title),
                    dpi=None, facecolor='w', edgecolor='w',
                    orientation='portrait', papertype=None, format=None,
                    transparent=False, bbox_inches=None, pad_inches=0.1,
                    frameon=None)


plt.show()

