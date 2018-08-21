"""
Data to xls
"""

def df_to_xls(dfs, out_xls, sheetsName=None, sanitizeUtf8=True):
    """
    Pandas DataFrame to Excel table
    """
    
    import pandas; import os
    from gasp      import goToList
    from gasp.oss  import get_filename
    
    def sanitizeP(row, cols):
        for c in cols:
            try:
                _c = int(row[c])
            except:
                try:
                    row[c] = unicode(str(row[c]), 'utf-8')
                except:
                    pass
        
        return row
    
    dfs = [dfs] if type(dfs) != list else dfs
    sheetsName = goToList(sheetsName)
    
    if sanitizeUtf8:
        for i in range(len(dfs)):
            COLS = list(dfs[i].columns.values)
            dt = dfs[i].apply(
                lambda x: sanitizeP(x, COLS), axis=1
            )
        
            dfs[i] = dt
    
    writer = pandas.ExcelWriter(out_xls, engine='xlsxwriter')
    
    for i in range(len(dfs)):
        dfs[i].to_excel(
            writer, 
            sheet_name="{}_{}".format(
                get_filename(out_xls), str(i)
            ) if not sheetsName else sheetsName[i]
        )
    
    writer.save()
    
    return out_xls


def psql_to_xls(pg_queries, out_xls, sheetsNames,
                dicParam, overwrite=None):
    """
    Export data from PostgreSQL to a XLS File using Pandas
    """
    
    import os
    from gasp         import goToList
    from gasp.fm.psql import query_to_df
    
    if overwrite:
        if os.path.exists(out_xls):
            os.remove(out_xls)
    
    else:
        if os.path.exists(out_xls):
            raise ValueError("{} already exists".format(out_xls))
    
    PG_QUERY    = goToList(pg_queries)
    sheetsnames = goToList(sheetsNames)
    
    SHEETS_DATA = [query_to_df(
        dicParam, QUERY if QUERY.startswith(
            "SELECT") else "SELECT * FROM {}".format(QUERY)
    ) for QUERY in PG_QUERY]
    
    # Produce XLS file
    df_to_xls(
        SHEETS_DATA, out_xls, sheetsName=sheetsnames,
        sanitizeUtf8=None
    )
    
    return out_xls


def pgsqldb_to_xls(workspace, conPSQL={
        'HOST': 'localhost', 'PASSWORD': 'admin',
        'USER': 'postgres', 'DATABASE': 'osm2lulc',
        'PORT': '5432'
    }):
    """
    Execute pgsql_to_xls for all tables in PSQL Database
    """
    
    import os
    from gasp.cpu.psql.i import lst_tbl
    
    tables = lst_tbl(conPSQL)
    
    for table in tables:
        psql_to_xls(
            table,
            os.path.jon(workspace, '{}.xls'.format(table)),
            table, conPSQL
        )


def txt_to_xls(txt, xls_out, delimiter='\t', _encoding_='utf-8'):
    """
    Convert txt to xls file
    """
    
    import codecs
    import os
    import xlwt
    
    # Create XLS file
    xls = xlwt.Workbook(encoding=_encoding_)
    sheet = xls.add_sheet(
        os.path.splitext(os.path.basename(txt))[0]
    )
    
    with codecs.open(txt, 'r', encoding=_encoding_) as f:
        lnh = 0
        
        for line in f:
            c = 0
            
            cols = line.replace('\r', '').strip('\n').split(delimiter)
            
            for col_value in cols:
                sheet.write(lnh, c, col_value)
                c += 1
            
            lnh += 1
        
        xls.save(xls_out)
        
        f.close()


def dbf_to_xls(dbfFile, xlsFile):
    """
    Convert dbf to xlsx using pandas in the process
    """
    
    import os
    from gasp.fm.dbf import dbf_to_df
    from simpledbf   import Dbf5
    from gasp.to.xls import df_to_xls
    
    if os.path.splitext(dbfFile)[1] != '.dbf':
        raise ValueError(
            'dbfFile should be a dBase table'
        )
    
    tableDf = dbf_to_df(dbfFile)
    
    df_to_xls(tableDf, xlsFile)
    
    return xlsFile


def dict_to_xls(dataDict, xlsout_path, outSheet):
    """
    Python Dict to a XLS File

    dict = {
        row_1 : {
            col_1 : XXXXX,
            col_2 : XXXXX,
            ...
            col_n : XXXXX
        },
        row_2 : {
            col_1 : XXXXX,
            col_2 : XXXXX,
            ...
            col_n : XXXXX
        },
        ...,
        row_n : {
            col_1 : XXXXX,
            col_2 : XXXXX,
            ...
            col_n : XXXXX
        }
    }
          | col_1 | col_2 | ... | col_n
    row_1 | XXXXX | XXXXX | ... | XXXXX
    row_2 | XXXXX | XXXXX | ... | XXXXX
      ... | XXXXX | XXXXX | ... | XXXXX
    row_n | XXXXX | XXXXX | ... | XXXXX
    """

    import xlwt

    out_xls = xlwt.Workbook()
    new_sheet = out_xls.add_sheet(outSheet)

    # Write Columns Titles
    new_sheet.write(0, 0, 'ID')
    l = 0
    COLUMNS_ORDER = []

    for fid in dataDict:
        if not l:
            c = 1
            for col in dataDict[fid]:
                COLUMNS_ORDER.append(col)
                new_sheet.write(l, c, col)
                c+=1
            l += 1
        else:
            break

    # Write data - Columns are written by the same order
    for fid in dataDict:
        new_sheet.write(l, 0, fid)

        c = 1
        for col in COLUMNS_ORDER:
            new_sheet.write(l, c, dataDict[fid][col])
            c+=1
        l+=1

    # Save result
    out_xls.save(xlsout_path)
    
    return xlsout_path


def sqlitedb_to_xls(sqliteDB, outXls):
    """
    All tables of one SQLITE Database will be a sheet of outXls
    """
    
    from gasp.sqLite.i  import lst_table
    from gasp.fm.sqLite import sqlq_to_df
    
    tables = lst_table(sqliteDB)
    
    dfs = [sqlq_to_df(
        sqliteDB, "SELECT * FROM {}".format(table)
    ) for table in TABLES]
    
    df_to_xls(dfs, outXls, sheetsName=tables, sanitizeUtf8=True)
    
    return outXls


def table_to_excel_viaA(table, excel, table_ext='.shp'):
    # TODO: table could be a list, No?
    # TODO: if table if a dir, excel must be to
    
    import os
    import arcpy
    
    if os.path.isdir(table):
        from gasp.oss import list_files
        
        tbl_lst = list_files(table, file_format=table_ext)
        
        for t in tbl_lst:
            arcpy.TableToExcel_conversion(
                t,
                os.path.join(
                    excel,
                    os.path.splitext(os.path.basename(t))[0] + '.xls'
                )
            )
    
    else:
        arcpy.TableToExcel_conversion(table, excel)

