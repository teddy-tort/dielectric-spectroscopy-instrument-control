import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot, QRunnable, Qt, QThread, QObject, pyqtSignal
import PyQt5.QtGui as qtg
from start_meas_dialog import StartMeasDialog
import threading
import client_tools
import socket
import time


class ControlTab(qtw.QWidget):
    def __init__(self, parent):
        super(qtw.QWidget, self).__init__(parent)
        self.parent = parent

        self.ls = None  # lakeshore class will pull from measure tabs .data class

        self.layout = qtw.QVBoxLayout(self)

        intro = qtw.QLabel("LakeShore Remote Control")
        intro.setAlignment(Qt.AlignCenter)
        intro.setFont(qtg.QFont('Arial', 20))
        self.layout.addWidget(intro)

        """CONTROLS"""
        labels = ['Model', 'Heater Power Range [W]', 'Ramp Speed [K/min]', 'Setpoint [K]', 'PID']

        self.modelChoice = qtw.QComboBox()
        self.model_choices = ['LS331', 'LS340']
        self.modelChoice.addItems(self.model_choices)

        self.heaterRangeChoice = qtw.QComboBox()
        self.heater_range_choices = ['Off', '500 mW', '5 W']
        self.heaterRangeChoice.addItems(self.heater_range_choices)

        self.rampSpeed = qtw.QSpinBox()
        self.rampSetButton = qtw.QPushButton()
        self.rampSetButton.setText('Apply')
        self.rampSetButton.setFixedWidth(100)
        self.rampSetButton.clicked.connect(self.set_ramp_speed)

        self.setpointEntry = qtw.QSpinBox()
        self.setpointButton = qtw.QPushButton()
        self.setpointButton.setText('Apply')
        self.setpointButton.setFixedWidth(100)
        self.setpointButton.clicked.connect(self.set_setpoint)

        self.pValue = qtw.QSpinBox()
        self.iValue = qtw.QSpinBox()
        self.dValue = qtw.QSpinBox()
        self.pidButton = qtw.QPushButton()
        self.pidButton.setText('Apply')
        self.pidButton.setFixedWidth(100)
        self.pidButton.clicked.connect(self.set_PID)

        widgets = [[self.modelChoice],
                   [self.heaterRangeChoice],
                   [self.rampSpeed, self.rampSetButton],
                   [self.setpointEntry, self.setpointButton],
                   [self.pValue, self.iValue, self.dValue, self.pidButton]]

        grid = qtw.QGridLayout()

        for ii, label, widget in zip(range(len(labels)), labels, widgets):
            labelW = qtw.QLabel(label)
            labelW.setAlignment(Qt.AlignRight | Qt.AlignCenter)
            # labelW.setSizePolicy(qtg.QSizePolicy.Expanding, qtg.QSizePolicy.Expanding)
            labelW.setFont(qtg.QFont('Arial', 16))
            row_widget = qtw.QWidget()
            row_layout = qtw.QHBoxLayout()
            for w in widget:
                if not (isinstance(w, qtw.QComboBox) or isinstance(w, qtw.QPushButton)):
                    w.setAlignment(Qt.AlignCenter)
                w.setFont(qtg.QFont('Arial', 16))
                row_layout.addWidget(w)
            row_widget.setLayout(row_layout)
            grid.addWidget(labelW, ii, 0)
            grid.addWidget(row_widget, ii, 1)
        self.layout.addLayout(grid)

        """UPDATED VALUES"""

        live_rowW = qtw.QWidget()
        live_rowL = qtw.QHBoxLayout()

        labels = ['Temperature', 'Heater Output', 'Setpoint', 'Ramp Status']
        colors = ['lightblue', 'pink', 'lightgrey', 'lightgreen']
        widths = [120, 110, 120, 50]

        self.tempValue = qtw.QLineEdit()
        self.heaterValue = qtw.QLineEdit()
        self.setpointValue = qtw.QLineEdit()
        self.rampStatus = qtw.QLineEdit()

        widgets = [self.tempValue, self.heaterValue, self.setpointValue, self.rampStatus]

        for label, widget, color, width in zip(labels, widgets, colors, widths):
            labelW = qtw.QLabel(label)
            labelW.setFont(qtg.QFont('Arial', 16))
            widget.setReadOnly(True)
            widget.setFont(qtg.QFont('Arial', 16))
            widget.setStyleSheet("QLineEdit{background : %s;}" % color)
            widget.setAlignment(Qt.AlignRight)
            widget.setFixedWidth(width)
            live_rowL.addWidget(labelW)
            live_rowL.addWidget(widget)
        live_rowW.setLayout(live_rowL)
        self.layout.addWidget(live_rowW)
        self.setLayout(self.layout)

    def update_values(self, temperature, heater, setpoint, ramp):
        print(temperature)
        self.tempValue.setText('%.2f K' % temperature)
        self.heaterValue.setText(f'{heater} %')
        self.setpointValue.setText('%.2f K' % setpoint)
        self.rampStatus.setText('On' if ramp else 'Off')

    def initialize(self):
        print('\n\n initialize received \n\n')
        self.ls = self.parent.tabMeas.data.ls

        self.modelChoice.setCurrentIndex(self.model_choices.index(f'LS{self.ls.inst_num}'))
        hrange = self.ls.read_heater_range()
        if hrange > 1:
            hstring = f'{int(hrange)} W'
        elif not hrange:
            hstring = 'Off'
        else:
            hstring = f'{int(hrange*1000)} mW'
        self.heaterRangeChoice.setCurrentIndex(self.heater_range_choices.index(hstring))
        self.rampSpeed.setText(self.ls.read_ramp_speed())
        self.setpointEntry.setText(self.ls.read_setpoint())
        pid = self.ls.read_PID()
        self.pValue.setText(pid[0])
        self.iValue.setText(pid[1])
        self.dValue.setText(pid[2])

    @pyqtSlot()
    def set_heater_range(self):
        t = threading.Thread(target=self.set_heater_range_thread, args=())
        t.start()

    def set_heater_range_thread(self):
        hstring = self.heaterRangeChoice.text()
        if hstring == 'Off':
            hrange = 0.
        elif 'mW' in hstring:
            hrange = float(hstring.strip('mW'))
        else:
            hrange = float(hstring.strip('W'))
        self.ls.set_heater_range(hrange)

    @pyqtSlot()
    def set_ramp_speed(self):
        t = threading.Thread(target=set_ramp_speed_thread, args=())
        t.start()

    def set_ramp_speed_thread(self):
        self.ls.set_ramp_speed(float(self.rampSpeed.text()))

    @pyqtSlot()
    def set_setpoint(self):
        t = threading.Thread(target=self.set_setpoint_thread, args=())
        t.start()

    def set_setpoint_thread(self):
        self.ls.set_setpoint(float(self.setpointEntry.text()))

    @pyqtSlot()
    def set_PID(self):
        t = threading.Thread(target=self.set_PID_thread, args=())
        t.start()

    def set_PID_thread(self):
        self.ls.set_PID(float(self.pValue.text()), float(self.iValue.text(), float(self.dValue.text())))
