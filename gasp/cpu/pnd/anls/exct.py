"""
Extract data tools using Pandas
"""

def split_shp_by_attr(inShp, attr, outDir, _format='.shp'):
    """
    Create a new shapefile for each value in a column
    """
    
    import os
    from gasp.fm.shp          import shp_to_df
    from gasp.oss             import get_filename
    from gasp.cpu.pnd.mng.fld import col_distinct
    from gasp.to.shp          import df_to_shp
    
    # Sanitize format
    FFF = _format if _format[0] == '.' else '.' + _format
    
    # SHP TO DF
    dataDf = shp_to_df(inShp)
    
    # Get values in attr
    uniqueAttr = col_distinct(dataDf, attr)
    
    # Export Features with the same value in attr to a new File
    BASENAME = get_filename(inShp, forceLower=True)
    for val in uniqueAttr:
        df = dataDf[dataDf[attr] == val]
        
        newShp = df_to_shp(df, os.path.join(outDir, "{}_{}{}".format(
            BASENAME, str(val), FFF
        )))
    
    return outDir

