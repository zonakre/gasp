"""
Copy data
"""

def copy_fromdb_todb(conFromDb, conToDb, tables, qForTbl=None):
    """
    Send PGSQL Tables from one database to other
    """
    
    import pandas
    
    from gasp                  import goToList
    from gasp.fm.psql          import query_to_df
    from gasp.cpu.psql         import alchemy_engine
    from gasp.cpu.psql.mng.fld import cols_name
    from gasp.to.psql          import df_to_pgsql
    
    psEngine = alchemy_engine(conToDb)
    
    tables = goToList(tables)
    
    for table in tables:
        cols = cols_name(conFromDb, table)
        
        if not qForTbl:
            tblDf = query_to_df(conFromDb, "SELECT {} FROM {}".format(
                ", ".join(cols), table)
            )
        
        else:
            if table not in qForTbl:
                tblDf = query_to_df(conFromDb, "SELECT {} FROM {}".format(
                    ", ".join(cols), table
                ))
            
            else:
                tblDf = query_to_df(conFromDb, qForTbl[table])
        
        df_to_pgsql(conToDb, tblDf, table)


def copy_fromdb_todb2(conFrom, conTo, tables):
    """
    Send PGSQL Tables from one database to another using
    pg_dump and pg_restore
    """
    
    import os
    from gasp                   import goToList
    from gasp.oss.ops           import create_folder, del_folder
    from gasp.cpu.psql.mng.bkup import dump_table
    from gasp.cpu.psql.mng.bkup import restore_table
    
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

