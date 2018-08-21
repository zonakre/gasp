"""
SQLITE DB Fields
"""


def pandas_map_sqtypes(type_):
    __types = {
        'int32'   : 'integer',
        'int64'   : 'integer',
        'float32' : 'numeric',
        'float64' : 'numeric',
        'object'  : 'text'
    }
    
    return __types[type_]


def sqtypes_from_df(df):
    """
    Get PGTypes from pandas dataframe
    """
    
    dataTypes = dict(df.dtypes)
    
    return {col : pandas_map_sqtypes(type_)(
        str(dataTypes[col])) for col in dataTypes}


def get_fields_name(db, table):
    """
    List all columns in a SQLITE table
    """
    
    import sqlite3
    
    con = sqlite3.connect(db)
    cursor = con.execute("SELECT * FROM {}".format(
        table
    ))
    
    names = list(map(lambda x: x[0], cursor.description))
    
    return names

