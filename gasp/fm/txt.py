"""
Text files to Something
"""

import pandas

def txt_to_df(csvFile, _delimiter, encoding_='utf8'):
    """
    Text file to Pandas Dataframe
    """
    
    return pandas.read_csv(
        csvFile, sep=_delimiter, low_memory=False,
        encoding=encoding_
    )

