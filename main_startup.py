import os
from PySide6.QtWidgets import QApplication, QDialog
import get
import sys
import time
from gui.dialogs.new_file import NewFileDialog


def launch_process(command, leave_open=True):
    """
    Opens a new cmd prompt window and executes a command.
    :param command: command to execute.
    :param leave_open: do you want to leave the cmd prompt open when finished?
    """
    if leave_open:
        open_key = "k"
    else:
        open_key = "c"
    os.system("start cmd /{} {}".format(open_key, command))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    path = os.path.join(get.base_path(), 'Dielectric_data')

    """LAUNCH DIALOG"""
    dialog = NewFileDialog(path)
    dialog.exec()
    if dialog.result() == QDialog.Accepted:
        print("accepted dialog")
        bridge = dialog.bridge_choice
        ls_num = dialog.ls_choice
        cid = dialog.chip_id.replace(" ", "-")
        sample = dialog.sample.replace(" ", "-")
        purpose = dialog.purp_choice
        # cal_file = dialog.calibration_path
        # print("get some dialog settings")

        creation_datetime = dialog.date

        """LAUNCH SERVER"""
        launch_process("py server.py {} {}".format(bridge, ls_num), leave_open=True)
        print("Launched server")

        print("Launched data taking process {m:02}/{d:02}/{y:04} at {h:02}:{min:02}:{s}".format(
            m=creation_datetime.month,
            d=creation_datetime.day,
            y=creation_datetime.year,
            h=creation_datetime.hour,
            min=creation_datetime.minute,
            s=creation_datetime.second))

        """CREATE FILENAME"""
        day = f"{creation_datetime.day:02}"
        year = f"{creation_datetime.year:04}"
        month = f"{creation_datetime.month:02}"
        start_time = f"{dialog.date.hour:02}-{dialog.date.minute:02}"
        if not sample:
            sample = "Bare"
        if not cid:
            cid = "test"
        filename = f"{year}-{month}-{day}__{sample}__{cid}__{purpose}__T-{start_time}.csv"
        print(f"Creating file: {filename}")

        """CREATE COMMENT LINE"""
        full_comment = str(dialog.presets)

        """CREATE DATA FILE"""
        launch_process('py data_taker.py "{path}" "{fname}" "{f}" "{v}" "{ave}" "{dc}" "{b}" "{ls}" "{c}" "{p}"'.format(
            path=path,
            fname=filename,
            f=str(dialog.frequencies).strip("[").strip("]"),
            v=dialog.voltage,
            ave=dialog.averaging,
            dc=dialog.dc_bias_setting,
            b=bridge,
            ls=ls_num,
            c=full_comment,
            p=purpose
        ), leave_open=True)

        time.sleep(5)
        launch_process("py temperature_controller.py", leave_open=True)
        print("Launched server")
    else:
        print("Canceled")
    # input("Press Enter to close")


