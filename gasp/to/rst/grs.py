"""
GRASS Methods to convert to Raster
"""


def rst_to_grs(rst, grsRst, as_cmd=None):
    """
    Raster to GRASS GIS Raster
    """
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "r.in.gdal", input=rst, output=grsRst, flags='o',
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "r.in.gdal input={} output={} -o --overwrite "
            "--quiet"
        ).format(rst, grsRst))
    
    return grsRst


def grs_to_rst(grsRst, rst, as_cmd=None, allBands=None):
    """
    GRASS Raster to Raster
    """
    
    from gasp.cpu.grs import RasterDrivers
    from gasp.oss     import get_fileformat
    
    rstDrv = RasterDrivers()
    rstExt = get_fileformat(rst)
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "r.out.gdal", input=grsRst, output=rst,
            format=rstDrv[rstExt], flags='c' if not allBands else '',
            createopt="INTERLEAVE=PIXEL,TFW=YES" if allBands else '',
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "r.out.gdal input={} output={} format={} "
            "{} --overwrite --quiet"
        ).format(
            grsRst, rst, rstDrv[rstExt],
            "-c" if not allBands else "createopt=\"INTERLEAVE=PIXEL,TFW=YES\""
        ))
    
    return rst


def shp_to_raster(shp, rst, source, as_cmd=None):
    """
    Vectorial geometry to raster
    
    If source is None, the convertion will be based on the cat field.
    
    If source is a string, the convertion will be based on the field
    with a name equal to the given string.
    
    If source is a numeric value, all cells of the output raster will have
    that same value.
    """
    
    __USE = "cat" if not source else "attr" if type(source) == str or \
        type(source) == unicode else "val" if type(source) == int or \
        type(source) == float else None
    
    if not __USE:
        raise ValueError('\'source\' parameter value is not valid')
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "v.to.rast", input=shp, output=rst, use=__USE,
            attribute_column=source if __USE == "attr" else None,
            value=source if __USE == "val" else None,
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.to.rast input={} output={} use={}{} "
            "--overwrite --quiet"
        ).format(
            shp, rst, __USE,
            "" if __USE == "cat" else " attribute_column={}".format(source) \
                if __USE == "attr" else " val={}".format(source)
        ))
    
    return rst

