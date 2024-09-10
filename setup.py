import sys
import subprocess

packages_to_install = ['matplotlib',
                       'numba',
                       'numpy',
                       'pyqtgraph',
                       'pyserial',
                       'pyside6',
                       'pyvisa',
                       'pyyaml',
                       'scipy']

if __name__ == "__main__":
    if sys.argv[1] == "pip":
        for package_name in packages_to_install:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', package_name])