"""
Methods to delete tables
"""

from gasp.cpu.psql import connection


def drop_db(lnk, database):
    """
    Delete PostgreSQL database
    
    Return 0 if the database does not exist
    """
    
    if "DATABASE" in lnk:
        raise ValueError(
            "For this method, the dict used to connected to "
            "PostgreSQL could not have a DATABASE key"
        )
    
    from gasp.i import list_db
    
    databases = list_db(lnk)
    
    if database not in databases: return 0
    
    con = connection(lnk)
    cursor = con.cursor()
    
    cursor.execute("DROP DATABASE {};".format(database))
        
    cursor.close()
    con.close()


def del_tables(lnk, pg_table_s, isViews=None):
    """
    Delete all tables in pg_table_s
    """
    
    from gasp import goToList
    
    pg_table_s = goToList(pg_table_s)
        
    con = connection(lnk)
    
    l = []
    for i in range(0, len(pg_table_s), 100):
        l.append(pg_table_s[i:i+100])
    
    for lt in l:
        cursor = con.cursor()
        cursor.execute('DROP {} {};'.format(
            'TABLE' if not isViews else 'VIEW', ', '.join(lt)))
        con.commit()
        cursor.close()
    
    con.close()


def del_tables_wbasename(conParam, table_basename):
    """
    Delete all tables with a certain general name
    """
    
    from gasp.cpu.psql.i import lst_tbl_basename
    
    pgTables = lst_tbl_basename(table_basename, conParam)
    
    del_tables(conParam, pgTables)


def drop_table_data(dic_con, table, where=None):
    """
    Delete all data on a PGSQL Table
    """
    
    con = connection(dic_con)
    
    cursor = con.cursor()    
    
    cursor.execute("DELETE FROM {}{};".format(
        table, "" if not where else " WHERE {}".format(where)
    ))
    
    con.commit()
    cursor.close()
    con.close()


def drop_where_cols_are_same(conParam, table, colA, colB):
    """
    Delete rows Where colA has the same value than colB
    """
    
    con = connection(conParam)
    
    cursor = con.cursor()
    
    cursor.execute('DELETE FROM {} WHERE {}={}'.format(table, colA, colB))
    
    con.commit()
    cursor.close()
    con.close()

