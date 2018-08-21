"""
Surface tools for SAGA GIS
"""

from gasp import exec_cmd

def viewshed(demrst, obsShp, output):
    """
    This tool computes a visibility analysis using observer points from
    a point shapefile.
    """
    
    import os
    from gasp.oss         import get_filename
    from gasp.to.rst.saga import saga_to_geotiff
    
    SAGA_RASTER = os.path.join(
        os.path.dirname(output),
        "sg_{}.sgrd".format(get_filename(output))
    )
    
    cmd = (
       "saga_cmd ta_lighting 6 -ELEVATION {elv} -POINTS {pnt} "
       "-VISIBILITY {out} -METHOD 0"
    ).format(
        elv=demrst, pnt=obsShp, out=SAGA_RASTER
    )
    
    outcmd = exec_cmd(cmd)
    
    # Convert to Tiif
    saga_to_geotiff(SAGA_RASTER, output)
    
    return output

