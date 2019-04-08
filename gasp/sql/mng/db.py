"""
Database Information and Management
"""

from gasp.sql.c import psqlcon


"""
Databases Info
"""

def list_db(conParam):
    """
    List all PostgreSQL databases
    """
    
    con = psqlcon(conParam)
    
    cursor = con.cursor()
    
    cursor.execute("SELECT datname FROM pg_database")
    
    return [d[0] for d in cursor.fetchall()]


def db_exists(lnk, db):
    """
    Database exists
    """
    con = psqlcon(lnk)
        
    cursor = con.cursor()
    
    cursor.execute("SELECT datname FROM pg_database")
    
    dbs = [d[0] for d in cursor.fetchall()]
    
    return 1 if db in dbs else 0


"""
Create Databases
"""

def create_db(lnk, newdb, overwrite=True, api='psql'):
    """
    Create Relational Database
    
    APIS Available:
    * psql;
    * sqlite;
    """
    
    if api == 'psql':
        def drop(cursor, database):
            cursor.execute(
                "DROP DATABASE {};".format(database)
            )
    
        if "DATABASE" in lnk:
            raise ValueError(
                "For this method, the dict used to connected to "
                "PostgreSQL could not have a DATABASE key"
            )
    
        dbs = list_db(lnk)
    
        con = psqlcon(lnk)
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
    
    elif api == 'sqlite':
        import os
        import sqlite3
        
        try:
            DB = os.path.join(lnk, newdb)
            if os.path.exists(DB) and overwrite:
                from gasp.oss.ops import del_file
                del_file(os.path.join(DB))
            
            conn = sqlite3.connect(DB)
        except Error as e:
            print e
        finally:
            conn.close()
    
    else:
        raise ValueError('API {} is not available'.format(api))
    
    return newdb


"""
Delete Databases
"""

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
    
    databases = list_db(lnk)
    
    if database not in databases: return 0
    
    con = psqlcon(lnk)
    cursor = con.cursor()
    
    cursor.execute("DROP DATABASE {};".format(database))
        
    cursor.close()
    con.close()

"""
Dump Databases
"""

def dump_db(conPSQL, outSQL):
    """
    DB to SQL Script
    """
    
    from gasp import exec_cmd
    
    outcmd = exec_cmd("pg_dump -U {} -h {} -p {} -w {} > {}".format(
        conPSQL["USER"], conPSQL["HOST"], conPSQL["PORT"],
        conPSQL["DATABASE"], outSQL      
    ))
    
    return outSQL


"""
Copy data from one Database to another
"""

def copy_fromdb_todb(conFromDb, conToDb, tables, qForTbl=None):
    """
    Send PGSQL Tables from one database to other
    """
    
    import pandas
    from gasp             import goToList
    from gasp.fm.sql      import query_to_df
    from gasp.sql.mng.fld import cols_name
    from gasp.to.sql      import df_to_db
    
    tables = goToList(tables)
    
    for table in tables:
        cols = cols_name(conFromDb, table)
        
        if not qForTbl:
            tblDf = query_to_df(conFromDb, "SELECT {} FROM {}".format(
                ", ".join(cols), table), db_api='psql'
            )
        
        else:
            if table not in qForTbl:
                tblDf = query_to_df(conFromDb, "SELECT {} FROM {}".format(
                    ", ".join(cols), table
                ), db_api='psql')
            
            else:
                tblDf = query_to_df(conFromDb, qForTbl[table], db_api='psql')
        
        df_to_db(conToDb, tblDf, table, api='psql')


def copy_fromdb_todb2(conFrom, conTo, tables):
    """
    Send PGSQL Tables from one database to another using
    pg_dump and pg_restore
    """
    
    import os
    from gasp             import goToList
    from gasp.oss.ops     import create_folder, del_folder
    from gasp.sql.mng.tbl import dump_table
    from gasp.sql.mng.tbl import restore_table
    
    tmpFolder = create_folder(
        os.path.dirname(os.path.abspath(__file__)), randName=True
    )
    
    tables = goToList(tables)
    
    for table in tables:
        # Dump
        sqlScript = dump_table(
            conFrom, table,
            os.path.join(tmpFolder, table + ".sql")
        )
        
        # Restore
        tblname = restore_table(conTo, sqlScript, table)
    
    del_folder(tmpFolder)

