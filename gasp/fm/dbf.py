"""DBF Tables to Something"""


def dbf_to_df(dbfTable):
    """
    Convert dBase to Pandas Dataframe
    """
    
    from simpledbf import Dbf5
    
    dbfObj = Dbf5(dbfTable)
    tableDf = dbfObj.to_dataframe()
    
    return tableDf


def dbase_to_dict(inTbl, fields_filter=None):
    """
    Shapefile table to dict
    
    Return
    dict = {
        0 : {
            Field_1 : value,
            ...
            Field_N : value
        }
        ...
    }
    """
    
    from gasp        import goToList
    from gasp.to.obj import df_to_dict
    
    # dBase Table to Pandas Dataframe
    dBaseDf = dbf_to_df(inTbl)
    
    # Delete unecessary fields
    fields_filter = goToList(fields_filter)
    if fields_filter:
        delCols = []
        for fld in list(dBaseDf.columns.values):
            if fld not in fields_filter:
                delCols.append(fld)
        
        if delCols:
            dBaseDf.drop(delCols, axis=1, inplace=True)
    
    # DataFrame to Dict
    dbase_dict = df_to_dict(dBaseDf)
    
    return dbase_dict

