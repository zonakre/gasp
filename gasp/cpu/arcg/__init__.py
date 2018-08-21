"""
GIS API's subpackage:

Tools from ArcGIS converted to Python.
"""


"""
In this file, we have
Basic functions needed to put ArcGIS regular functions working
"""


import arcpy

"""
Feature datasets
"""

def get_geom_field(lyr):
    return arcpy.Describe(lyr).shapeFieldName


def get_feat_area(instance, shapeFld):
    return float(instance.getValue(shapeFld).area)


def get_geom_type(fc):
    """
    Return GEOMETRY TYPE of one feature class
    """
    
    return arcpy.Describe(fc).ShapeType
