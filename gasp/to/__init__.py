"""
File data to File Data
"""


def obj_to_tbl(pyObj, outTbl, delimiter=None, wIndex=None,
               sheetsName=None, sanitizeUtf8=True):
    """
    Python object to data File
    """
    
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
    
    import pandas
    from gasp.oss import get_fileformat
    
    ff = get_fileformat(outTbl)
    
    if ff == '.txt' or ff == '.csv' or ff == '.tsv':
        if not delimiter:
            raise ValueError((
                "To save your data into a text file, you need to give a value "
                "to the delimiter input parameter"
            ))
        
        if type(pyObj) == pandas.DataFrame:
            pyObj.to_csv(outTbl, sep=delimiter, encoding='utf-8', index=wIndex)
        
        else:
            raise ValueError((
                "pyObj has an invalid data type"
            ))
    
    elif ff == '.xlsx' or ff == '.xls':
        from gasp import goToList
        from gasp.oss import get_filename
        
        dfs = [pyObj] if type(pyObj) != list else pyObj
        sheetsName = goToList(sheetsName)
        
        for df in dfs:
            if type(df) != pandas.DataFrame:
                raise ValueError("pyObj has an invalid data type")
            
        if sanitizeUtf8:
            for i in range(len(dfs)):
                COLS = list(dfs[i].columns.values)
                
                dt = dfs[i].apply(lambda x: sanitizeP(x, COLS), axis=1)
                
                dfs[i] = dt
            
        writer = pandas.ExcelWriter(outTbl, engine='xlsxwriter')
        
        for i in range(len(dfs)):
            dfs[i].to_excel(
                writer,
                sheet_name="{}_{}".format(
                    get_filename(outTbl), str(i)
                ) if not sheetsName or i+1 > len(sheetsName) else sheetsName[i]
            )
        
        writer.save()
    
    else:
        raise ValueError('{} is not a valid table format!'.format(ff))
    
    return outTbl


def tbl_to_tbl(inTbl, outTbl, inSheet=None, txtDelimiter=None,
               inTxtDelimiter=None, inEncoding='utf-8'):
    """
    Convert data format
    """
    
    from gasp.fm import tbl_to_obj
    
    data = tbl_to_obj(
        tblFile, sheet=inSheet,
        #useFirstColAsIndex, _delimiter,
        encoding_=inEncoding, _delimiter=inTxtDelimiter
        #output, fields, geomCol, colsAsArray, geomAsWkt, srsTo
    )
    
    outTbl = obj_to_tbl(data, outTbl, delimiter=txtDelimiter)
    
    return outTbl


def db_to_tbl(conDB, tables, outTbl, txtDelimiter=None, dbAPI='psql',
              outTblF=None, sheetsNames=None):
    """
    Database data to File table
    
    API's Avaialble:
    * psql;
    * sqlite;
    """
    
    import os
    from gasp        import goToList
    from gasp.fm.sql import query_to_df
    
    if tables == 'ALL':
        from gasp.sql.mng.tbl import lst_tbl
        
        tables = lst_tbl(conDB, schema='public', excludeViews=True, api=dbAPI)
    else:
        tables = goToList(tables)
    
    sheetsNames = goToList(sheetsNames)
    
    outTblF = None if not outTblF else outTblF \
        if outTblF[0] == '.' else '.' + outTblF
    
    if len(tables) > 1:
        if not os.path.isdir(outTbl) or not outTblF:
            raise ValueError((
                "When tables has more than one table, "
                "outTbl must be dir and outTblF must be specified"
            ))
    
    elif len(tables) == 1:
        if os.path.isdir(outTbl) and outTblF:
            outTbl = os.path.join(outTbl, tables[0] + outTblF)
        
        elif os.path.isdir(outTbl) and not outTbl:
            raise ValueError((
                'We find only a table to export and outTbl is a dir. '
                'Please give a path to a file or specify the table format '
                'using outTblF format'
            ))
        
        else:
            outTbl = outTbl
    
    else:
        raise ValueError(
            "tables value is not valid"
        )   
    
    DFS = [query_to_df(
        conDB, t if t.startswith(
            "SELECT") else "SELECT * FROM {}".format(t), db_api=dbAPI
    ) for t in tables]
    
    if os.path.isfile(outTbl):
        from gasp.oss import get_fileformat
        
        ff = get_fileformat(outTbl)
        
        if ff == '.xlsx' or ff == '.xls':
            obj_to_tbl(DFS, outTbl, sheetsName=sheetsNames, sanitizeUtf8=None)
            
            return outTbl
    
    for i in range(len(DFS)):
        obj_to_tbl(
            DFS[i],
            outTbl if len(DFS) == 1 else os.path.join(
                outTbl, tables[i] + outTblF
            ),
            delimiter=txtDelimiter,
            sheetsName=sheetsNames
        )
    
    return outTbl


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

