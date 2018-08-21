"""
Data to SQLITE Database
"""

import sqlite3

def insert_query(db, table, cols, new_values, execute_many=None):
    """
    Method to insert data into SQLITE Database
    """
    
    from gasp import goToList
    
    cols = goToList(cols)
    
    if not cols:
        raise ValueError('cols value is not valid')
    
    conn = sqlite3.connect(db)
    cs = conn.cursor()
    
    if not execute_many:
        cs.execute(
            "INSERT INTO {} ({}) VALUES {}".join(
                table, ', '.join(cols),
                ', '.join(
                    ['({})'.format(', '.join(row)) for row in new_values]
                )
            )
        )
    
    else:
        cs.executemany(
            '''INSERT INTO {} ({}) VALUES ({})'''.format(
                table, ', '.join(cols),
                ', '.join(['?' for i in range(len(cols))])
            ),
            new_values
        )
    
    conn.commit()
    cs.close()
    conn.close()


def txt_to_sqlite(csv, database, table, delimiter, encoding_='utf-8'):
    """
    Method to insert tables writen in a text file into SQLITE
    """
    
    import codecs
    
    def sanitize_value(v):
        return None if not v or v == 'None' else v
    
    
    with codecs.open(csv, 'r', encoding=encoding_) as f:
        c = 0
        data = []
        for l in f:
            cols = l.replace('\r', '').strip('\n').split(delimiter)
            if not c:
                cols_name = ['`%s`' % cl.strip('"') for cl in cols]
                c+=1
            else:
                data.append(tuple([sanitize_value(v) for v in cols]))
    
    conn = sqlite3.connect(database)
    cs = conn.cursor()
    cs.executemany(
        '''INSERT INTO {tbl} ({col}) VALUES ({i})'''.format(
            tbl=table, col=', '.join(cols_name),
            i=', '.join(['?' for i in range(len(cols_name))])
            ),
        data
    )
    conn.commit()
    cs.close()
    conn.close()


def txts_to_sqlite(folder, sqlite_db, delimiter, __encoding='utf-8'):
    """
    Executes text_to_sqlite for every txt file in a given folder
    
    The file name should be the table name
    """
    
    import os
    
    from gasp.oss import list_files
    
    txt_tables = list_files(folder, file_format=['.txt', '.csv', '.tsv'])
    
    for table in txt_tables:
        txt_to_sqlite(
            table, sqlite_db,
            os.path.splitext(os.path.basename(table))[0],
            delimiter, encoding_=__encoding
        )


def xls_to_sqlite(xls, sqDb, sqtable=None, excelSheet=None):
    """
    Insert data in XLS file into a SQLITE Database
    """
    
    import os
    import pandas
    
    from gasp.fm.xls    import xls_to_df
    from gasp.to.sqLite import insert_query
    from gasp.sqLite.i  import lst_table
    
    sqtable = sqtable if sqtable else os.path.splitext(os.path.basename(xls))[0]
    # Excel to pandas dataframe
    data = xls_to_df(xls, sheet=excelSheet)
    
    # Check if sqtable is in sqDb
    tables = lst_table(sqDb)
    if sqtable not in tables:
        from gasp.sqLite.mng     import new_table
        from gasp.sqLite.mng.fld import sqtypes_from_df
        
        new_table(sqDb, sqtable, sqtypes_from_pandasdf(data))
    
    # Send data to SQLITE
    insert_query(
        sqDb, sqtable, list(data.columns.values),
        data.values.tolist(), execute_many=True
    )


def df_to_sqlite(dataframe, database, outtable):
    """
    Dataframe to SQLite Database
    """
    
    from gasp.sqLite import alchemy_eng
    
    eng = alchemy_eng(database)
    
    dataframe.to_sql(outtable, eng, if_exists="replace",
                     index=False)
    
    return outtable

