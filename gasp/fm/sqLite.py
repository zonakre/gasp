"""
Get Data from SQLITE DATABASE
"""

import sqlite3

def data_by_query(db, sql):
    """
    Retrive data from SQLITE DB using query
    """
    
    conn = sqlite3.connect(db)
    csr = conn.cursor()
    csr.execute(sql)
    data = csr.fetchall()
    csr.close()
    conn.close()
    
    return data


def sqlq_to_df(db, sql):
    """
    Sqlite data to Pandas
    """
    
    import pandas
    from gasp.sqLite import alchemy_eng
    
    engine = alchemy_eng(db)
    
    df = pandas.read_sql(sql, engine, columns=None)
    
    return df

