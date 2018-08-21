"""
Split tables
"""


def split_table_by_number(xlsTable, row_number, output,
                          sheetName=None, sheetIndex=None):
    """
    Split a table by row number
    
    Given a number of rows, this method will split an input table
    in several tables with a number of rows equal to row_number.
    
    TODO: Do it with Pandas
    """
    
    import xlrd
    import xlwt
    from gasp.xls.fld import columns_by_order
    from gasp.fm.xls  import xls_to_array
    
    COLUMNS_ORDER = columns_by_order(
        xlsTable, sheet_name=sheetName, sheet_index=sheetIndex
    )
    
    DATA = xls_to_array(xlsTable,
        sheet=sheetIndex if sheetIndex else sheetName
    )
    
    # Create output
    out_xls = xlwt.Workbook()
    
    l = 1
    s = 1
    base = sheetName if sheetName else 'data'
    for row in DATA:
        if l == 1:
            sheet = out_xls.add_sheet('{}_{}'.format(base, s))
            
            # Write Columns
            for col in range(len(COLUMNS_ORDER)):
                sheet.write(0, col, COLUMNS_ORDER[col])
        
        for col in range(len(COLUMNS_ORDER)):
            sheet.write(l, col, row[COLUMNS_ORDER[col]])
        
        l += 1
        
        if l == row_number + 1:
            l = 1
            s += 1
    
    # Save result
    out_xls.save(output)

