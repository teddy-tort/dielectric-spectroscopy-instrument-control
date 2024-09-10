import sys
import os
from PySide6.QtWidgets import (QFileDialog, QGroupBox, QFormLayout, QDialogButtonBox,QDialog, QVBoxLayout, QPushButton,
                               QLabel)
from PySide6.QtCore import Slot


class FileButton(QPushButton):
    def __init__(self, base_path: str, title: str = "", label: str = "",
                 whats_this: str = None, filetypes: str = "CSV (*.csv)", default_value: str = None):
        """
        Create a button for opening a file
        :param base_path: base path for file dialog
        :param title: Default text of button (and title of dialog window)
        :param label: text to the side
        :param whats_this: description
        :param filetypes: types of files to filter separated by ';;'
        """
        super(self.__class__, self).__init__()
        self.base_path = base_path
        self.title = title
        self.setText(title)
        self.label = QLabel(label + ":")
        if whats_this:
            self.label.setWhatsThis(whats_this)
        self.filetypes = filetypes

        self.filename = None

        self.clicked.connect(self.open_file)

        if default_value is not None:
            self.set(default_value)

    @Slot()
    def open_file(self):
        """
        Open file dialog and replace button text with the filename
        """
        self.filename, filetype = QFileDialog.getSaveFileName(self, caption=self.title,
                                                              dir=os.path.join(get.onedrive(), "Teddy"),
                                                              filter="CSV (*.csv)")
        # filename_display = self.filename.lstrip(self.base_path)
        print(self.filename)
        print(a)

    def get(self) -> str:
        """
        Get the filepath
        :return: Will return the filepath given from the button
        """
        if self.filename:
            return self.filename
        elif self.text() == self.title or not self.text():
            return ""
        else:
            return os.path.join(self.base_path, self.text())

    def set(self, text: str):
        if text:
            self.setText(text)
        else:
            self.setText(self.title)


class NewFileDialog(QDialog):
    def __init__(self, base_path):
        """
        Create a form dialog box that you can fill out to prompt the code with the details of a new dataset
        :param base_path: base path to data
        """
        super(self.__class__, self).__init__()
        self.base_path = base_path
        self.date = None        # will fill once Okay is hit
        self.setWindowTitle("Measurement Details")
        with open(os.path.join("gui", "stylesheets", "main.css"), "r") as f:
            self.setStyleSheet(f.read())

        # FOR FILMS
        self.button = FileButton(base_path=os.path.join(base_path, "1-Calibrations"),
                                 title="Locate Calibration File",
                                 label="Path to Calibration File",
                                 whats_this="This is used for film measurements to remove the background and"
                                            "reveal the dielectric constant")
                                 # default_value=self.calibration_path)


        boxes = [self.button]

        """GENERATE FORM"""
        self.form = QGroupBox("Enter measurement details for the dataset")

        form_layout = QFormLayout()

        for box in boxes:
            form_layout.addRow(box.label, box)
        self.form.setLayout(form_layout)

        """PLACE BUTTONS IN THE BOX"""
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_click)
        button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.form)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

    def accept_click(self):
        pass


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import get

    app = QApplication(sys.argv)
    dialog = NewFileDialog(get.onedrive())
    sys.exit(dialog.exec())