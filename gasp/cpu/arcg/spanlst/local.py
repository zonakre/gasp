import arcpy


def Combine(inRst, outRst, template=None):
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    arcpy.gp.Combine_sa(";".join(inRst), outRst)
    if template:
        arcpy.env.extent = tempEnvironment0
    
    return outRst

