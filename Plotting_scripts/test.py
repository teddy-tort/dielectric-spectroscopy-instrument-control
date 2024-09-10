import tkinter as Tkinter
from tkinter import filedialog
import os
import sys
sys.path.append('..')
import get

root = Tkinter.Tk()
root.title('File Selector')

filename = filedialog.askopenfilenames(initialdir=os.path.join(get.google_drive(), 'Dielectric_data', 'Teddy-2'),
                                       title='Select a data file to plot',
                                       filetypes=(('CSV files', '*.csv',), ('all files', '*.*')))

#files = root.filename
print(filename)

