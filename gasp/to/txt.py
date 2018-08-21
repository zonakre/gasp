"""
Any table to txt file
"""


def xls_to_txt(inXls, delimiter, outTxt, en_coding='utf-8'):
    """
    Excel to Text File
    
    Create a new txt table which columns are delimited by a delimiter specfified
    by the user.
    """
    
    def sanitize(v):
        if type(v) == type(10.0):
            if v == int(v):
                return unicode(int(v))
            else:
                return unicode(v)
        else:
            return unicode(v)
    
    
    import xlrd
    import codecs
    
    
    # Open input
    xls_data = xlrd.open_workbook(inXls)
    sheets = xls_data.sheet_names()
    sheet = xls_data.sheet_by_name(sheets[0])
    # Create output
    with codecs.open(outTxt, 'w', encoding=en_coding) as f:
        for row in range(sheet.nrows):
            l = [sheet.cell(row, col).value for col in range(sheet.ncols)]
            for i in range(len(l)):
                if i+1 == len(l):
                    f.write(sanitize(l[i]) + '\n')
                else:
                    f.write(sanitize(l[i]) + delimiter)
        f.close()


def pgsql_to_txt(pg_table, out_txt, delimiter, where_clause=None,
                 _encoding='utf-8',
                 dic_con={
                     'HOST': 'localhost', 'PASSWORD': 'admin',
                     'USER': 'postgres', 'DATABASE': 'matuc_db', 'PORT': '5432'
                     }):
    """
    Method to export data from PostgreSQL to a text file
    """
    
    def sanitize(v):
        if type(v) == type(10.0):
            if v == int(v):
                return unicode(str(int(v)), _encoding)
            else:
                return unicode(str(v), _encoding)
        else:
            return unicode(str(v), _encoding)    

    import os;                 import codecs
    from gasp.fm.psql          import sql_query
    from gasp.cpu.psql.mng.fld import cols_name

    # Delete output file if exists
    if os.path.exists(out_txt):
        os.remove(out_txt)

    # Get columns names
    colsName = cols_name(dic_con, pg_table)

    # Get data from postgresql
    if where_clause != None:
        table_data = sql_query(
            dic_con,
            "SELECT {col_s} FROM {tbl} WHERE {whr};".format(
                col_s=', '.join(colsName),
                tbl=pg_table, whr=where_clause
            )
        )

    else:
        table_data = sql_query(
            dic_con,
            "SELECT {col_s} FROM {tbl};".format(
                col_s=', '.join(colsName), tbl=pg_table
            )
        )

    # Create txt file
    with codecs.open(out_txt, 'w', encoding=_encoding) as txt:
        for i in range(len(colsName)):
            if i+1 == len(colsName):
                txt.write(sanitize(colsName[i]) + '\n')
            else:
                txt.write(sanitize(colsName[i]) + delimiter)

        for row in table_data:
            l = [value for value in row]

            for i in range(len(colsName)):
                if i+1 == len(colsName):
                    txt.write(sanitize(l[i]) + '\n')
                else:
                    txt.write(sanitize(l[i]) + delimiter)
        txt.close()


def pgsqldb_to_txt(delimiter, workspace, __conPSQL, encoding='utf-8'):
    """
    Execute pgsql_to_txt for all tables in a database
    """
    
    import os
    from gasp.cpu.psql.i import lst_tbl
    
    tables = lst_tbl(__conPSQL)
    
    for table in tables:
        pgsql_to_txt(
            table,
            os.path.join(workspace, '{}.txt'.format(table)),
            delimiter, _encoding=encoding,
            dic_con=__conPSQL
        )


def dbf_to_txt(dbf, delimiter, out_txt, encoding='utf-8'):
    """
    Export dbf table to a txt file
    """
    
    import codecs;            import os
    from osgeo                import ogr
    from gasp.cpu.gdl.mng.fld import lst_fld
    
    def sanitize(v):
        if type(v) == float:
            if v == int(v):
                return unicode(str(int(v)), "utf-8")
            else:
                return unicode(str(v), "utf-8")
        elif type(v) == int:
            return unicode(str(v), "utf-8")
        else:
            return unicode(v, "utf-8")
    
    if os.path.exists(dbf):
        if os.path.splitext(dbf)[1] != '.dbf':
            raise ValueError('The specified file is not a dbf file')
    
    else:
        raise ValueError('The specified file does not exist')
    
    # Open input
    table = ogr.GetDriverByName("ESRI Shapefile").Open(dbf, 0)
    
    viewTable = table.GetLayer()
    
    cols = lst_fld(dbf)
    
    # Create txt file
    with codecs.open(out_txt, 'w', encoding=encoding) as txt:
        for i in range(len(cols)):
            if i+1 == len(cols):
                txt.write(sanitize(cols[i]) + '\n')
            else:
                txt.write(sanitize(cols[i]) + delimiter)
        
        for row in viewTable:
            for i in range(len(cols)):
                value = row.GetField(cols[i])
                if i+1 == len(cols):
                    txt.write(sanitize(value) + '\n')
                else:
                    txt.write(sanitize(value) + delimiter)
        
        txt.close()


def df_to_txt(df, outTxt, delimiter='\t', wIndex=False):
    """
    Write a Pandas dataframe in a CSV File
    """
    
    df.to_csv(outTxt, sep=delimiter, encoding='utf-8',
              index=wIndex)
    
    return outTxt


def psql_to_txt(table, outTxt, conParam, delim="\t"):
    """
    PGSQL TO TEXT USING PANDAS
    """
    
    from gasp.fm.psql import query_to_df
    
    tableDf = query_to_df(
        conParam, "SELECT * FROM {}".format(table)
    )
    
    df_to_txt(tableDf, outTxt, delim)
    
    return outTxt


def psqldb_to_txt(delimiter, workspace, conPSQL):
    """
    All tables in PSQL DB to text files
    """
    
    import os
    from gasp.cpu.psql.i import lst_tbl
    
    tables = lst_tbl(conPSQL)
    
    for table in tables:
        psql_to_txt(
            table,
            os.path.join(workspace, "{}.txt".format(table)),
            conPSQL, delim=delimiter
        )


"""
Geometry to Text file

TODO: These methods are for ArcGIS. Convert them to
a method that could be used with any software
"""
def pnt_to_txt(pntShp, outTxt):
    """
    Point Feature Class to Text File
    """
    
    from gasp.cpu.arcg.lyr import feat_lyr
    
    lyr = feat_lyr(pntShp)
    
    with open(outTxt, mode='w') as txt:
        cursor = arcpy.SearchCursor(lyr)
        
        for linha in cursor:
            txt.write(
                '{fid} {pnt}\n'.format(
                    fid=str(linha.getValue("FID")),
                    pnt=str(linha.Shape.centroid)
                )
            )
        
        txt.close()
    
    return outTxt

def lines_polygons_to_txt(lnhShp, outTxt):
    """
    Lines or Polygons Feature Class to Text File
    """
    
    from gasp.cpu.arcg.lyr import feat_lyr
    
    lyr = feat_lyr(lnhShp)
    
    with open(outTxt, mode='w') as txt:
        cursor = arcpy.SearchCursor(lyr)
        
        for reg in cursor:
            fid  = reg.getValue("FID")
            geom = reg.getValue("Shape")
            
            nr_part = 0
            
            for vector in geom:
                for pnt in vector:
                    txt.write(
                        '{_id} {part} {_pnt}\n'.format(
                            _id=str(fid), part=str(nr_part), _pnt=str(pnt)
                        )
                    )
                
                nr_part += 1
        
        txt.close()
    
    return outTxt

