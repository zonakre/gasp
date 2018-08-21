"""
Raster tools - GRASS GIS

GRASS GIS Tools translated to Python
"""

from grass.pygrass.modules import Module


def slope(m, s):
    sl = Module(
        "r.slope.aspect", elevation=m, slope=s, format='percent',
        overwrite=True, precision="FCELL", run_=False, quiet=True
    )
    
    sl()
    
    return s


def viewshed(dem, obsPnt, outRst):
    """
    Compute viewshed
    """
    
    vshd = Module(
        "r.viewshed", input=dem, output=outRst, coordinates="east,north",
        flags="b", overwrite=True, run_=False, quiet=True
    )
    
    vshd()
    
    return outRst


def vidw(inShp, col, outdem, nrPnt=None, _power=None):
    """
    v.surf.idw - Provides surface interpolation from vector point data by
    Inverse Distance Squared Weighting.
    
    v.surf.idw fills a raster matrix with interpolated values generated from
    a set of irregularly spaced vector data points using numerical approximation
    (weighted averaging) techniques. The interpolated value of a cell is
    determined by values of nearby data points and the distance of the cell
    from those input points. In comparison with other methods, numerical
    approximation allows representation of more complex surfaces (particularly
    those with anomalous features), restricts the spatial influence of any
    errors, and generates the interpolated surface from the data points.
    
    Values to interpolate are read from column option. If this option is not
    given than the program uses categories as values to interpolate or
    z-coordinates if the input vector map is 3D.
    """
    
    nrPnt  = 12 if not nrPnt else nrPnt
    _power = 2.0 if not _power else _power
    
    idw = Module(
        "v.surf.idw", input=inShp, column=col, output=outdem,
        npoints=nrPnt, power=_power,
        run_=False, quiet=True, overwrite=True
    )
    
    idw()

def ridw(inRst, outRst, numberPoints=None):
    """
    r.surf.idw - Provides surface interpolation from raster point data
    by Inverse Distance Squared Weighting.
    
    r.surf.idw fills a grid cell (raster) matrix with interpolated values
    generated from input raster data points. It uses a numerical approximation
    technique based on distance squared weighting of the values of nearest data
    points. The number of nearest data points used to determined the
    interpolated value of a cell can be specified by the user (default:
    12 nearest data points).
    
    If there is a current working mask, it applies to the output raster map.
    Only those cells falling within the mask will be assigned interpolated
    values. The search procedure for the selection of nearest neighboring
    points will consider all input data, without regard to the mask.
    The -e flag is the error analysis option that interpolates values
    only for those cells of the input raster map which have non-zero
    values and outputs the difference (see NOTES below).
    
    The npoints parameter defines the number of nearest data points used to
    determine the interpolated value of an output raster cell.
    """
    
    numberPoints = 12 if not numberPoints else numberPoints
    
    idw = Module(
        'r.surf.idw', input=inRst, output=outRst, npoints=numberPoints,
        run_=False, quiet=True, overwrite=True
    )
    
    idw()

