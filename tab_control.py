import PyQt5.QtWidgets as qtw
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal
import PyQt5.QtGui as qtg
import threading


class ButtonHandler(qtw.QWidget):

    ave = pyqtSignal(bool)
    heater = pyqtSignal(bool)
    ramp = pyqtSignal(bool)
    setpt = pyqtSignal(bool)
    pid = pyqtSignal(bool)

    def activate(self, label):
        label = label.lower()
        if 'ave' in label:
            self.ave.emit(True)
        elif 'heat' in label:
            self.heater.emit(True)
        elif 'ramp' in label:
            self.ramp.emit(True)
        elif 'set' in label:
            self.setpt.emit(True)
        elif 'pid' in label:
            self.pid.emit(True)

    def deactivate(self, label):
        label = label.lower()
        if 'ave' in label:
            self.ave.emit(False)
        elif 'heat' in label:
            self.heater.emit(False)
        elif 'ramp' in label:
            self.ramp.emit(False)
        elif 'set' in label:
            self.setpt.emit(False)
        elif 'pid' in label:
            self.pid.emit(False)

class ControlTab(qtw.QWidget):
    def __init__(self, parent):
        super(qtw.QWidget, self).__init__(parent)
        self.parent = parent

        self.ls = None  # lakeshore class will pull from measure tabs .data class
        self.button_handler = ButtonHandler()
        self.button_handler.ave.connect(self.averaging_button_active)
        self.button_handler.heater.connect(self.heater_button_active)
        self.button_handler.ramp.connect(self.ramp_button_active)
        self.button_handler.setpt.connect(self.setpt_button_active)
        self.button_handler.pid.connect(self.pid_button_active)

        self.layout = qtw.QVBoxLayout(self)

        bridge_intro = qtw.QLabel("Bridge Remote Control")
        bridge_intro.setAlignment(Qt.AlignCenter)
        bridge_intro.setFont(qtg.QFont('Arial', 20))
        self.layout.addWidget(bridge_intro)

        labels = ['Averaging']

        self.averagingTime = qtw.QSpinBox()
        self.averagingTime.setMaximum(15)
        self.averagingButton = qtw.QPushButton()
        self.averagingButton.setText('Apply')
        self.averagingButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.averagingButton.setFixedWidth(100)
        self.averagingButton.setFixedHeight(30)
        self.averagingButton.clicked.connect(self.set_averaging)
        self.aveUpdateButton = qtw.QPushButton()
        self.aveUpdateButton.setText('Refresh')
        self.aveUpdateButton.setFixedWidth(100)
        self.aveUpdateButton.clicked.connect(self.update_averaging)

        widgets = [[self.averagingTime, self.averagingButton, self. aveUpdateButton]]

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


        ls_intro = qtw.QLabel("LakeShore Remote Control")
        ls_intro.setAlignment(Qt.AlignCenter)
        ls_intro.setFont(qtg.QFont('Arial', 20))
        self.layout.addWidget(ls_intro)

        """CONTROLS"""
        labels = ['Model', 'Heater Power Range [W]', 'Ramp Speed [K/min]', 'Setpoint [K]', 'PID']

        self.modelChoice = qtw.QComboBox()
        self.model_choices = ['LS331', 'LS340']
        self.modelChoice.addItems(self.model_choices)

        self.heaterRangeChoice = qtw.QComboBox()
        self.heater_range_choices = ['Off', '500 mW', '5 W']
        self.heaterRangeChoice.addItems(self.heater_range_choices)
        self.heaterRangeChoice.activated.connect(self.set_heater_range)
        self.heaterRangeUpdateButton = qtw.QPushButton()
        self.heaterRangeUpdateButton.setText('Refresh')
        self.heaterRangeUpdateButton.setFixedWidth(100)
        self.heaterRangeUpdateButton.clicked.connect(self.update_heater_range)

        self.rampSpeed = qtw.QDoubleSpinBox()
        self.rampSpeed.setDecimals(1)
        self.rampSpeed.setMaximum(100.0)
        self.rampSetButton = qtw.QPushButton()
        self.rampSetButton.setText('Apply')
        self.rampSetButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.rampSetButton.setFixedWidth(100)
        self.rampSetButton.setFixedHeight(30)
        self.rampSetButton.clicked.connect(self.set_ramp_speed)
        self.rampUpdateButton = qtw.QPushButton()
        self.rampUpdateButton.setText('Refresh')
        self.rampUpdateButton.setFixedWidth(100)
        self.rampUpdateButton.clicked.connect(self.update_ramp_speed)

        self.setpointEntry = qtw.QDoubleSpinBox()
        self.setpointEntry.setDecimals(2)
        self.setpointEntry.setMaximum(400.00)
        self.setpointButton = qtw.QPushButton()
        self.setpointButton.setText('Apply')
        self.setpointButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.setpointButton.setFixedWidth(100)
        self.setpointButton.clicked.connect(self.set_setpoint)
        self.setptUpdateBotton = qtw.QPushButton()
        self.setptUpdateBotton.setText('Refresh')
        self.setptUpdateBotton.setFixedWidth(100)
        self.setptUpdateBotton.clicked.connect(self.update_setpoint)

        self.pValue = qtw.QDoubleSpinBox()
        self.iValue = qtw.QDoubleSpinBox()
        self.dValue = qtw.QDoubleSpinBox()
        self.pValue.setDecimals(1)
        self.iValue.setDecimals(1)
        self.dValue.setDecimals(1)
        self.pValue.setMaximum(1000.0)
        self.iValue.setMaximum(1000.0)
        self.dValue.setMaximum(1000.0)
        self.pidButton = qtw.QPushButton()
        self.pidButton.setText('Apply')
        self.pidButton.setStyleSheet("QPushButton{font-weight : bold}")
        self.pidButton.setFixedWidth(100)
        self.pidButton.clicked.connect(self.set_PID)
        self.pidUpdateButton = qtw.QPushButton()
        self.pidUpdateButton.setText('Refresh')
        self.pidUpdateButton.setFixedWidth(100)
        self.pidUpdateButton.clicked.connect(self.update_PID)

        widgets = [[self.modelChoice],
                   [self.heaterRangeChoice, self.heaterRangeUpdateButton],
                   [self.rampSpeed, self.rampSetButton, self.rampUpdateButton],
                   [self.setpointEntry, self.setpointButton, self.setptUpdateBotton],
                   [self.pValue, self.iValue, self.dValue, self.pidButton, self.pidUpdateButton]]

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
            # live_rowL.addWidget(labelW)
            live_rowL.addWidget(widget)
            live_rowL.addWidget(labelW)
        live_rowW.setLayout(live_rowL)
        self.layout.addWidget(live_rowW)
        self.setLayout(self.layout)

    @pyqtSlot(float, float, float, bool)
    def update_values(self, temperature, heater, setpoint, ramp):
        print(temperature)
        self.tempValue.setText('%.2f K' % temperature)
        self.heaterValue.setText(f'{heater} %')
        self.setpointValue.setText('%.2f K' % setpoint)
        self.rampStatus.setText('On' if ramp else 'Off')

    @pyqtSlot()
    def initialize(self):
        print('\n\n initialize received \n\n')
        self.ls = self.parent.tabMeas.data.ls
        self.bridge = self.parent.tabMeas.data.bridge

        self.averagingTime.setValue(self.bridge.read_ave())

        self.modelChoice.setCurrentIndex(self.model_choices.index(f'LS{self.ls.inst_num}'))
        hrange = self.ls.read_heater_range()
        if hrange > 1:
            hstring = f'{int(hrange)} W'
        elif not hrange:
            hstring = 'Off'
        else:
            hstring = f'{int(hrange*1000)} mW'
        self.heaterRangeChoice.setCurrentIndex(self.heater_range_choices.index(hstring))
        self.rampSpeed.setValue(self.ls.read_ramp_speed())
        self.setpointEntry.setValue(self.ls.read_setpoint())
        pid = self.ls.read_PID()
        self.pValue.setValue(pid[0])
        self.iValue.setValue(pid[1])
        self.dValue.setValue(pid[2])

    @pyqtSlot()
    def set_averaging(self):
        t = threading.Thread(target=self.set_averaging_thread, args=())
        t.start()

    def set_averaging_thread(self):
        print('Setting Averaging')
        self.button_handler.deactivate('ave')
        self.bridge.set_ave(float(self.averagingTime.text()))
        self.button_handler.activate('ave')

    @pyqtSlot()
    def update_averaging(self):
        self.averagingTime.setValue(self.bridge.read_ave())

    @pyqtSlot()
    def set_heater_range(self):
        t = threading.Thread(target=self.set_heater_range_thread, args=())
        t.start()

    def set_heater_range_thread(self):
        print('Setting heater')
        self.button_handler.deactivate('heater')
        hstring = self.heaterRangeChoice.currentText()
        if hstring == 'Off':
            hrange = 0.
        elif 'mW' in hstring:
            hrange = float(hstring.strip('mW')) / 1000.
        else:
            hrange = float(hstring.strip('W'))
        self.ls.set_heater_range(hrange)
        print('Set heater')
        self.button_handler.activate('heater')

    @pyqtSlot()
    def update_heater_range(self):
        hrange = self.ls.read_heater_range()
        if hrange > 1:
            hstring = f'{int(hrange)} W'
        elif not hrange:
            hstring = 'Off'
        else:
            hstring = f'{int(hrange * 1000)} mW'
        self.heaterRangeChoice.setCurrentIndex(self.heater_range_choices.index(hstring))

    @pyqtSlot()
    def set_ramp_speed(self):
        t = threading.Thread(target=self.set_ramp_speed_thread, args=())
        t.start()

    def set_ramp_speed_thread(self):
        self.button_handler.deactivate('ramp')
        self.ls.set_ramp_speed(float(self.rampSpeed.text()))
        self.button_handler.activate('ramp')

    @pyqtSlot()
    def update_ramp_speed(self):
        self.rampSpeed.setValue(self.ls.read_ramp_speed())

    @pyqtSlot()
    def set_setpoint(self):
        t = threading.Thread(target=self.set_setpoint_thread, args=())
        t.start()

    def set_setpoint_thread(self):
        self.button_handler.deactivate('setpoint')
        self.ls.set_setpoint(float(self.setpointEntry.text()))
        self.button_handler.activate('setpoint')

    @pyqtSlot()
    def update_setpoint(self):
        self.setpointEntry.setValue(self.ls.read_setpoint())

    @pyqtSlot()
    def set_PID(self):
        t = threading.Thread(target=self.set_PID_thread, args=())
        t.start()

    def set_PID_thread(self):
        self.button_handler.deactivate('pid')
        P = float(self.pValue.text())
        I = float(self.iValue.text())
        D = float(self.dValue.text())
        self.ls.set_PID(P, I, D)
        self.button_handler.activate('pid')

    @pyqtSlot()
    def update_PID(self):
        pid = self.ls.read_PID()
        self.pValue.setValue(pid[0])
        self.iValue.setValue(pid[1])
        self.dValue.setValue(pid[2])

    @pyqtSlot(bool)
    def averaging_button_active(self, activate):
        self.averagingButton.setEnabled(activate)

    @pyqtSlot(bool)
    def heater_button_active(self, activate):
        self.heaterRangeChoice.setEnabled(activate)

    @pyqtSlot(bool)
    def ramp_button_active(self, activate):
        self.rampSetButton.setEnabled(activate)

    @pyqtSlot(bool)
    def setpt_button_active(self, activate):
        self.setpointButton.setEnabled(activate)

    @pyqtSlot(bool)
    def pid_button_active(self, activate):
        self.pidButton.setEnabled(activate)
