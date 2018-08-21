"""
Know more about a SQlite Database
"""


import sqlite3


def lst_table(sqliteDB):
    """
    List tables in one sqliteDB
    """
    
    conn = sqlite3.connect(sqliteDB)
    cursor = conn.cursor()
    
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )
    
    tables = [n[0] for n in tables]
    cursor.close
    conn.close()
    
    return tables


def count_rows_in_query(db, table, where=None):
    """
    Return Row number in Query
    """
    
    from gasp.fm.sqLite import sqlq_to_df
    
    d = sqlq_to_df(db, "SELECT COUNT(*) AS nrows FROM {}{}".format(
        table,
        "" if not where else " WHERE {}".format(where)
    ))
    
    return int(d.iloc[0].nrows)

