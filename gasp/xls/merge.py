"""
Merge tables
"""

def merge_tables_in_folder(tbl_folder, out_table):
    """
    Get all excel tables in a folder and make one table of them
    """
    
    import pandas
    
    from gasp.oss    import list_files
    from gasp.fm.xls import xls_to_df
    from gasp.to.xls import df_to_xls
    
    tables = list_files(tbl_folder, file_format=['.xls', '.xlsx'])
    
    dfs = [xls_to_df(table) for table in tables]
    
    result = pandas.concat(dfs)
    
    out_table = df_to_xls(result, out_table)
    
    return out_table


def merge_sheets_into_file(xlsFolder, outXls, intSheets):
    """
    For each xls file in one folder, pick one interest sheet
    and save all sheets in a single file
    """
    
    from gasp           import goToList
    from gasp.oss.info  import list_files
    from gasp.oss.info  import get_filename
    from gasp.xls.sheet import copy_sheet_to_file
    
    xls_s = list_files(xlsFolder, file_format=['.xls', '.xlsx'])
    
    for xlsPath in xls_s:
        copy_sheet_to_file(
            xlsPath, outXls, intSheets,
            {intSheets : get_filename(xlsPath, forceLower=True)}
        )
    
    return outXls
