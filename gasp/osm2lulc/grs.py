"""
OpenStreetMap to Land Use/Land Cover Maps
"""

def raster_based(osmdata, nomenclature, refRaster, lulcRst,
           epsg=3857, overwrite=None, dataStore=None):
    """
    Convert OSM Data into Land Use/Land Cover Information
    
    An raster based approach.
    
    TODO: Add detailed description
    """
    
    # ************************************************************************ #
    # Python Modules from Reference Packages #
    # ************************************************************************ #
    import datetime; import os; import pandas
    # ************************************************************************ #
    # Gasp dependencies #
    # ************************************************************************ #
    from gasp.oss.ops        import create_folder
    from gasp.cpu.grs        import run_grass
    from gasp.osm2lulc.utils import osm_to_sqdb, osm_project
    from gasp.osm2lulc.utils import add_lulc_to_osmfeat
    from gasp.osm2lulc.mod1  import grs_rst
    from gasp.osm2lulc.mod2  import grs_rst_roads
    from gasp.osm2lulc.m3_4  import rst_area
    from gasp.osm2lulc.mod5  import basic_buffer
    from gasp.osm2lulc.mod6  import rst_pnt_to_build
    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    if not os.path.exists(os.path.dirname(lulcRst)):
        raise ValueError('{} does not exist!'.format(os.path.dirname(lulcRst)))
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    from gasp.osm2lulc.var import PRIORITIES, osmTableData
    
    workspace = os.path.join(os.path.dirname(
        lulcRst), 'osmtolulc') if not dataStore else dataStore
    
    # Check if workspace exists
    if os.path.exists(workspace):
        if overwrite:
            create_folder(workspace)
        else:
            raise ValueError('Path {} already exists'.format(workspace))
    else:
        create_folder(workspace)
    
    __priorites = PRIORITIES[nomenclature]
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Convert OSM file to SQLITE DB #
    # ************************************************************************ #
    osm_db = osm_to_sqdb(osmdata, os.path.join(workspace, 'osm.sqlite'))
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Add Lulc Classes to OSM_FEATURES by rule #
    # ************************************************************************ #
    add_lulc_to_osmfeat(osm_db, osmTableData, nomenclature)
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Transform SRS of OSM Data #
    # ************************************************************************ #
    osmTableData = osm_project(osm_db, epsg)
    time_e = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Start a GRASS GIS Session #
    # ************************************************************************ #
    grass_base = run_grass(
        workspace, grassBIN='grass74', location='grloc', srs=epsg)
    import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grass_base, workspace, 'grloc', 'PERMANENT')
    
    # ************************************************************************ #
    # IMPORT SOME GASP MODULES FOR GRASS GIS #
    # ************************************************************************ #
    from gasp.to.rst.grs      import rst_to_grs, grs_to_rst
    from gasp.cpu.grs.spanlst import mosaic_raster
    from gasp.cpu.grs.conf    import rst_to_region
    
    # ************************************************************************ #
    # SET GRASS GIS LOCATION EXTENT #
    # ************************************************************************ #
    extRst = rst_to_grs(refRaster, 'extent_raster')
    rst_to_region(extRst)
    time_f = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # MapResults #
    mergeOut = {}
    # ************************************************************************ #
    # ************************************************************************ #
    # 1 - Selection Rule #
    # ************************************************************************ #
    """
    selOut = {
        cls_code : rst_name, ...
    }
    """
    selOut, timeCheck1 = grs_rst(osm_db, osmTableData['polygons'])
    for cls in selOut:
        mergeOut[cls] = [selOut[cls]]
    
    time_g = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 2 - Get Information About Roads Location #
    # ************************************************************************ #
    """
    roads = {
        cls_code : rst_name, ...
    }
    """
    
    roads, timeCheck2 = grs_rst_roads(
        osm_db, osmTableData['lines'], osmTableData['polygons'],
        workspace, 1221 if nomenclature != "GLOBE_LAND_30" else 801
    )
    
    for cls in roads:
        if cls not in mergeOut:
            mergeOut[cls] = [roads[cls]]
        else:
            mergeOut[cls].append(roads[cls])
    
    time_h = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 3 - Area Upper than #
    # ************************************************************************ #
    """
    auOut = {
        cls_code : rst_name, ...
    }
    """
    
    auOut, timeCheck3 = rst_area(osm_db, osmTableData['polygons'], UPPER=True)
    for cls in auOut:
        if cls not in mergeOut:
            mergeOut[cls] = [auOut[cls]]
        else:
            mergeOut[cls].append(auOut[cls])
    
    time_l = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 4 - Area Lower than #
    # ************************************************************************ #
    """
    alOut = {
        cls_code : rst_name, ...
    }
    """
    
    alOut, timeCheck4 = rst_area(osm_db, osmTableData['polygons'], UPPER=None)
    for cls in alOut:
        if cls not in mergeOut:
            mergeOut[cls] = [alOut[cls]]
        else:
            mergeOut[cls].append(alOut[cls])
    
    time_j = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 5 - Get data from lines table (railway | waterway) #
    # ************************************************************************ #
    """
    bfOut = {
        cls_code : rst_name, ...
    }
    """
    
    bfOut, timeCheck5 = basic_buffer(
        osm_db, osmTableData['lines'], workspace
    )
    for cls in bfOut:
        if cls not in mergeOut:
            mergeOut[cls] = [bfOut[cls]]
        else:
            mergeOut[cls].append(bfOut[cls])
    
    time_m = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 7 - Assign untagged Buildings to tags #
    # ************************************************************************ #
    if nomenclature != "GLOBE_LAND_30":
        buildsOut, timeCheck7 = rst_pnt_to_build(
            osm_db, osmTableData['points'], osmTableData['polygons']
        )
        
        for cls in buildsOut:
            if cls not in mergeOut:
                mergeOut[cls] = buildsOut[cls]
            else:
                mergeOut[cls] += buildsOut[cls]
        
        time_n = datetime.datetime.now().replace(microsecond=0)
    
    else:
        timeCheck7 = None
        time_n = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Produce LULC Map  #
    # ************************************************************************ #
    """
    Merge all results for one cls into one raster
    mergeOut = {
        cls_code : [rst_name, rst_name, ...], ...
    }
    into
    mergeOut = {
        cls_code : patched_raster, ...
    }
    """
    
    for cls in mergeOut:
        if len(mergeOut[cls]) == 1:
            mergeOut[cls] = mergeOut[cls][0]
        
        else:
            mergeOut[cls] = mosaic_raster(
                mergeOut[cls], 'mosaic_{}'.format(str(cls)), asCmd=True
            )
    
    time_o = datetime.datetime.now().replace(microsecond=0)
    
    """
    Merge all Class Raster using a priority rule
    """
    
    __priorities = PRIORITIES[nomenclature]
    lst_rst = []
    for cls in __priorities:
        if cls not in mergeOut:
            continue
        else:
            lst_rst.append(mergeOut[cls])
    
    outGrs = mosaic_raster(
        lst_rst, os.path.splitext(os.path.basename(lulcRst))[0], asCmd=True
    )
    time_p = datetime.datetime.now().replace(microsecond=0)
    
    grs_to_rst(outGrs, lulcRst, as_cmd=True)
    time_q = datetime.datetime.now().replace(microsecond=0)
    
    return lulcRst, {
        0  : ('set_settings', time_b - time_a),
        1  : ('osm_to_sqdb', time_c - time_b),
        2  : ('cls_in_sqdb', time_d - time_c),
        3  : ('proj_data', time_e - time_d),
        4  : ('set_grass', time_f - time_e),
        5  : ('rule_1', time_g - time_f, timeCheck1),
        6  : ('rule_2', time_h - time_g, timeCheck2),
        7  : ('rule_3', time_l - time_h, timeCheck3),
        8  : ('rule_4', time_j - time_l, timeCheck4),
        9  : ('rule_5', time_m - time_j, timeCheck5),
        10 : None if not timeCheck7 else ('rule_7', time_n - time_m, timeCheck7),
        11 : ('merge_rst', time_o - time_n),
        12 : ('priority_rule', time_p - time_o),
        13 : ('export_rst', time_q - time_p)
    }

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #

def vector_based(osmdata, nomenclature, refRaster, lulcShp,
                 epsg=3857, overwrite=None, dataStore=None,
                 RoadsAPI='SQLITE'):
    """
    Convert OSM Data into Land Use/Land Cover Information
    
    An vector based approach.
    
    TODO: Add a detailed description.
    """
    
    # ************************************************************************ #
    # Python Modules from Reference Packages #
    # ************************************************************************ #
    import datetime; import os
    # ************************************************************************ #
    # GASP dependencies #
    # ************************************************************************ #
    from gasp.oss.ops           import create_folder
    from gasp.cpu.grs           import run_grass
    from gasp.osm2lulc.utils    import osm_to_sqdb, osm_project, add_lulc_to_osmfeat
    from gasp.cpu.pnd.mng.gen   import merge_shp
    from gasp.osm2lulc.mod1     import grs_vector
    if RoadsAPI == 'SQLITE':
        from gasp.osm2lulc.mod2 import roads_sqdb
    else:
        from gasp.osm2lulc.mod2 import grs_vec_roads
    from gasp.osm2lulc.m3_4     import grs_vect_selbyarea
    from gasp.osm2lulc.mod5     import grs_vect_bbuffer
    from gasp.osm2lulc.mod6     import vector_assign_pntags_to_build
    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    if not os.path.exists(os.path.dirname(lulcShp)):
        raise ValueError('{} does not exist!'.format(os.path.dirname(lulcShp)))
    
    time_a = datetime.datetime.now().replace(microsecond=0)
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
    time_b = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Convert OSM file to SQLITE DB #
    # ************************************************************************ #
    osm_db = osm_to_sqdb(osmdata, os.path.join(workspace, 'osm.sqlite'))
    time_c = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Add Lulc Classes to OSM_FEATURES by rule #
    # ************************************************************************ #
    add_lulc_to_osmfeat(osm_db, osmTableData, nomenclature)
    time_d = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Transform SRS of OSM Data #
    # ************************************************************************ #
    osmTableData = osm_project(osm_db, epsg)
    time_e = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Start a GRASS GIS Session #
    # ************************************************************************ #
    grass_base = run_grass(workspace, grassBIN='grass74', location='grloc', srs=epsg)
    #import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grass_base, workspace, 'grloc', 'PERMANENT')
    
    # ************************************************************************ #
    # IMPORT SOME GASP MODULES FOR GRASS GIS #
    # ************************************************************************ #
    from gasp.cpu.grs.anls.ovlay import erase
    from gasp.cpu.grs.conf       import rst_to_region
    from gasp.cpu.grs.mng.genze  import dissolve
    from gasp.cpu.grs.mng.tbl    import reset_table
    from gasp.to.shp.grs         import shp_to_grs, grs_to_shp
    from gasp.to.rst.grs         import rst_to_grs
    
    # ************************************************************************ #
    # SET GRASS GIS LOCATION EXTENT #
    # ************************************************************************ #
    extRst = rst_to_grs(refRaster, 'extent_raster')
    rst_to_region(extRst)
    time_f = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # MapResults #
    # ************************************************************************ #
    osmShps = []
    # ************************************************************************ #
    # 1 - Selection Rule #
    # ************************************************************************ #
    ruleOneShp, timeCheck1 = grs_vector(osm_db, osmTableData['polygons'])
    osmShps.append(ruleOneShp)
    
    time_g = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 2 - Get Information About Roads Location #
    # ************************************************************************ #
    ruleRowShp, timeCheck2 = roads_sqdb(
        osm_db, osmTableData['lines'], osmTableData['polygons']
    ) if RoadsAPI == 'SQLITE' else grs_vec_roads(
        osm_db, osmTableData['lines'], osmTableData['polygons'])
    
    osmShps.append(ruleRowShp)
    time_h = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 3 - Area Upper than #
    # ************************************************************************ #
    ruleThreeShp, timeCheck3 = grs_vect_selbyarea(
        osm_db, osmTableData['polygons'], UPPER=True)
    
    osmShps.append(ruleThreeShp)
    time_l = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 4 - Area Lower than #
    # ************************************************************************ #
    ruleFourShp, timeCheck4 = grs_vect_selbyarea(
        osm_db, osmTableData['polygons'], UPPER=False)
    
    osmShps.append(ruleFourShp)
    time_j = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 5 - Get data from lines table (railway | waterway) #
    # ************************************************************************ #
    ruleFiveShp, timeCheck5 = grs_vect_bbuffer(osm_db, osmTableData["lines"])
    
    osmShps.append(ruleFiveShp)
    time_m = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 7 - Assign untagged Buildings to tags #
    # ************************************************************************ #
    if nomenclature != "GLOBE_LAND_30":
        ruleSeven11, ruleSeven12, timeCheck7 = vector_assign_pntags_to_build(
            osm_db, osmTableData['points'], osmTableData['polygons']
        )
        
        if ruleSeven11:
            osmShps.append(ruleSeven11)
        
        if ruleSeven12:
            osmShps.append(ruleSeven12)
        
        time_n = datetime.datetime.now().replace(microsecond=0)
    
    else:
        timeCheck7 = None
        time_n = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Produce LULC Map  #
    # ************************************************************************ #
    """
    Get Shps with all geometries related with one class - One Shape for Classe
    """
    
    from gasp.cpu.pnd.mng import same_attr_to_shp
    
    _osmShps = []
    for i in range(len(osmShps)):
        if not osmShps[i]: continue
        
        _osmShps.append(grs_to_shp(
            osmShps[i], os.path.join(workspace, osmShps[i] + '.shp'),
            'auto', lyrN=1, asCMD=True, asMultiPart=None
        ))
    
    _osmShps = same_attr_to_shp(
        _osmShps, "cat", workspace, "osm_", resultDict=True
    )
    del osmShps
    
    time_o = datetime.datetime.now().replace(microsecond=0)
    
    """
    Merge all Classes into one feature class using a priority rule
    """
    
    osmShps = {}
    for cls in _osmShps:
        if cls == '1':
            osmShps[1221] = shp_to_grs(_osmShps[cls], "osm_1221", asCMD=True)
        
        else:
            osmShps[int(cls)] = shp_to_grs(_osmShps[cls], "osm_" + cls,
                asCMD=True)
    
    # Erase overlapping areas by priority
    for e in range(len(__priorities)):
        if e + 1 == len(__priorities): break
        
        if __priorities[e] not in osmShps: continue
        else:
            for i in range(e+1, len(__priorities)):
                if __priorities[i] not in osmShps:
                    continue
                else:
                    osmShps[__priorities[i]] = erase(
                        osmShps[__priorities[i]], osmShps[__priorities[e]],
                        "{}_{}".format(osmShps[__priorities[i]], e),
                        asCMD=True
                    )
    
    time_p = datetime.datetime.now().replace(microsecond=0)
    
    # Export all classes
    lst_merge = []
    for cls in osmShps:
        reset_table(
            osmShps[cls], {'cls' : 'varchar(5)'}, {'cls' : str(cls)}
        )
        
        ds = dissolve(
            osmShps[cls], 'dl_{}'.format(str(cls)), 'cls', asCMD=True)
        
        lst_merge.append(grs_to_shp(
            ds, os.path.join(workspace, "lulc_{}.shp".format(str(cls))),
            'auto', lyrN=1, asCMD=True, asMultiPart=None
        ))
    
    time_q = datetime.datetime.now().replace(microsecond=0)
    
    merge_shp(lst_merge, lulcShp)
    
    time_r = datetime.datetime.now().replace(microsecond=0)
    
    return lulcShp, {
        0  : ('set_settings', time_b - time_a),
        1  : ('osm_to_sqdb', time_c - time_b),
        2  : ('cls_in_sqdb', time_d - time_c),
        3  : ('proj_data', time_e - time_d),
        4  : ('set_grass', time_f - time_e),
        5  : ('rule_1', time_g - time_f, timeCheck1),
        6  : ('rule_2', time_h - time_g, timeCheck2),
        7  : ('rule_3', time_l - time_h, timeCheck3),
        8  : ('rule_4', time_j - time_l, timeCheck4),
        9  : ('rule_5', time_m - time_j, timeCheck5),
        10 : None if not timeCheck7 else ('rule_7', time_n - time_m, timeCheck7),
        11 : ('disj_cls', time_o - time_n),
        12 : ('priority_rule', time_p - time_o),
        13 : ('export_cls', time_q - time_p),
        14 : ('merge_cls', time_r - time_q)
    }

