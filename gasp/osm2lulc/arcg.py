"""
OSM2LULC using ArcMap
"""


def osm2lulc_vector(osmdata, refBoundary, nomenclature, lulcShp, epsg=3857):
    """
    Convert OSM Data into Land Use/Land Cover Information
    
    An vector based approach.
    
    TODO: Add a detailed description.
    """
    
    # ************************************************************************ #
    # Python Modules from Reference Packages #
    # ************************************************************************ #
    import os
    import pandas
    
    # ************************************************************************ #
    # GASP dependencies #
    # ************************************************************************ #
    from gasp.oss                 import get_filename
    from gasp.cpu.arcg.anls.exct  import clip
    from gasp.cpu.arcg.anls.ovlay import erase
    from gasp.cpu.arcg.mng.fld    import calc_fld, add_geom_attr
    from gasp.cpu.arcg.mng.gen    import merge
    from gasp.mng.prj             import project
    from gasp.cpu.arcg.mng.wspace import create_featdts
    from gasp.osm2lulc.mod1       import arcg_selection
    from gasp.osm2lulc.mod2       import arc_roadsrule
    from gasp.osm2lulc.m3_4       import arcg_area
    from gasp.osm2lulc.mod5       import arcg_buffering
    from gasp.osm2lulc.mod6       import arc_pnt_to_build
    
    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    from gasp.osm2lulc.var import osmTableData, PRIORITIES
    
    # ************************************************************************ #
    # Convert OSM file to Feature Classes #
    # ************************************************************************ #
    if type(osmdata) == list or type(osmdata) == tuple:
        osm_geodb, featDataset, osm_feat_cls = osmdata
    
    else:
        from gasp.to.shp.arcg import osm_to_featurecls
        osm_geodb, featDataset, osm_feat_cls = osm_to_featurecls(
            osmdata, os.path.join(os.path.dirname(lulcShp), "gdb_" + get_filename(osmdata))
        )
    
    # ************************************************************************ #
    # Create a new Feature Dataset and Re-project osm features classes #
    # ************************************************************************ #
    envFeatDataset = create_featdts(osm_geodb, 'osmtolulc', epsg)
    
    for ot in osm_feat_cls:
        osm_feat_cls[ot] = project(
            os.path.join(osm_geodb, featDataset, osm_feat_cls[ot]),
            os.path.join(envFeatDataset, "osm_{}".format(ot.lower())),
            epsg
        )
        
        osm_feat_cls[ot] = clip(
            osm_feat_cls[ot], refBoundary, os.path.join(
                envFeatDataset, "osm_clp_{}".format(ot)
            )
            #osm_feat_cls[ot], refBoundary, "in_memory/osm_clp_{}".format(ot)
        )
        
        if ot == "POLYGONS":
            add_geom_attr(osm_feat_cls[ot], "shp_area", geom_attr="AREA")
    
    # ************************************************************************ #
    # OSM2LULC Data Processing #
    # ************************************************************************ #
    mergeOut = {}
    # ************************************************************************ #
    # 1 - Selection Rule #
    # ************************************************************************ #
    """
    selOut = {cls_code : shp_path, ...}
    """
    selOut = arcg_selection(nomenclature, osm_feat_cls["POLYGONS"])
    
    for cls in selOut:
        mergeOut[cls] = [selOut[cls]]
    
    # ************************************************************************ #
    # 2 - Get Information About Roads Location #
    # ************************************************************************ #
    """
    roads = {cls_code : shp_path, ...}
    """
    roads = arc_roadsrule(
        osm_feat_cls["LINES"], osm_feat_cls["POLYGONS"], nomenclature
    )
    
    for cls in roads:
        if cls not in mergeOut:
            mergeOut[cls] = roads[cls]
        
        else:
            mergeOut[cls] += roads[cls]
    
    # ************************************************************************ #
    # 3 - Area Upper than #
    # ************************************************************************ #
    """
    auOut = {cls_code : shp_path, ...}
    """
    auOut = arcg_area(osm_feat_cls["POLYGONS"], nomenclature, UPPER=True)
    
    for cls in auOut:
        if cls not in mergeOut:
            mergeOut[cls] = [auOut[cls]]
        
        else:
            mergeOut[cls].append(auOut[cls])
    
    # ************************************************************************ #
    # 4 - Area Lower than #
    # ************************************************************************ #
    """
    alOut = {cls_code : shp_path, ...}
    """
    alOut = arcg_area(osm_feat_cls["POLYGONS"], nomenclature, UPPER=None)
    
    for cls in alOut:
        if cls not in mergeOut:
            mergeOut[cls] = [alOut[cls]]
        
        else:
            mergeOut[cls].append(alOut[cls])
    
    # ************************************************************************ #
    # 5 - Get data from lines table (railway | waterway) #
    # ************************************************************************ #
    """
    alOut = {cls_code : [shp_path, ...], ...}
    """
    bfOut = arcg_buffering(osm_feat_cls["LINES"], nomenclature)
    
    for cls in bfOut:
        if cls not in mergeOut:
            mergeOut[cls] = bfOut[cls]
        
        else:
            mergeOut[cls] += bfOut[cls]
    
    # ************************************************************************ #
    # 7 - Assign untagged Buildings to tags #
    # ************************************************************************ #
    if nomenclature != "GLOBE_LAND_30":
        buildsOut = arc_pnt_to_build(
            nomenclature, osm_feat_cls["POINTS"], osm_feat_cls["POLYGONS"])
        
        for cls in buildsOut:
            if cls not in mergeOut:
                mergeOut[cls] = [buildsOut[cls]]
            else:
                mergeOut[cls].append(buildsOut[cls])
    
    # ************************************************************************ #
    # Produce LULC Map  #
    # ************************************************************************ #
    """
    Merge all results for one cls into one single feature class
    """
    for cls in mergeOut:
        if len(mergeOut[cls]) == 1:
            mergeOut[cls] = mergeOut[cls][0]
        
        else:
            mergeOut[cls] = merge(
                mergeOut[cls], os.path.join(envFeatDataset, "merge_{}".format(cls))
            )
    
    """
    Apply Priorites Rule
    """
    __p = PRIORITIES[nomenclature]
    for i in range(len(__p)):
        if __p[i] not in mergeOut:
            continue
        
        else:
            for e in range(i+1, len(__p)):
                if __p[e] not in mergeOut:
                    continue
                
                else:
                    mergeOut[__p[e]] = erase(
                        mergeOut[__p[e]], mergeOut[__p[i]],
                        os.path.join(envFeatDataset, "{}_{}".format(
                            os.path.basename(mergeOut[__p[e]]), str(e)
                        ))
                    )
    
    """
    Merge all lulc Classes
    """
    for cls in mergeOut:
        calc_fld(
            mergeOut[cls], "lulc_cls", "\"{}\"".format(str(cls)),
            isNewField={"TYPE" : "TEXT", "LENGTH" : "5", "PRECISION" : ""}
        )
    
    _lulcShp = merge([mergeOut[k] for k in mergeOut], lulcShp)
    
    return _lulcShp


def osm2lulc_v2(osmdata, nomenclature, refPrj, refBoundary, lulcShp, dataStore=None):
    """
    Convert OSM Data into Land Use/Land Cover Information
    
    An vector based approach using a interoperable strategie.
    
    TODO: Add a detailed description.
    """
    
    # ************************************************************************ #
    # Python Modules from Reference Packages #
    # ************************************************************************ #
    import os; import datetime
    # ************************************************************************ #
    # GASP dependencies #
    # ************************************************************************ #
    from gasp.oss.ops  import create_folder
    from gasp.osm2lulc import osm_to_sqdb, osm_project, add_lulc_to_osmfeat
    
    from gasp.osm2lulc.rule1 import arcg_selection
    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    from gasp.osm2lulc.var import osmTableData, PRIORITIES
    
    workspace = os.path.join(os.path.dirname(
        lulcShp), 'osmtolulc') if not dataStore else dataStore
    
    # Check if workspace exists
    if os.path.exists(workspace):
        if overwrite:
            create_folder(workspace)
        else:
            raise ValueError('Path {} already exists'.format(workspace))
    else:
        create_folder(workspace)
    
    __priorities = PRIORITIES[nomenclature]
    # ************************************************************************ #
    # Convert OSM file to SQLITE DB #
    # ************************************************************************ #
    osm_db = osm_to_sqdb(osmdata, os.path.join(workspace, 'osm.sqlite'))
    # ************************************************************************ #
    # Add Lulc Classes to OSM_FEATURES by rule #
    # ************************************************************************ #
    add_lulc_to_osmfeat(osm_db, osmTableData, nomenclature)
    # ************************************************************************ #
    # Transform SRS of OSM Data #
    # ************************************************************************ #
    osmTableData = osm_project(osm_db, epsg)
    
    # ************************************************************************ #
    # MapResults #
    # ************************************************************************ #
    OSM_SHPS = {}
    
    # ************************************************************************ #
    # 1 - Selection Rule #
    # ************************************************************************ #
    ruleOne, timeCheck1 = arcg_selection(
        osm_db, osmTableData['polygons'], workspace)
    
    for cls in ruleOne: OSM_SHPS[cls] = [ruleOne[cls]]
    # ************************************************************************ #
    # 2 - Get Information About Roads Location #
    # ************************************************************************ #