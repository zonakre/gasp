"""
GIS API's subpackage:

Python GDAL Tools.
"""


"""
In this file, we have:
Basic and generic tools using GDAL/OGR Library
"""

import os
import shutil
from osgeo import gdal
from osgeo import ogr
from osgeo import osr


"""
OGR tools
"""
"""
Geometry Attributes
"""

def get_centroid_boundary(shp, isFile=None):
    """
    Return centroid (OGR Point object) of a Boundary (layer with a single
    feature).
    """
    
    if isFile:
        shp = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0)
    
        lyr = shp.GetLayer()
    
        feat = lyr[0]; geom = feat.GetGeometryRef()
    
    else:
        geom = shp
    
    centroid = geom.Centroid()
    
    cnt = ogr.CreateGeometryFromWkt(centroid.ExportToWkt())
    
    shp.Destroy()
    
    return cnt


def area_to_dic(shp):
    """
    Return the following output:
    
    dic = {
        id_feat: area,
        ...,
        id_feat: area
    }
    """
    
    o = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
    l = o.GetLayer()
    d = {}
    c = 0
    for feat in l:
        g = feat.GetGeometryRef()
        area = g.GetArea()
        d[c] = area
        c += 1
    del l
    o.Destroy()
    return d


"""Create Geometries"""
def create_point(x, y):
    """
    Return a OGR Point geometry object
    """
    
    pnt = ogr.Geometry(ogr.wkbPoint)
    pnt.AddPoint(float(x), float(y))
    
    return pnt


def create_polygon(points):
    """
    Return a OGR Polygon geometry object
    """
    
    ring = ogr.Geometry(ogr.wkbLinearRing)
    
    for pnt in points:
        ring.AddPoint(pnt.GetX(), pnt.GetY())
    
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    
    return polygon


"""
Get Geometries from file
"""

def get_geom_by_index(inShp, idx):
    """
    Get Geometry by index in file
    """
    
    src = ogr.GetDriverByName(drv_name(inShp)).Open(inShp)
    lyr = src.GetLayer()
    
    c = 0
    geom = None
    for f in lyr:
        if idx == c:
            geom = f.GetGeometryRef()
        
        else:
            c += 1
    
    if not geom:
        raise ValueError("inShp has not idx")
    
    _geom = geom.ExportToWkt()
    
    del lyr
    src.Destroy()
    
    return _geom

