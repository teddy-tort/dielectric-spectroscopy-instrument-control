"""
A tab widget for plotting data in app.py

@author: Teddy Tortorici
"""
import sys
import os
import time
import threading
import pyqtgraph as pg
import numpy as np
from PySide6.QtWidgets import (QWidget, QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout,
                               QToolButton, QMessageBox, QApplication, QFileDialog)
from PySide6.QtGui import QAction
from PySide6.QtCore import Slot, Qt
import shutil
import get
from gui.dialogs.help import HelpPrompt
import gui.icons as icon
from gui.plotting import Plot, RightAxisPlot
from gui.signalers import Signaler
from files.csv import CSVFile
from files.data import DielectricSpec
from communication.socket_client import shutdown_command


class PlotWindow(QMainWindow):

    width = 1200
    height = 650

    def __init__(self, sys_argv):
        self.purpose = sys_argv[-1]     # "CAL", "POW", "FILM", "OTHER", "TEST"
        QMainWindow.__init__(self)
        self.plot_widget = PlotWidget(sys_argv)

        self.force_quit = True

        try:
            with open(os.path.join("gui", "stylesheets", "main.css"), "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            with open(os.path.join("stylesheets", "main.css"), "r") as f:
                self.setStyleSheet(f.read())

        """WINDOW PROPERTIES"""
        self.setWindowTitle("Data Acquisition App")
        self.resize(PlotWindow.width, PlotWindow.height)
        self.setWindowIcon(icon.custom('app.png'))

        self.setCentralWidget(self.plot_widget)

        """MENU BAR"""
        main_menu = self.menuBar()

        # File, Data, and Help drop down menus
        file_menu = main_menu.addMenu('&File')
        data_menu = main_menu.addMenu('&Data')
        help_menu = main_menu.addMenu('&Help')

        self.help = HelpPrompt()

        """MENU ACTIONS"""
        # File menu actions
        self.exit_action = QAction(icon.built_in(self, 'BrowserStop'), 'E&xit', self)
        self.exit_action.setShortcut('CTRL+Q')
        self.exit_action.triggered.connect(self.quit)
        # Data menu actions
        self.play_action = QAction(icon.custom("play.png"), 'Take &Data', self)
        self.play_action.setShortcut('CTRL+SPACE')
        self.play_action.triggered.connect(self.continue_data)
        self.pause_action = QAction(icon.custom("pause.png"), 'Pause &Data', self)
        self.pause_action.setShortcut('CTRL+SPACE')
        self.pause_action.triggered.connect(self.pause_data)
        # Help menu actions
        self.about_action = QAction(icon.built_in(self, 'MessageBoxQuestion'), '&About', self)
        self.about_action.setShortcut('CTRL+/')
        self.about_action.triggered.connect(self.get_help)

        self.play_action.setEnabled(False)
        self.pause_action.setEnabled(True)

        file_actions = [self.exit_action]
        data_actions = [self.play_action, self.pause_action]
        help_actions = [self.about_action]

        """ADD ACTIONS to MENUS"""
        for action in file_actions:
            file_menu.addAction(action)
        for action in data_actions:
            data_menu.addAction(action)
        for action in help_actions:
            help_menu.addAction(action)

        self.start()

    def start(self):
        self.plot_widget.data_taking_thread.start()

    def pause_data(self):
        self.plot_widget.running = False
        self.play_action.setEnabled(True)
        self.pause_action.setEnabled(False)

    def continue_data(self):
        self.plot_widget.running = True
        self.play_action.setEnabled(False)
        self.pause_action.setEnabled(True)

    @Slot()
    def quit(self):
        """Exit program"""
        exit_question = QMessageBox.critical(self, 'Exiting', 'Are you sure you would like to quit?',
                                             QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)
        if exit_question == QMessageBox.Yes:
            self.force_quit = False
            print('Exiting')
            shutdown_command("localhost", get.port())

            file = os.path.join(self.plot_widget.base_path, self.plot_widget.filename)
            save_loc = os.path.join(get.onedrive(), "Teddy")

            if self.purpose == "CAL":
                save_loc = os.path.join(save_loc, "Capacitors" , "Mounts")
            elif self.purpose == "POW":
                save_loc = os.path.join(save_loc, "Powders")
            elif self.purpose == "FILM":
                save_loc = os.path.join(save_loc, "Capacitors", "TPP Films")

            file_save, filetype = QFileDialog.getSaveFileName(self, caption="Save Data to OneDrive",
                                                              dir=save_loc, filter="CSV (*.csv)")
            shutil.copyfile(file, file_save)
            self.close()

    @Slot()
    def closeEvent(self, event):
        """Overrides closeEvent so that there is no force quit"""
        if self.force_quit:
            event.ignore()
            self.quit()
        else:
            event.accept()

    @Slot()
    def get_help(self):
        """Opens HELP Prompt"""
        self.help.exec()


class PlotWidget(QWidget):
    labels = ['time', 'temperature a', 'temperature b', 'capacitance', 'loss', 'voltage', 'frequency']
    colors = {"temperature": ((85, 179, 255),       # light blue
                              (75, 245, 215)),      # teal
              "capacitance": ((255, 125, 150),      # light red
                              (255, 255, 255),      # white
                              (180, 165, 255),      # lighter blue
                              (220, 220, 220),      # light grey
                              (180, 255, 180),      # light green
                              (253, 254, 150),      # yellow
                              (255, 163, 102)),     # orange
              "loss": ((255, 105, 183),             # magenta
                       (210, 210, 210),             # light grey
                       (205, 145, 255),             # light purple
                       (255, 255, 255),             # white
                       (204, 255, 137),             # lime
                       (249, 218, 122),             # yellow-orange
                       (255, 131, 102))}            # red-orange
    pen_width = 2
    # colors = [(0, 0, 255), (255, 0, 0), (0, 0, 0)]
    # pens = dict(zip(data_columns[1:], [pg.mkPen(color, width=2) for color in colors]))
    plot_colors = {"background": (42, 42, 38),      # dark mode
                   "foreground": (255, 255, 255)}   # white

    def __init__(self, sys_argv, link_x: bool = True, link_y: bool = False):
        """
        Tab for plotting
        :param link_x: Do you want it to lock x axes of the same type together?
        :param link_y: Do you want it to lock y axes of the same type together?
        """
        QWidget.__init__(self)

        """SET UP THREADING"""
        self.data_taking_thread = threading.Thread(target=self.take_data, args=())
        self.data_taking_thread.daemon = True
        self.running = False
        # self.started = False

        """SET UP SIGNALERS"""
        # self.plot_updater = MessageSignaler()
        self.plot_updater = Signaler()
        self.plot_updater.signal.connect(self.update_plots)
        # self.plot_initializer = MessageSignaler()
        # self.plot_initializer.signal.connect(self.parent.initialize)

        """SET UP DATA FILE"""
        self.data = None
        self.file = None
        self.base_path = sys_argv[1]
        self.filename = sys_argv[2]
        self.frequencies = [int(f) for f in sys_argv[3].split(",")[::-1]]
        self.voltage = float(sys_argv[4])
        self.averaging = int(sys_argv[5])
        self.dc_bias_setting = sys_argv[6]
        self.bridge = sys_argv[7]
        self.ls_num = int(sys_argv[8])
        self.create_file(sys_argv[9])

        """PLOT COLORS"""
        for key in PlotWidget.plot_colors.keys():
            pg.setConfigOption(key, PlotWidget.plot_colors[key])
        pg.setConfigOptions(antialias=True)

        self.data_line_skip = 0
        self.live_plotting = True

        self.freq_labels = None

        """CREATE LAYOUT"""
        main_layout = QHBoxLayout(self)
        plot_layout = QGridLayout()
        button_layout = QVBoxLayout()

        """CREATE PLOTS"""
        self.plot_CvT = Plot('Temperature (K)', 'Capacitance (pF)')
        self.plot_LvT = Plot('Temperature (K)', 'Loss Tangent')
        self.plot_Tvt = Plot('Time', 'Temperature (K)', date_axis_item=True)
        self.plot_Lvt = RightAxisPlot('Loss Tangent')
        self.plot_Cvt = Plot('Time', 'Capacitance (pF)', right_axis=self.plot_Lvt, date_axis_item=True, legend=False)

        # Will place in the gid to mimic the list of lists
        plots = [[self.plot_CvT, self.plot_Tvt],
                 [self.plot_LvT, self.plot_Cvt]]

        """Link X and Y axes (if specified)"""
        if link_x or link_y:
            plot_list = [plot for plot_row in plots for plot in plot_row]       # flattens list of lists into a list
            for ii, plot_ii in enumerate(plot_list):
                for jj, plot_jj in enumerate(plot_list):
                    if ii < jj:
                        if link_x:
                            if plot_ii.x_label.lower() == plot_jj.x_label.lower():
                                plot_ii.setXLink(plot_jj)
                        if link_y:
                            if plot_ii.y_label.lower() == plot_jj.y_label.lower():
                                plot_ii.setYLink(plot_jj)

        """Place Plots in the grid layout"""
        for ii, plot_row in enumerate(plots):
            for jj, plot in enumerate(plot_row):
                plot_layout.addWidget(plot, ii, jj)

        """Place buttons in vertical layout"""
        self.button_update = QToolButton()
        self.button_update.setIcon(icon.built_in(self, 'BrowserReload'))
        self.button_update.setToolTip('Update Plots')
        self.button_update.clicked.connect(self.update_plots)

        self.button_play_pause = QToolButton()
        self.button_play_pause.clicked.connect(self.swap_live)
        self.set_live_plotting(True)

        buttons = [self.button_play_pause, self.button_update]
        for button in buttons:
            button_layout.addWidget(button)
        button_layout.addStretch(0)

        """Place layouts in main layout"""
        main_layout.addLayout(plot_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.initialize_plots()

    def create_file(self, comment):
        self.file = DielectricSpec(path=self.base_path,
                                   filename=self.filename,
                                   frequencies=self.frequencies,
                                   bridge=self.bridge,
                                   ls_model=self.ls_num,
                                   comment=comment)
        self.file.initiate_devices(voltage_rms=self.voltage,
                                   averaging_setting=self.averaging,
                                   dc_setting=self.dc_bias_setting)

    def initialize_plots(self):
        self.freq_labels = [str(freq) for freq in self.frequencies]
        freq_num = len(self.freq_labels)
        labels = CSVFile.get_labels(os.path.join(self.base_path, self.filename))

        """CREATE CURVES"""
        width = self.__class__.pen_width

        colors = self.__class__.colors["capacitance"][:freq_num]
        pens = [pg.mkPen(color, width=width) for color in colors]
        self.plot_CvT.set_curves(self.freq_labels, pens)
        self.plot_Cvt.set_curves([f"C: {f}" for f in self.freq_labels], pens)

        colors = self.__class__.colors["loss"][:freq_num]
        pens = [pg.mkPen(color, width=width, style=Qt.DashLine) for color in colors]
        self.plot_LvT.set_curves(self.freq_labels, pens)
        self.plot_Lvt.set_curves([f"L: {f}" for f in self.freq_labels], pens)

        colors = self.__class__.colors["temperature"][:freq_num]
        self.plot_Tvt.set_curves(["A", "B"], [pg.mkPen(color, width=width) for color in colors])

        """FIND INDEXES IN DATA"""
        time_indices = [ii for ii, ll in enumerate(labels) if 'time' in ll.lower()]
        temp_a_indices = [ii for ii, ll in enumerate(labels) if 'temperature a' in ll.lower()]
        temp_b_indices = [ii for ii, ll in enumerate(labels) if 'temperature b' in ll.lower()]
        cap_indices = [ii for ii, ll in enumerate(labels) if 'capacitance' in ll.lower()]
        loss_indices = [ii for ii, ll in enumerate(labels) if 'loss' in ll.lower()]

        self.plot_CvT.set_indices(temp_a_indices, cap_indices)
        self.plot_LvT.set_indices(temp_a_indices, loss_indices)
        self.plot_Tvt.set_indices(time_indices, zip(temp_a_indices, temp_b_indices))
        self.plot_Cvt.set_indices(time_indices, cap_indices)
        self.plot_Lvt.set_indices(time_indices, loss_indices)

        self.plot_Cvt.update_views()
        self.plot_Tvt.setXRange(time.time(), time.time() + 360, padding=0)

    def take_data(self):
        """This should be run in a thread"""
        self.running = True

        # self.data = self.file.sweep_frequencies()
        # self.file.write_row(self.data)

        """INITIATE DEVICES WITH DIALOG SETTINGS"""
        while self.running:
            data_point = self.file.sweep_frequencies()
            # self.file.write_row(data_point)

            # self.data = np.vstack((self.data, data_point))
            if self.live_plotting:
                # self.plot_updater.signal.emit(str(data_point).strip('[').strip(']'))
                self.plot_updater.signal.emit()

    def set_live_plotting(self, on):
        """Turn live plotting on or off"""
        self.live_plotting = on
        self.button_update.setEnabled(not on)
        if on:
            self.button_play_pause.setIcon(icon.built_in(self, 'DialogYesButton'))
            self.button_play_pause.setToolTip('Live Plotting')
        else:
            self.button_play_pause.setIcon(icon.built_in(self, 'DialogNoButton'))
            self.button_play_pause.setToolTip('Click to turn on Live Plotting')

    @Slot()
    def swap_live(self):
        """Switch the live plotting setting"""
        self.set_live_plotting(not self.live_plotting)

    @Slot()
    def update_plots(self):
        """Draw curves to update the plots to any changes in the data file"""
        # data = data_str.split(', ')
        # data = [float(element.strip("'")) for element in data]
        data = self.load_data()
        # print(self.data)

        self.plot_CvT.update_plot(data)
        self.plot_LvT.update_plot(data)
        self.plot_Tvt.update_plot(data)
        self.plot_Cvt.update_plot(data)
        self.plot_Lvt.update_plot(data)

    def load_data(self) -> np.ndarray:
        """Loads data from filename. Will make attempts to load data and if it fails, it will add to the amount of lines
        needed to skip. After the first attempt to load data, it should succeed on the first attempt every time"""
        data, self.data_line_skip = CSVFile.load_data_np(
            os.path.join(self.base_path, self.filename), self.data_line_skip
        )
        return data


if __name__ == "__main__":
    print("Launching plot")
    app = QApplication(sys.argv)

    main_window = PlotWindow(sys.argv)
    main_window.show()

    sys.exit(app.exec())
