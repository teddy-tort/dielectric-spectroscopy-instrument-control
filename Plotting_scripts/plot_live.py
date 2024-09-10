# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 16:52:03 2017

@author: Teddy
"""
# date you want to plot in "mm-dd-yyyy" (None will choose today)
date = None
# date = "12-01-2020"
# date = '11-14-2017'

# string of bools to select files
fb = None
#fb = [0, 0, 1]
# fb[-1] = 1
# fb = [0,1,1,0,0]
# fb = [1,0]

HP = 0


import os
import sys
sys.path.append('..')
import get
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import numpy as np
import datetime
import DateAxisItem
import time
import data_files
import itertools
import csv
import operator
try:
    import Tkinter
    from Tkinter import filedialog
except ImportError:
    import tkinter as Tkinter
    from tkinter import filedialog

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


def most_common(L):
    """Returns the value found most common in a list"""
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))
    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index
    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


def get_labels(f):
    """Retrieve data file's comment"""
    with open(f[0], 'r') as fff:
        labels = next(itertools.islice(csv.reader(fff), 2, None))
    return labels


def get_f_labels(f):
    global labels
    f_labels = [''] * 3
    ii = 0
    # print 'it is here'
    for label in labels:
        # print(label)
        if 'Frequency' in label:
            label_list = label.strip(' ').split(' ')
            print(label_list)
            for ll in label_list:
                # print(ll)
                if 'Hz' in ll and ll.strip('[').strip(']') == ll:
                    # print(ll)
                    f_labels[ii] = ll.strip('(').strip(')')
                    ii += 1
    # print('\n', f_labels, '\n')
    return f_labels


def load_data(files_to_use):
    skip = 0
    temp_skip = -1
    while not skip == temp_skip:  # as long as the "try" passes, the while loop dies
        temp_skip = skip
        try:
            data = np.loadtxt(files_to_use[0], comments='#', delimiter=',', skiprows=3)
        except StopIteration:
            skip += 1
    if len(files_to_use) > 1:
        for ii, f in enumerate(files_to_use[1:]):
            try:
                data_temp = np.loadtxt(f, comments='#', delimiter=',', skiprows=3)
                try:
                    data = np.append(data, data_temp, axis=0)
                except ValueError:
                    data = np.append(data, np.array([data_temp]), axis=0)
            except StopIteration:
                pass
    return data

    
def updateViews():
    global p4a, p4
    p4a.setGeometry(p4.getViewBox().sceneBoundingRect())
    p4a.linkedViewChanged(p4.getViewBox(), p4a.XAxis)


def update():
    global files, c_curves, l_curves, ct_curves, lt_curves, T_curves, labels, flabels,\
        time_indexes, cap_indexes, loss_indexes, tempA_indexes, tempB_indexes
    data = load_data(files)

    ts = [data[:, ind] for ind in time_indexes]
    Ts = [data[:, ind] for ind in tempA_indexes]
    if tempB_indexes:
        TBs = [data[:, ind] for ind in tempB_indexes]
    else:
        TBs = None
    Cs = [data[:, ind] for ind in cap_indexes]
    Ls = [data[:, ind] for ind in loss_indexes]

    for curve, t, C in zip(ct_curves, ts, Cs):
        curve.setData(x=t, y=C)
    for curve, t, L in zip(lt_curves, ts, Ls):
        curve.setData(x=t, y=L)
    for curve, T, C in zip(c_curves, Ts, Cs):
        curve.setData(x=T, y=C)
    for curve, T, L in zip(l_curves, Ts, Ls):
        curve.setData(x=T, y=L)
    if TBs:
        data = np.column_stack((np.concatenate(ts),
                                np.concatenate(Ts),
                                np.concatenate(TBs)))
    else:
        data = np.column_stack((np.concatenate(ts),
                                np.concatenate(Ts)))
    data = np.array(sorted(data, key=lambda row: row[0]))
    for ii, curve in enumerate(T_curves):
        curve.setData(x=data[:, 0], y=data[:, ii+1])


if __name__ == '__main__':
    root = Tkinter.Tk()
    root.title('File Selector')

    files = filedialog.askopenfilenames(initialdir=os.path.join(get.google_drive(), 'Dielectric_data', 'Teddy-2'),
                                        title='Select a data file to plot',
                                        filetypes=(('CSV files', '*.csv',), ('all files', '*.*')))

    RC_count = 0
    Z_count = 0
    y_Alabel = 'Capacitance (pF)'
    y_Blabel = 'Loss Tangent'

    title = "Live Plotting"
    app = pg.QtGui.QApplication([])
    win = pg.GraphicsWindow(title="Live Plotting")
    win.resize(1900, 1000)
    win.setWindowTitle(title)
        
    # enable antialiasing
    pg.setConfigOptions(antialias=True)
        
    p1 = win.addPlot(title=title, row=0, col=0)
    p1.setLabel('left', y_Alabel)
    p1.setLabel('bottom', 'Temperature (K)')
    p1.addLegend()
    
    p2 = win.addPlot(title='', row=1, col=0)
    p2.setLabel('left', y_Blabel)
    p2.setLabel('bottom', 'Temperature (K)')
    p2.addLegend()
    
    p2.setXLink(p1)
    
    p3 = win.addPlot(title='',
                     axisItems={'bottom': DateAxisItem.DateAxisItem('bottom')},
                     row=0, col=1)
    p3.setLabel('left', 'Temperature (K)')
    p3.addLegend()

    p4 = win.addPlot(title='',
                     axisItems={'bottom': DateAxisItem.DateAxisItem('bottom')},
                     row=1, col=1)
    p4.setLabel('left', y_Alabel)
    p4.showAxis('right')
    p4.setLabel('right', y_Blabel)
    
    p4a = pg.ViewBox()
    p4.scene().addItem(p4a)
    p4.getAxis('right').linkToView(p4a)
    p4a.setXLink(p4)
    p3.setXLink(p4)

    colors6 = [(204, 0, 0),    # dark red
               (76, 153, 0),   # dark green
               (0, 0, 204),    # dark blue
               (255, 128, 0),  # orange
               (0, 204, 204),  # cyan
               (153, 51, 255)] # purple
    colors2 = [(255, 0, 0), (0, 0, 255)]
    pens6 = [''] * len(colors6)
    pens2 = [''] * len(colors2)
    for ii, color in enumerate(colors6):
        pens6[ii] = pg.mkPen(color, width=2)
    for ii, color in enumerate(colors2):
        pens2[ii] = pg.mkPen(color, width=2)
    c_curves = ['']
    l_curves = [''] 
    ct_curves = ['']
    lt_curves = ['']
    if not HP:
        c_curves *= 3
        l_curves *= 3
        ct_curves *= 6
        lt_curves *= 3
    else:
        ct_curves *= 2

    labels = get_labels(files)
    print(labels)

    flabels = [''] * len(files)
    for ii, f in enumerate(files):
        flabels[ii] = get_f_labels(files)
        print(flabels)

    flabels = most_common(flabels)

    for ii, label in enumerate(flabels):
        offset = len(flabels)
        c_curves[ii] = p1.plot(pen=pens6[ii], name=label)
        l_curves[ii] = p2.plot(pen=pens6[ii+offset], name=label)
        ct_curves[ii] = p4.plot(pen=pens6[ii], name=label+' capacitance')
        ct_curves[ii+offset] = p4.plot(pen=pens6[ii+offset], name=label+' loss')
        lt_curves[ii] = pg.PlotCurveItem(pen=pens6[ii+offset], name=label)
        p4a.addItem(lt_curves[ii])

    stage_num = 1
    T_labels = ['Sample Stage']
    for l in labels:
        if 'temperature b' in l.lower():
            stage_num += 1
            T_labels.append('Cooling Stage')
            break
    T_curves = [None] * stage_num

    for ii, l in enumerate(T_labels):
        T_curves[ii] = p3.plot(pen=pens2[ii], name=l)

    time_indexes = [ii for ii, ll in enumerate(labels) if 'time' in ll.lower()]
    if len(T_labels) == 1:
        tempA_indexes = [ii for ii, ll in enumerate(labels) if 'temperature' in ll.lower()]
        tempB_indexes = None
    else:
        tempA_indexes = [ii for ii, ll in enumerate(labels) if 'temperature a' in ll.lower()]
        tempB_indexes = [ii for ii, ll in enumerate(labels) if 'temperature b' in ll.lower()]
    cap_indexes = [ii for ii, ll in enumerate(labels) if 'capacitance' in ll.lower()]
    loss_indexes = [ii for ii, ll in enumerate(labels) if 'loss' in ll.lower()]
    print(time_indexes)
    print(tempA_indexes)
    print(cap_indexes)
    print(loss_indexes)

    updateViews()
    p4.getViewBox().sigResized.connect(updateViews)
    
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(50)
    pg.QtGui.QApplication.instance().exec_()