# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Data Management Tools > General
"""

"""
Pandas Objects Tools
"""

def merge_df(dfs, ignIndex=True):
    """
    Merge Multiple DataFrames into one
    """
    
    if type(dfs) != list:
        raise ValueError('dfs should be a list with Pandas Dataframe')
    
    result = dfs[0]
    
    for df in dfs[1:]:
        result = result.append(df, ignore_index=ignIndex)#, sort=True)
    
    return result

"""
Tools to process GIS Data in files
"""

def copy_feat(inShp, outShp, gisApi='arcpy', outDefn=None, only_geom=None):
    """
    Copy Features to a new Feature Class
    """
    
    if gisApi == 'arcpy':
        import arcpy
        
        arcpy.CopyFeatures_management(inShp, outShp, "", "", "", "")
    
    elif gisApi == 'ogrlyr':
        """
        Copy the features of one layer to another layer...
    
        If the layers have the same fields, this method could also copy
        the tabular data
    
        TODO: See if the input is a layer or not and make arrangements
        """
        
        from osgeo import ogr
        
        for f in inShp:
            geom = f.GetGeometryRef()
        
            new = ogr.Feature(outDefn)
        
            new.SetGeometry(geom)
        
        # Copy tabular data
        if not only_geom:
            for i in range(0, outDefn.GetFieldCount()):
                new.SetField(outDefn.GetFieldDefn(i).GetNameRef(), f.GetField(i))
        
        outShp.CreateFeature(new)
        
        new.Destroy()
        f.Destroy()
        
        return None
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp   


def merge_feat(shps, outShp, api="ogr2ogr"):
    """
    Get all features in several Shapefiles and save them in one file
    """
    
    if api == "ogr2ogr":
        from gasp         import exec_cmd
        from gasp.prop.ff import drv_name
        
        out_drv = drv_name(outShp)
        
        # Create output and copy some features of one layer (first in shps)
        cmdout = exec_cmd('ogr2ogr -f "{}" {} {}'.format(
            out_drv, outShp, shps[0]
        ))
        
        # Append remaining layers
        lcmd = [exec_cmd(
            'ogr2ogr -f "{}" -update -append {} {}'.format(
                out_drv, outShp, shps[i]
            )
        ) for i in range(1, len(shps))]
    
    elif api == 'pandas':
        """
        Merge SHP using pandas
        """
        
        from gasp.fm     import tbl_to_obj
        from gasp.to.shp import df_to_shp
        
        if type(shps) != list:
            raise ValueError('shps should be a list with paths for Feature Classes')
        
        dfs = [tbl_to_obj(shp) for shp in shps]
        
        result = dfs[0]
        
        for df in dfs[1:]:
            result = result.append(df, ignore_index=True, sort=True)
        
        df_to_shp(result, outShp)
    
    else:
        raise ValueError(
            "{} API is not available"
        )
    
    return outShp


def same_attr_to_shp(inShps, interestCol, outFolder, basename="data_",
                     resultDict=None):
    """
    For several SHPS with the same field, this program will list
    all values in such field and will create a new shp for all
    values with the respective geometry regardeless the origin shp.
    """
    
    import os
    from gasp         import goToList
    from gasp.fm      import tbl_to_obj
    from gasp.mng.gen import merge_df
    from gasp.to.shp  import df_to_shp
    
    EXT = os.path.splitext(inShps[0])[1]
    
    shpDfs = [tbl_to_obj(shp) for shp in inShps]
    
    DF = merge_df(shpDfs, ignIndex=True)
    #DF.dropna(axis=0, how='any', inplace=True)
    
    uniqueVal = DF[interestCol].unique()
    
    nShps = [] if not resultDict else {}
    for val in uniqueVal:
        ndf = DF[DF[interestCol] == val]
        
        KEY = str(val).split('.')[0] if '.' in str(val) else str(val)
        
        nshp = df_to_shp(ndf, os.path.join(
            outFolder, '{}{}{}'.format(basename, KEY, EXT)
        ))
        
        if not resultDict:
            nShps.append(nshp)
        else:
            nShps[KEY] = nshp
    
    return nShps


"""
Tools for PDF
"""

def merge_pdf(inputPdf, outPdf):
    """
    Merge several PDF's in the same file
    """
    
    from PyPDF2 import PdfFileWriter, PdfFileReader
    
    pdf_writer = PdfFileWriter()
    
    for _pdf in inputPdf:
        pdf_reader = PdfFileReader(_pdf)
        for page in range(pdf_reader.getNumPages()):
            pdf_writer.addPage(pdf_reader.getPage(page))
    
    with open(outPdf, 'wb') as fh:
        pdf_writer.write(fh)
    
    return outPdf


"""
Tools for Excel data
"""

def merge_xls_in_folder(tbl_folder, out_table):
    """
    Get all excel tables in a folder and make one table of them
    """
    
    import pandas
    from gasp.oss import list_files
    from gasp.fm  import tbl_to_obj
    from gasp.to  import obj_to_tbl
    
    tables = list_files(tbl_folder, file_format=['.xls', '.xlsx'])
    
    dfs = [tbl_to_obj(table) for table in tables]
    
    result = pandas.concat(dfs)
    
    out_table = obj_to_tbl(result, out_table)
    
    return out_table


def sheets_into_file(xlsFolder, outXls, intSheets):
    """
    For each xls file in one folder, pick one interest sheet
    and save all sheets in a single file
    """
    
    from gasp                  import goToList
    from gasp.oss.info         import list_files
    from gasp.oss.info         import get_filename
    from gasp.mng.xlstbx.sheet import copy_sheet_to_file
    
    xls_s = list_files(xlsFolder, file_format=['.xls', '.xlsx'])
    
    for xlsPath in xls_s:
        copy_sheet_to_file(
            xlsPath, outXls, intSheets,
            {intSheets : get_filename(xlsPath, forceLower=True)}
        )
    
    return outXls

