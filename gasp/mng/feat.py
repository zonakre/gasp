"""
Feature Classes tools
"""


def eachfeat_to_newshp(inShp, outFolder, epsg=None):
    """
    Export each feature in inShp to a new/single File
    """
    
    import os
    from osgeo                import ogr
    from gasp.prop.ff         import drv_name
    from gasp.prop.feat       import get_geom_type
    from gasp.cpu.gdl.mng.fld import lst_fld
    from gasp.cpu.gdl.mng.fld import ogr_copy_fields
    from gasp.oss             import get_fileformat, get_filename
    
    inDt = ogr.GetDriverByName(
        drv_name(inShp)).Open(inShp)
    
    lyr = inDt.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from gasp.cpu.gdl.mng.prj import get_shp_sref
        srs = get_shp_sref(lyr)
    
    else:
        from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    # Get fields name
    fields = lst_fld(lyr)
    
    # Get Geometry type
    geomCls = get_geom_type(inShp, gisApi='ogr', name=None, py_cls=True)
    
    # Read features and create a new file for each feature
    RESULT_SHP = []
    for feat in lyr:
        # Create output
        newShp = os.path.join(outFolder, "{}_{}{}".format(
            get_filename(inShp), str(feat.GetFID()),
            get_fileformat(inShp)
        ))
        
        newData = ogr.GetDriverByName(
            drv_name(newShp)).CreateDataSource(newShp)
        
        newLyr = newData.CreateLayer(
            get_filename(newShp), srs, geom_type=geomCls
        )
        
        # Copy fields from input to output
        ogr_copy_fields(lyr, newLyr)
        
        newLyrDefn = newLyr.GetLayerDefn()
        
        # Create new feature
        newFeat = ogr.Feature(newLyrDefn)
        
        # Copy geometry
        geom = feat.GetGeometryRef()
        newFeat.SetGeometry(geom)
        
        # Set fields attributes
        for fld in fields:
            newFeat.SetField(fld, feat.GetField(fld))
        
        # Save feature
        newLyr.CreateFeature(newFeat)
        
        newFeat.Destroy()
        
        del newLyr
        newData.Destroy()
        RESULT_SHP.append(newShp)
    
    return RESULT_SHP

