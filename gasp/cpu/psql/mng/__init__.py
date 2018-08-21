"""
General Management Data Elements
"""

from gasp.cpu.psql import connection


def create_db(lnk, newdb, overwrite=True):
    """
    Create New PostgreSQL database
    """
    
    def drop(cursor, database):
        cursor.execute(
            "DROP DATABASE {};".format(database)
        )
    
    if "DATABASE" in lnk:
        raise ValueError(
            "For this method, the dict used to connected to "
            "PostgreSQL could not have a DATABASE key"
        )
    
    from gasp.cpu.psql.i import list_db
    
    dbs = list_db(lnk)
    
    con = connection(lnk)
    cs = con.cursor()
    
    if newdb in dbs and overwrite:
        drop(cs, newdb)
    
    cs.execute(
        "CREATE DATABASE {}{};".format(
            newdb,
            " TEMPLATE={}".format(lnk["TEMPLATE"]) \
                if "TEMPLATE" in lnk else ""
        )
    )
    
    cs.close()
    con.close()
    
    return newdb


def create_tbl(conParam, table, fields, orderFields=None):
    """
    Create PGSQL Table
    """
    
    ordenedFields = orderFields if orderFields else fields.keys()
    
    con = connection(conParam)
    
    cursor = con.cursor()
    
    cursor.execute(
        "CREATE TABLE {} ({})".format(
            table,
            ', '.join([
                '{} {}'.format(
                    ordenedFields[x], fields[ordenedFields[x]]
                ) for x in range(len(ordenedFields))
            ])
        )
    )
    
    con.commit()
    
    cursor.close()
    con.close()
    
    return table


def rename_tbl(conParam, table, newName):
    """
    Rename PGSQL Table
    """
    
    con = connection(conParam)
    
    cursor = con.cursor()
    
    cursor.execute(
        "ALTER TABLE {} RENAME TO {}".format(table, newName)
    )
    
    con.commit()
    
    cursor.close()
    con.close()
    
    return newName


def tbls_to_tbl(conParam, lst_tables, outTable):
    """
    Append all tables in lst_tables into the outTable
    """
    
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    sql = " UNION ALL ".join([
        "SELECT * FROM {}".format(t) for t in lst_tables])
    
    outTable = ntbl_by_query(conParam, outTable, sql)
    
    return outTable

