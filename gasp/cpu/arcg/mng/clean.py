"""
Clean table data with arcGIS
"""

import arcpy


def round_table_values(table, decimal_by_col_file, outputFile):
    """
    Round all column values using the number of decimal places written
    in a excel file
    
    COL_NAME | nr_decimal_places
    COL_1    | 1
    COL_2    | 0
    ...      | ...
    COL_N    | 2
    """
    
    from gasp.cpu.arcg.lyr     import feat_lyr
    from gasp.cpu.arcg.mng.gen import copy_features
    from gasp.cpu.arcg.mng.fld import type_fields
    from gasp.fm.xls           import xls_to_dict
    
    arcpy.env.overwriteOutput = True
    
    # Get number of decimal places for the values of each column
    places_by_col = xls_to_dict(decimal_by_col_file, sheet=0)
    
    PLACES_FIELD = places_by_col[places_by_col.keys()[0]].keys()[0]
    
    # Copy table
    outTable = copy_features(table, outputFile)
    
    # Edit copy putting the correct decimal places in each column
    lyr = feat_lyr(outTable)
    
    # List table fields
    fields = type_fields(lyr)
    cursor = arcpy.UpdateCursor(lyr)
    for lnh in cursor:
        for col in fields:
            if col in places_by_col:
                if fields[col] == 'Integer' or fields[col] == 'Double' \
                   or fields[col] == 'SmallInteger':
                    value = lnh.getValue(col)
                
                    lnh.setValue(
                        col, 
                        round(value, int(places_by_col[col][PLACES_FIELD]))
                    )
                else:
                    continue
            else:
                print "{} not in {}".format(col, decimal_by_col_file)
        
        cursor.updateRow(lnh)
    
    del lyr
    
    return outputFile


def round_tables_values(fldTables, decimal_col_file, outFolder,
                        table_format='.shp'):
    """
    Round all column values using the number of decimal places written
    in a excel file in loop
    """
    
    import os
    
    from gasp.oss import list_files
    
    tables = list_files(fldTables, file_format=table_format)
    
    for table in tables:
        round_table_values(
            table, decimal_col_file, os.path.join(
                outFolder, 'rnd_' + os.path.basename(table)
            )
        )

