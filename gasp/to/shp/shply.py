"""
Array with Shapely Geometries to a Feature Class
"""

from osgeo import ogr

def shply_array_to_shp(arrayLike, outfile, geomType, epsg=None,
                         fields=None, crsObj=None):
    """
    Convert a array with Shapely geometric data into a file
    with geometry (GML, ESRI Shapefile or others).
    
    Example of an array_like object:
    data = [
        {col_1: value, col_2: value, geom: geomObj},
        {col_1: value, col_2: value, geom: geomObj},
    ]
    """
    
    import os
    from gasp.prop.ff  import drv_name
    from gasp.prop.prj import get_sref_from_epsg
    
    # Create output file
    shp = ogr.GetDriverByName(
        drv_name(outfile)).CreateDataSource(outfile)
    
    lyr = shp.CreateLayer(
        os.path.splitext(os.path.basename(outfile))[0],
        get_sref_from_epsg(epsg) if epsg else crsObj if crsObj else \
            None, geom_type=geomType
    )
    
    # Create fields of output file
    # TODO: Automatic mapping of filters types needs further testing
    if fields:
        for f in fields:
            lyr.CreateField(ogr.FieldDefn(f, fields[f]))
    
    # Add features
    defn = lyr.GetLayerDefn()
    for feat in arrayLike:
        newFeat = ogr.Feature(defn)
        
        newFeat.SetGeometry(
            ogr.CreateGeometryFromWkb(feat['GEOM'].wkb)
        )
        
        if len(fields):
            for f in fields:
                newFeat.SetField(f, feat[f])
        
        lyr.CreateFeature(newFeat)
        
        newFeat = None
    
    shp.Destroy()
    
    return outfile


def shply_dict_to_shp(dictLike, outfile, geomType, epsg=None,
                      fields=None, crsObj=None):
    """
    Dict with shapely Geometries to Feature Class
    """
    
    import os
    from gasp.prop.ff  import drv_name
    from gasp.prop.prj import get_sref_from_epsg
    from gasp.oss      import get_filename
    
    # Create output file
    shp = ogr.GetDriverByName(
        drv_name(outfile)).CreateDataSource(outfile)
    
    lyr = shp.CreateLayer(get_filename(outfile),
        get_sref_from_epsg(epsg) if epsg else crsObj if \
            crsObj else None,
        geom_type=geomType
    )
    
    # Create fields of output file
    if fields:
        for f in fields:
            lyr.CreateField(ogr.FieldDefn(f, fields[f]))
    
    # Add features
    fids = dictLike.keys()
    fids.sort()
    defn = lyr.GetLayerDefn()
    for fid in fids:
        if type(dictLike[fid]["GEOM"]) == list:
            for geom in dictLike[fid]["GEOM"]:
                newFeat = ogr.Feature(defn)
        
                newFeat.SetGeometry(
                    ogr.CreateGeometryFromWkb(geom.wkb)
                )
                
                if len(fields):
                    for f in fields:
                        newFeat.SetField(f, dictLike[fid][f])
                
                lyr.CreateFeature(newFeat)
                
                newFeat = None
        
        else:
            newFeat = ogr.Feature(defn)
            
            newFeat.SetGeometry(
                ogr.CreateGeometryFromWkb(dictLike[fid]["GEOM"].wkb)
            )
            
            if len(fields):
                for f in fields:
                    newFeat.SetField(f, dictLike[fid][f])
                
            lyr.CreateFeature(newFeat)
            
            newFeat = None
    
    del lyr
    shp.Destroy()
    
    return outfile

