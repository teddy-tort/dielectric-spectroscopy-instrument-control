import sys
import subprocess

packages_to_install = ['pip',
                       'matplotlib',
                       'numba',
                       'numpy',
                       'pyqtgraph',
                       'pyserial',
                       'pyside6',
                       'pyvisa',
                       'pyyaml',
                       'scipy']

if __name__ == "__main__":
    for package_name in packages_to_install:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', package_name])