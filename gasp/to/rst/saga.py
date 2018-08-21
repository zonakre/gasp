"""
Import and Export data from SAGA GIS
"""


from gasp import exec_cmd


def saga_to_geotiff(inFile, outFile):
    """
    SAGA GIS format to GeoTIFF
    """
    
    import os
    
    # Check if outFile is a GeoTiff
    if os.path.splitext(outFile)[1] != '.tif':
        raise ValueError(
            'Outfile should have GeoTiff format'
        )
    
    cmd = (
        "saga_cmd io_gdal 2 -GRIDS {} "
        "-FILE {}"
    ).format(inFile, outFile)
    
    outcmd = exec_cmd(cmd)
    
    return outFile

