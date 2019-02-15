# -*- coding: utf-8 -*-
from __future__ import unicode_literals


"""
Get Raster properties
"""

def get_nodata(r, gisApi='gdal'):
    """
    Returns the value defining NoData in a Raster file
    
    API'S Available:
    * gdal;
    * arcpy;
    """
    
    if gisApi == 'gdal':
        from osgeo import gdal
        
        img = gdal.Open(r)
        band = img.GetRasterBand(1)
        
        ndVal = band.GetNoDataValue()
    
    elif gisApi == 'arcpy':
        import arcpy
        
        desc = arcpy.Describe(r)
        
        ndVal = desc.noDataValue
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))
    
    return ndVal


def rst_shape(rst, gisApi='gdal'):
    """
    Return number of lines and columns in a raster
    
    API'S Available:
    * gdal;
    * arcpy;
    """
    
    from gasp import goToList
    
    rst    = goToList(rst)
    shapes = {}
    
    if gisApi == 'arcpy':
        import arcpy
        
        for r in rst:
            describe = arcpy.Describe(rst)
            
            shapes[r] = [describe.Height, describe.Width]
    
    elif gisApi == 'gdal':
        from gasp.fm.rst import rst_to_array
        
        for r in rst:
            array = rst_to_array(r)
            lnh, cols = array.shape
            
            shapes[r] = [lnh, cols]
            
            del array
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))
    
    return shapes if len(rst) > 1 else shapes[rst[0]]


def rst_distinct(rst, gisApi='gdal'):
    """
    Export a list with the values of a raster
    
    API'S Available:
    * gdal;
    * arcpy;
    """
    
    import numpy
    
    if gisApi == 'gdal':
        from gasp.fm.rst import rst_to_array
    
    elif gisApi == 'arcpy':
        from gasp.fm.rst import toarray_varcmap as rst_to_array
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))
    
    v = numpy.unique(rst_to_array(rst, flatten=True, with_nodata=False))
    
    return list(v)


def rst_dataType(rsts):
    """
    Get Raster dataType
    
    Only Available for GDAL
    """
    
    from osgeo import gdal
    
    dataTypes = {
        'Byte'    : gdal.GDT_Byte,
        'Int16'   : gdal.GDT_Int16,
        'UInt16'  : gdal.GDT_UInt16,
        'Int32'   : gdal.GDT_Int32,
        'UInt32'  : gdal.GDT_UInt32,
        'Float32' : gdal.GDT_Float32,
        'Float64' : gdal.GDT_Float64
    }
    
    rsts = rsts if type(rsts) == list else rst.keys() if \
        type(rsts) == dict else [rsts]
    
    types = []
    for rst in rsts:
        if type(rst) == gdal.Band:
            band = rst
        else:
            src  = gdal.Open(rst)
            band = src.GetRasterBand(1)
    
        dataType = gdal.GetDataTypeName(band.DataType)
        
        types.append(dataTypes[dataType])
        
        src  = None
        band = None
    
    if len(types) == 1:
        return types[0]
    
    else:
        return types


def get_cellsize(rst, xy=False, bnd=None, gisApi='gdal'):
    """
    Return cellsize of one or more Raster Datasets
    
    In the case of groups, the result will be:
    d = {
        'path_to_raster1': cellsize_raster_1,
        'path_to_raster2': cellsize_raster_2,
        'path_to_raster3': cellsize_raster_3,
        ...,
        'path_to_rastern': cellsize_raster_n,
    }
    
    API'S Available:
    * gdal;
    * arcpy;
    """
    
    import os
    
    if gisApi == 'gdal':
        from osgeo import gdal
        
        def __get_cellsize(__rst):
            img = gdal.Open(__rst)
            (upper_left_x, x_size, x_rotation,
             upper_left_y, y_rotation, y_size) = img.GetGeoTransform()
        
            return int(x_size), int(y_size)
        
        def __loop(files, __xy):
            return {f : __get_cellsize(f) for f in files} if __xy \
                else {f : __get_cellsize(f)[0] for f in files}
        
        if os.path.exists(rst):
            if os.path.isfile(rst):
                xs, ys = __get_cellsize(rst)
                
                if not xy:
                    return xs
                
                else:
                    return [xs, xy]
            
            elif os.path.isdir(rst):
                from gasp.oss import list_files
                
                rsts = list_files(rst, file_format=gdal_drivers().keys())
                
                return __loop(rsts, xy)
            
            else:
                raise ValueError('The path exists but is not a file or dir')
        
        else:
            if type(rst) == list:
                return __loop(rst, xy)
            
            else:
                raise ValueError((
                    'Invalid object rst. Please insert a path to a raster, '
                    'a path to a directory with rasters or a list with '
                    'rasters path.'
                ))
    
    elif gisApi == 'arcpy':
        import arcpy
        from gasp.cpu.arcg.lyr import rst_lyr, checkIfRstIsLayer
        
        def _get_cell_arc(_r):
            # Check if r is a Raster Layer
            isRaster = checkIfRstIsLayer(_r)
            
            lyr = rst_lyr(_r) if not isRaster else _r
            
            cellsizeX = arcpy.GetRasterProperties_management(
                lyr, "CELLSIZEX", "" if not bnd else bnd
            )
                
            cellsizeY = arcpy.GetRasterProperties_management(
                lyr, "CELLSIZEY", "" if not bnd else bnd
            )
            
            if xy:
                if str(cellsizeY) != str(cellsizeX):
                    raise ValueError((
                        'Cellsize is not the same in both dimensions (x, y)'
                    ))
            
                else:
                    return int(str(cellsizeX))
            
            else:
                return int(str(cellsizeX)), int(str(cellsizeY))
        
        def get_cellsize2(rst):
            describe = arcpy.Describe(rst)
    
            return describe.MeanCellWidth, describe.MeanCellHeight
        
        def _loop(files):
            return {f : _get_cell_arc(f) for f in files}
        
        if os.path.exists(rst):
            if os.path.isfile(rst):
                CELLSIZE = _get_cell_arc(rst)
                
                return CELLSIZE
            
            elif os.path.isdir(rst):
                from gasp.oss import list_files
                
                rsts = list_files(rst)
                
                return _loop(rsts)
            
            else:
                raise ValueError('The path exists but is not a file or dir')
        
        else:
            if type(rst) == list:
                return _loop(rst)
            
            else:
                raise ValueError((
                    'Invalid object rst. Please insert a path to a raster, '
                    'a path to a directory with rasters or a list with '
                    'rasters path.'
                ))
    
    elif gisApi == 'qgis':
        from qgis.core import QgsRasterLayer
        
        rasterLyr = QgsRasterLayer(rst, "lyr")
        x = rasterLyr.rasterUnitsPerPixelX()
        
        if xy:
            y = rasterLyr.rasterUnitsPerPixelY()
            
            return x, y
        else:
            return x
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))


def count_cells(raster, countNodata=None):
    """
    Return number of cells in a Raster Dataset
    """
    
    from gasp.fm.rst import rst_to_array
    from gasp.num    import count_where
    
    a = rst_to_array(raster)
    
    lnh, col = a.shape
    nrcell   = lnh * col
    
    if countNodata:
        return nrcell
    
    else:
        NoDataValue = get_nodata(raster)
        NrNodata = count_where(a, a == NoDataValue)
        return nrcell - NrNodata


"""
Cells Positions and Values
"""

def get_cell_value(rstLyr, x, y, xmin, ymin, cellwidth, cellheight):
    """
    Return the cell value in a raster with the x, y coordinates
    """
    
    import arcpy
    
    px = int((x - xmin) / cellwidth)
    py = int((y - ymin) / cellheight)
    
    val = arcpy.RasterToNumPyArray(rst, ncols=py, nrows=px)
    
    return val


def get_cell_coord(line, column, xmin, ymax, cellwidth, cellheight):
    """
    Return x, y coordinates of one cell in a raster
    
    This method needs x, y of the top left corner because a numpy array
    have indexes that increses from left to right and from top to bottom
    """
    
    x = xmin + (column * cellwidth) + (cellwidth / 2)
    
    y = ymax - ( line * cellheight) - (cellheight / 2)
    
    return x, y


"""
Raster Statistics
"""

def rst_stats(rst, bnd=None, api='gdal'):
    """
    Get Raster Statistics
    
    The output will be a dict with the following keys:
    * Min - Minimum
    * Max - Maximum
    * Mean - Mean value
    * StdDev - Standard Deviation
    
    API's Available:
    * arcpy;
    * gdal;
    """
    
    if api == 'gdal':
        """
        Using GDAL, it will be very simple
        """
        
        from osgeo import gdal
        
        r = gdal.Open(rst)
        
        bnd = r.GetRasterBand(1 if not bnd else bnd)
        stats = bnd.GetStatistics(True, True)
        
        dicStats = {
            'MIN' : stats[0], 'MAX' : stats[1], 'MEAN' : stats[2],
            "STDEV" : stats[3]
        }
    
    elif api == 'arcpy':
        """
        Do it with Arcpy
        """
        
        import arcpy
        from gasp.cpu.arcg.lyr import rst_lyr
        
        lyr = rst_lyr(rst)
        
        dicStats = {
            'MIN'  : 'MINIMUM', 'MAX'   : 'MAXIMUM',
            'MEAN' :    'MEAN', "STDEV" : "STD"
        }
        
        for s in d:
            stat = round(float(str(arcpy.GetRasterProperties_management(
                lyr, s, "layer_1" if not bnd else bnd
            )).replace(',', '.')), 4)
            
            dicStats[s] = stat
        
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return dicStats