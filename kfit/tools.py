'''
    Various tools to help with data processing,
    fitting, and visualization
'''

import tkinter as tk
from tkinter import filedialog
import pandas as pd


def get_data_source():
    '''
        Gets data from a csv file, return pandas dataframe 
    '''
    # prompt user for data file to fit
    root = tk.Tk()  # give the tk instance a name
    # prompt user to select file
    file_path = filedialog.askopenfilename()
    # make the tk window go away after file selection
    root.withdraw()
    return file_path

def to_csv(file_path, sep=',', header=None, index_col=None, dtype=None, skiprows=None, encoding=None): 
    '''
        []
    '''
    df = pd.read_csv(
        file_path, sep, header, index_col,
        dtype, skiprows, encoding
    )

    return df
