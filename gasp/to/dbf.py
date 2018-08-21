"""
Table conversion operations
"""

import arcpy

def xls_to_dbf(xlsTbl, dbfTbl, sheetname):
    """
    Excel table to dBase Table
    """
    
    arcpy.ExcelToTable_conversion(
        xlsTbl, dbfTbl, sheetname
    )
    
    return dbfTbl


def excel_to_table(xlsTable, dbfTable, sheetname=None, sheetindex=None):
    """
    Excel table to dBase
    
    If sheetname not given, convert all sheets to a new table
    sheetname could also be a list
    """
    
    import os
    from gasp.xls import list_sheets
    
    if os.path.isdir(xlsTable):
        if not os.path.isdir(dbfTable):
            raise ValueError((
                'If xlsTable is a folder with xls files, '
                'dbfTable must be a folder also'
            ))
        
        else:
            from gasp.oss import get_filename
            from gasp.oss import list_files
            
            tables = list_files(xlsTable, file_format=['.xls', '.xlsx'])
            
            for table in tables:
                if sheetname:
                    xls_to_dbf(
                        table,
                        os.path.join(dbfTable, '{}.dbf'.format(
                            get_filename(table)
                        )),
                        sheetname
                    )
                else:
                    sheets = list_sheets(table)
                    if sheetindex:
                        xls_to_dbf(
                            table,
                            os.path.join(dbfTable, '{}.dbf'.format(
                                get_filename(table)
                            )),
                            sheets[sheetindex]
                        )
                    
                    else:
                        for x in sheets:
                            xls_to_dbf(
                                table,
                                os.path.join(dbfTable, "{}_{}.dbf".format(
                                    get_filename(table), x
                                )),
                                x
                            )
    
    else:
        if not sheetname and sheetindex:
            if not os.path.isdir(dbfTable):
                raise ValueError((
                    'If no sheet name is specify, all sheets will be converted '
                    'to dBase, so dbfTable should be a path to a directory'
                ))
        
        if sheetname:
            xls_to_dbf(xlsTable, dbfTable, sheetname)
        
        else:
            sheets = list_sheets(xlsTable)
            
            if sheetindex:
                xls_to_dbf(xlsTable, dbfTable, sheets[sheetindex])
            
            else:
                for sheetn in sheets:
                    xls_to_dbf(
                        xlsTable, 
                        os.path.join(dbfTable, sheetn + '.dbf'),
                        sheetn
                    )

