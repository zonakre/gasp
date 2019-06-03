"""
Spatial Reference Systems Properties
"""

from osgeo import osr

def epsg_to_wkt(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    
    return s.ExportToWkt()


def get_sref_from_epsg(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    
    return s

def get_shp_sref(shp):
    """
    Get Spatial Reference Object from Feature Class/Lyr
    """
    
    from osgeo        import ogr
    from gasp.prop.ff import drv_name
    
    if type(shp) == ogr.Layer:
        lyr = shp
        
        c = 0
    
    else:
        data = ogr.GetDriverByName(
            drv_name(shp)).Open(shp)
        
        lyr = data.GetLayer()
        c = 1
    
    spref = lyr.GetSpatialRef()
    
    if c:
        del lyr
        data.Destroy()
    
    return spref

