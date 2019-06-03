"""
Operations based on extent
"""

from osgeo        import ogr
from gasp.prop.ff import drv_name


def coords_to_boundary(topLeft, lowerRight, epsg, outshp):
    """
    Top Left and Lower Right to Boundary
    """
    
    import os
    from gasp.oss      import get_filename
    from gasp.prop.prj import get_sref_from_epsg
    
    boundary_points = [
        (   topLeft[0],    topLeft[1]),
        (lowerRight[0],    topLeft[1]),
        (lowerRight[0], lowerRight[1]),
        (   topLeft[0], lowerRight[1]),
        (   topLeft[0],    topLeft[1])
    ]
    
    shp = ogr.GetDriverByName(
        drv_name(outshp)).CreateDataSource(outshp)
    
    lyr = shp.CreateLayer(
        get_filename(outshp), get_sref_from_epsg(epsg),
        geom_type=ogr.wkbPolygon
    )
    
    outDefn = lyr.GetLayerDefn()
    
    feat = ogr.Feature(outDefn)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    
    for pnt in boundary_points:
        ring.AddPoint(pnt[0], pnt[1])
    
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    
    feat.SetGeometry(polygon)
    lyr.CreateFeature(feat)
    
    feat.Destroy()
    shp.Destroy()
    
    return outshp


def shpext_to_boundary(inShp, outShp, epsg=None):
    """
    Read one feature class extent and create a boundary with that
    extent
    
    The outFile could be a Feature Class or one Raster Dataset
    """
    
    import os
    from gasp.oss      import get_filename
    from gasp.to.geom  import create_point
    from gasp.prop.ext import get_extent
    
    extent = get_extent(inShp, gisApi='ogr')
    
    # Create points of the new boundary based on the extent
    boundary_points = [
        create_point(extent[0], extent[3], api='ogr'),
        create_point(extent[1], extent[3], api='ogr'),
        create_point(extent[1], extent[2], api='ogr'),
        create_point(extent[0], extent[2], api='ogr'),
        create_point(extent[0], extent[3], api='ogr')
    ]
    
    # Get SRS for the output
    if not epsg:
        from gasp.prop.prj import get_shp_sref
        srs = get_shp_sref(inShp)
    
    else:
        from gasp.prop.prj import get_sref_from_epsg
        srs= get_sref_from_epsg(epsg)
    
    # Write new file
    shp = ogr.GetDriverByName(
        drv_name(outShp)).CreateDataSource(outShp)
    
    lyr = shp.CreateLayer(
        get_filename(outShp, forceLower=True),
        srs, geom_type=ogr.wkbPolygon
    )
    
    outDefn = lyr.GetLayerDefn()
    
    feat = ogr.Feature(outDefn)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    
    for pnt in boundary_points:
        ring.AddPoint(pnt.GetX(), pnt.GetY())
    
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    
    feat.SetGeometry(polygon)
    lyr.CreateFeature(feat)
    
    feat.Destroy()
    shp.Destroy()
    
    return outShp


def pnts_to_boundary(pntShp, outBound, distMeters):
    """
    Create a boundary from Point using a tolerance in meters
    """
    
    from osgeo         import ogr
    from gasp.oss      import get_filename
    from gasp.prop.ff  import drv_name
    from gasp.to.geom  import create_point
    from gasp.prop.prj import get_shp_sref
    
    SRS = get_shp_sref(pntShp)
    
    shp = ogr.GetDriverByName(drv_name(pntShp)).Open(pntShp)
    lyr = shp.GetLayer()
    
    outShp = ogr.GetDriverByName(drv_name(outBound)).CreateDataSource(outBound)
    outLyr = outShp.CreateLayer(
        get_filename(outBound, forceLower=True), SRS,
        geom_type=ogr.wkbPolygon
    )
    
    outDefn = outLyr.GetLayerDefn()
    
    for feat in lyr:
        __feat = ogr.Feature(outDefn)
        ring = ogr.Geometry(ogr.wkbLinearRing)
        
        geom = feat.GetGeometryRef()
        X, Y = geom.GetX(), geom.GetY()
        
        boundary_points = [
            create_point(X - distMeters, Y + distMeters, api='ogr'), # Topleft
            create_point(X + distMeters, Y + distMeters, api='ogr'), # TopRight
            create_point(X + distMeters, Y - distMeters, api='ogr'), # Lower Right
            create_point(X - distMeters, Y - distMeters, api='ogr'), # Lower Left
            create_point(X - distMeters, Y + distMeters, api='ogr')
        ]
        
        for pnt in boundary_points:
            ring.AddPoint(pnt.GetX(), pnt.GetY())
        
        polygon = ogr.Geometry(ogr.wkbPolygon)
        polygon.AddGeometry(ring)
        
        __feat.SetGeometry(polygon)
        
        outLyr.CreateFeature(__feat)
        
        feat.Destroy()
        
        __feat  = None
        ring    = None
        polygon = None
    
    shp.Destroy()
    outShp.Destroy()
    
    return outBound

