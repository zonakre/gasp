"""
ArcGIS tools from Analysis Tools > Overlay
"""

import arcpy


def union(lst, out):
    arcpy.Union_analysis(";".join(lst), out, "ALL", "", "GAPS")
    return out


def geom_contains(containerGeom, otherGeom):
    return containerGeom.contains(otherGeom)


def geom_intersect(geometry, intersectGeom, dimension):
    return geometry.intersect(intersectGeom, dimension)


def intersect(lst_lyr, outShp):
    arcpy.Intersect_analysis(lst_lyr, outShp)
    return outShp


def folderShp_Intersection(inFolder, intFeatures, outFolder):
    """
    Intersect all feature classes in a folder with the feature classes
    listed in the argument intFeatures (path to the file).
    """
    
    import os
    
    from gasp.cpu.arcg.lyr import feat_lyr
    from gasp.oss.ops      import create_folder
    
    # Environment
    arcpy.env.overwriteOutput = True
    # Workspace
    arcpy.env.workspace = inFolder
    
    if type(intFeatures) != list:
        intFeatures = [intFeatures]
    
    if not os.path.exists(outFolder):
        create_folder(outFolder)
    
    # List feature classes in inFolder
    fc_infld = arcpy.ListFeatureClasses()
    
    # Create Layer objects
    lyr_infld = [feat_lyr(os.path.join(inFolder, str(fc))) for fc in fc_infld]
    lyr_intFeat = [feat_lyr(fc) for fc in intFeatures]
    
    # Intersect things
    for i in range(len(lyr_infld)):
        intersect(
            [lyr_infld[i]] + lyr_intFeat,
            os.path.join(outFolder, os.path.basename(str(fc_infld[i])))
        )


def erase(inFeat, eraseFeat, outFeat):
    """
    Run erase tool
    """
    
    arcpy.Erase_analysis(
        in_features=inFeat, erase_features=eraseFeat, 
        out_feature_class=outFeat
    )
    
    return outFeat

