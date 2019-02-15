"""
To be defined
"""

from osgeo         import ogr
from gasp.prop.ff import drv_name
from gasp.web      import get_file


def coords_to_boundary(topLeft, lowerRight, epsg, outshp):
    """
    Top Left and Lower Right to Boundary
    """
    
    import os
    from gasp.oss              import get_filename
    from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
    
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


def shpextent_to_boundary(inShp, outShp, epsg=None):
    """
    Read one feature class extent and create a boundary with that
    extent
    
    The outFile could be a Feature Class or one Raster Dataset
    """
    
    import os
    from gasp.oss      import get_filename
    from gasp.cpu.gdl import create_point
    from gasp.prop.ext import get_extent
    
    extent = get_extent(inShp, gisApi='ogr')
    
    # Create points of the new boundary based on the extent
    boundary_points = [
        create_point(extent[0], extent[3]),
        create_point(extent[1], extent[3]),
        create_point(extent[1], extent[2]),
        create_point(extent[0], extent[2]),
        create_point(extent[0], extent[3])
    ]
    
    # Get SRS for the output
    if not epsg:
        from gasp.cpu.gdl.mng.prj import get_shp_sref
        srs = get_shp_sref(inShp)
    
    else:
        from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
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


def shpextent_to_raster(inShp, outRaster, cellsize=None, epsg=None,
                        invalidResultAsNone=None):
    """
    Extent to raster
    
    if invalidResultAsNone - if for some reason something went wrong, the 
    result of this method will be a None Object if there is an error on the
    numpy array creation. If False, an error will be raised.
    """
    
    import os
    import numpy
    from osgeo         import gdal
    from gasp.prop.ff  import drv_name
    from gasp.prop.ext import get_extent
        
    cellsize = 10 if not cellsize else cellsize
    
    # Get extent
    try:
        left, right, bottom, top = get_extent(inShp, gisApi='ogr')
    except:
        left, right, bottom, top = inShp.GetEnvelope()
    
    # Get row and cols number
    rows = (float(top) - float(bottom)) / cellsize
    cols = (float(right) - float(left)) / cellsize
    
    rows = int(rows) if rows == int(rows) else int(rows) + 1
    cols = int(cols) if cols == int(cols) else int(cols) + 1
    
    if not invalidResultAsNone:
        NEW_RASTER_ARRAY = numpy.zeros((rows, cols))
    else:
        try:
            NEW_RASTER_ARRAY = numpy.zeros((rows, cols))
        except:
            return None
        
    # Create new raster
    img = gdal.GetDriverByName(
        drv_name(outRaster)).Create(
            outRaster, cols, rows, 1, gdal.GDT_Int16
        )
    
    img.SetGeoTransform((left, cellsize, 0, top, 0, -cellsize))
    
    band = img.GetRasterBand(1)
    
    band.WriteArray(NEW_RASTER_ARRAY)
    
    if epsg:
        from osgeo import osr
        
        rstSrs = osr.SpatialReference()
        rstSrs.ImportFromEPSG(epsg)
        img.SetProjection(rstSrs.ExportToWkt())
    
    band.FlushCache()
    
    return outRaster


def geomext_to_rst_wShapeCheck(inGeom, maxCellNumber, desiredCellsizes, outRst,
                             inEPSG):
    """
    Convert one Geometry to Raster using the cellsizes included
    in desiredCellsizes. For each cellsize, check if the number of cells
    exceeds maxCellNumber. The raster with lower cellsize but lower than
    maxCellNumber will be the returned raster
    """
    
    import os
    from gasp import goToList
    
    desiredCellsizes = goToList(desiredCellsizes)
    if not desiredCellsizes:
        raise ValueError(
            'desiredCellsizes does not have a valid value'
        )
    
    # Get geom extent
    left, right, bottom, top = inGeom.GetEnvelope()
    
    # Check Rasters Shape for each desired cellsize
    SEL_CELLSIZE = None
    for cellsize in desiredCellsizes:
        # Get Row and Columns Number
        NROWS = int(round((top - bottom) / cellsize, 0))
        NCOLS = int(round((right - left) / cellsize, 0))
        
        NCELLS = NROWS * NCOLS
        
        if NCELLS <= maxCellNumber:
            SEL_CELLSIZE = cellsize
            break
    
    if not SEL_CELLSIZE:
        return None
    
    else:
        shpextent_to_raster(
            inGeom, outRst, SEL_CELLSIZE, epsg=inEPSG,
            invalidResultAsNone=True
        )
        
        return outRst


def points_to_boundary(pntShp, outBound, distMeters):
    """
    Create a boundary from Point using a tolerance in meters
    """
    
    from osgeo                import ogr
    from gasp.oss             import get_filename
    from gasp.prop.ff         import drv_name
    from gasp.cpu.gdl         import create_point
    from gasp.cpu.gdl.mng.prj import get_shp_sref
    
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
            create_point(X - distMeters, Y + distMeters), # Topleft
            create_point(X + distMeters, Y + distMeters), # TopRight
            create_point(X + distMeters, Y - distMeters), # Lower Right
            create_point(X - distMeters, Y - distMeters), # Lower Left
            create_point(X - distMeters, Y + distMeters)
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

