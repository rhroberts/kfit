'''
    Various tools to help with data processing,
    fitting, and visualization
'''

import pandas as pd


def to_df(file_path, sep=',', header='infer', index_col=None, skiprows=None, dtype=None, encoding=None): 
    '''
        Convert .csv file to dataframe using a few select
        pandas.read_csv() parameters
    '''
    df = pd.read_csv(
        file_path, sep=sep, header=header,
        index_col=index_col, skiprows=skiprows, 
        dtype=dtype, encoding=encoding
    )

    return df