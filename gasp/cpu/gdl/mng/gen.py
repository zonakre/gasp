"""
General tools for data management
"""

def copy_features(inLyr, outLyr, outDefn, only_geom=True):
    """
    Copy the features of one layer to another layer...
    
    If the layers have the same fields, this method could also copy
    the tabular data
    
    TODO: See if the input is a layer or not and make arrangements
    """
    
    from osgeo import ogr
    
    for f in inLyr:
        geom = f.GetGeometryRef()
        
        new = ogr.Feature(outDefn)
        
        new.SetGeometry(geom)
        
        # Copy tabular data
        if not only_geom:
            for i in range(0, outDefn.GetFieldCount()):
                new.SetField(outDefn.GetFieldDefn(i).GetNameRef(), f.GetField(i))
        
        outLyr.CreateFeature(new)
        
        new.Destroy()
        f.Destroy()


def ogr_merge(shp_to_merge, merged_shp, srs=None, fields_to_copy=None):
    """
    Merge all listed datasets into a single dataset
    """
    
    import os
    from osgeo                import ogr
    from gasp                 import goToList
    from gasp.oss             import get_filename
    from gasp.cpu.gdl         import drv_name
    from gasp.prop.feat       import get_geom_type
    from gasp.cpu.gdl.mng.fld import ogr_list_fields_defn
    
    # Create output
    o = ogr.GetDriverByName(
        drv_name(merged_shp)).CreateDataSource(merged_shp)
    
    # Get SRS
    if not srs:
        from gasp.cpu.gdl.mng.prj import get_shp_sref
        srsObj = get_shp_sref(shp_to_merge[0])
    
    else:
        from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
        srsObj = get_sref_from_epsg(srs)
    
    olyr = o.CreateLayer(
        get_filename(merged_shp, forceLower=True),
        srsObj,
        geom_type=get_geom_type(
            shp_to_merge[0], name=None, py_cls=True, gisApi='ogr')
    )
    
    fields_to_copy = goToList(fields_to_copy)
    
    # Add all fields existing in the inputs
    fields_defn = {}
    fields_shp = {}
    for shp in shp_to_merge:
        flds = ogr_list_fields_defn(shp)
        
        fields_shp[shp] = flds.keys()
        
        if not fields_to_copy:
            for fld in flds:
                if fld not in fields_defn:
                    fields_defn[fld] = flds[fld].keys()[0]
                    
                    olyr.CreateField(ogr.FieldDefn(fld, flds[fld].keys()[0]))
            
        else:
            for fld in flds:
                if fld not in fields_defn and fld in fields_to_copy:
                    fields_defn[fld] = flds[fld].keys()[0]
                    olyr.CreateField(ogr.FieldDefn(fld, flds[fld].keys()[0]))
    
    # Join all features together on the same dataset
    featDefn = olyr.GetLayerDefn()
    for i in range(len(shp_to_merge)):
        dt = ogr.GetDriverByName(
            drv_name(shp_to_merge[i])).Open(shp_to_merge[i], 0)
        
        lyr = dt.GetLayer()
        
        for feat in lyr:
            geom = feat.GetGeometryRef()
            new = ogr.Feature(featDefn)
            new.SetGeometry(geom)
            
            for e in range(0, featDefn.GetFieldCount()):
                name = featDefn.GetFieldDefn(e).GetNameRef()
                if name in fields_shp[shp_to_merge[i]]:
                    new.SetField(name, feat.GetField(name))
            
            olyr.CreateFeature(new)
            
            new.Destroy()
            feat.Destroy()
        
        dt.Destroy()
    
    o.Destroy()
    
    return merged_shp

