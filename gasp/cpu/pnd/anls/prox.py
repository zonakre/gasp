"""
Proximity tools
"""


def gp_buffer(gseries, dist):
    """
    Buffer of GeoSeries
    """
    
    return gseries.buffer(dist, resolution=16)


def buffer_to_shp(geoDf, dist, outfile, colgeom='geometry'):
    """
    Execute the Buffer Function of GeoPandas and export
    the result to a new shp
    """
    
    from gasp.to.shp import df_to_shp
    
    __geoDf = geoDf.copy()
    __geoDf["buffer_geom"] = __geoDf[colgeom].buffer(dist, resolution=16)
    
    __geoDf.drop(colgeom, axis=1, inplace=True)
    __geoDf.rename(columns={"buffer_geom" : colgeom}, inplace=True)
    
    df_to_shp(__geoDf, outfile)
    
    return outfile

def _buffer(inShp, radius, outShp):
    """
    Buffering on Shapefile
    """
    
    from gasp.fm.shp import shp_to_df
    
    geoDf_ = shp_to_df(inShp)
    
    return buffer_to_shp(geoDf_, radius, outShp)

