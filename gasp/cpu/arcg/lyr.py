"""
Deal with Layer Objects
"""

import arcpy

""" *********** Feature Classes *********** """
def feat_lyr(s, name=None):
    """
    Create a layer from a feature class data source
    """
    
    import os
    from gasp.oss import get_filename
    
    lyr = arcpy.MakeFeatureLayer_management(
        s, name if name else get_filename(s),
        "", "", ""
    )
    
    return lyr

""" *********** Raster Datasets *********** """
def rst_lyr(r):
    import os
    
    lyr = arcpy.MakeRasterLayer_management(
        r,
        os.path.splitext(os.path.basename(r))[0],
        "", "", "1"
    )
    return lyr

def checkIfRstIsLayer(obj):
    """
    Check if an object is a Raster Layer
    """
    
    dataType = arcpy.Describe(obj)
    
    return True if dataType == u'RasterLayer' else None
