# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
File Format Properties
"""

def vector_formats():
    return [
        '.shp'
    ]


def raster_formats():
    return [
        '.tiff', '.tif', '.img', '.nc', 'ecw', '.jpg'
    ]


def check_isRaster(_file):
    from gasp.oss import get_fileformat

    rst_lst = raster_formats()
    
    file_ext = get_fileformat(_file)
    
    if file_ext not in rst_lst:
        return None
    else:
        return True


"""
GDAL Drivers Name
"""

def drv_name(_file):
    """
    Return the driver for a given file format
    """
    
    import os
    
    drv = {
        # Vector files
        '.gml'    : 'GML',
        '.shp'    : 'ESRI Shapefile',
        '.json'   : 'GeoJSON',
        '.kml'    : 'KML',
        '.osm'    : 'OSM',
        '.dbf'    : 'ESRI Shapefile',
        '.vct'    : 'Idrisi',
        '.nc'     : 'netCDF',
        '.vrt'    : 'VRT',
        '.mem'    : 'MEMORY',
        '.sqlite' : 'SQLite',
        '.gdb'    : 'FileGDB',
        # Raster files
        '.tif'    : 'GTiff',
        '.ecw'    : 'ECW',
        '.mpr'    : 'ILWIS',
        '.mpl'    : 'ILWIS',
        '.jpg'    : 'JPEG',
        '.nc'     : 'netCDF',
        '.png'    : 'PNG',
        '.vrt'    : 'VRT'
    }
    name, ext = os.path.splitext(_file)
    return str(drv[ext])


"""
GRASS GIS Drivers
"""

def VectorialDrivers():
    return {
        '.shp' : 'ESRI_Shapefile',
        '.gml' : 'GML'
    }


def RasterDrivers():
    return {
        '.tif': 'GTiff',
        '.img': 'HFA'
    }

