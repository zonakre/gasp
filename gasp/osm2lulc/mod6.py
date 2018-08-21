"""
Rule 7
"""

import os
from gasp.osm2lulc.var   import DB_SCHEMA

def rst_pnt_to_build(osmdb, pntTable, polyTable):
    """
    Replace buildings with tag yes using the info in the Points Layer
    
    Only used for URBAN ATLAS and CORINE LAND COVER
    """
    
    import datetime
    from gasp.fm.sqLite            import sqlq_to_df
    from gasp.sqLite.i             import count_rows_in_query
    from gasp.cpu.gdl.splite.ovlay import intersect_point_with_polygon
    from gasp.cpu.gdl.splite.ovlay import disjoint_polygons_rel_points
    from gasp.to.rst.grs           import shp_to_raster
    from gasp.to.shp.grs           import sqlite_to_shp
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    intersect_point_with_polygon(
        osmdb,
        "pnt_buildings", "pnt_geom",
        "poly_buildings", "poly_geom",
        "new_buildings",
        "pnt_build AS cls",
        "poly_geom AS geometry",
        ("(SELECT buildings AS pnt_build, geometry AS pnt_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS pnt_buildings"
        ).format(pntTable),
        ("(SELECT buildings AS poly_build, geometry AS poly_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS poly_buildings"
        ).format(polyTable),
        outTblIsFile=None
    )
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    disjoint_polygons_rel_points(
        osmdb,
        "pnt_buildings", "pnt_geom",
        "poly_buildings", "poly_geom",
        "yes_builds",
        "poly_geom AS geometry, 11 AS cls",
        ("(SELECT buildings AS pnt_build, geometry AS pnt_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS pnt_buildings"
        ).format(pntTable),
        ("(SELECT buildings AS poly_build, geometry AS poly_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS poly_buildings"
        ).format(polyTable),
        outTblIsFile=None
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    resLayers = {}
    N11 = count_rows_in_query(osmdb, "yes_builds")
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    if N11:
        # Data to GRASS GIS
        grsBuild11 = sqlite_to_shp(
            osmdb, "yes_builds", "yes_builds", notTable=True)
        time_f = datetime.datetime.now().replace(microsecond=0)
        
        # To raster
        rstBuild11 = shp_to_raster(grsBuild11, "rst_builds11", 11, as_cmd=True)
        time_g = datetime.datetime.now().replace(microsecond=0)
        
        resLayers[11] = [rstBuild11]
    
    else:
        time_f = None; time_g = None
    
    # Add data into GRASS GIS
    lulcCls = sqlq_to_df(
        osmdb, "SELECT cls FROM new_buildings GROUP BY cls").cls.tolist()
    
    timeGasto = {
        0 : ('intersect', time_b - time_a),
        1 : ('disjoint', time_c - time_b),
        2 : ('count_b11', time_d - time_c),
        3 : None if not time_f else ('import_b11', time_f - time_d),
        4 : None if not time_g else ('torst_b11', time_g - time_f),
    }
    tk = 5
    for cls in lulcCls:
        time_x = datetime.datetime.now().replace(microsecond=0)
        shp = sqlite_to_shp(
            osmdb, "new_buildings", "nbuild_{}".format(str(cls)),
            "cls = {}".format(cls), notTable=True
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        rstb = shp_to_raster(
            shp, "rst_nbuild_{}".format(str(cls)), int(cls), as_cmd=True
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        if int(cls) == 11 and int(cls) in resLayers:
            resLayers[int(cls)].append(rstb)
        
        else:
            resLayers[int(cls)] = [rstb]
        
        timeGasto[tk]     = ('import_bn{}'.format(cls), time_y - time_x)
        timeGasto[tk + 1] = ('torst_bn{}'.format(cls), time_z - time_y)
        
        tk += 2
    
    return resLayers, timeGasto


def vector_assign_pntags_to_build(osmdb, pntTable, polyTable):
    """
    Replace buildings with tag yes using the info in the Points Layer
    
    Only used for URBAN ATLAS and CORINE LAND COVER
    """
    
    import datetime
    from gasp.sqLite.i             import count_rows_in_query
    from gasp.cpu.gdl.splite.ovlay import intersect_point_with_polygon
    from gasp.cpu.gdl.splite.ovlay import disjoint_polygons_rel_points
    from gasp.cpu.grs.mng.genze    import dissolve
    from gasp.to.shp.grs           import sqlite_to_shp
    from gasp.cpu.grs.mng.tbl      import add_table
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    intersect_point_with_polygon(
        osmdb,
        "pnt_buildings", "pnt_geom",
        "poly_buildings", "poly_geom",
        'new_buildings',
        "pnt_build AS cls",
        "poly_geom AS geometry",
        ("(SELECT buildings AS pnt_build, geometry AS pnt_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS pnt_buildings"
        ).format(pntTable),
        ("(SELECT buildings AS poly_build, geometry AS poly_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS poly_buildings"
        ).format(polyTable),
        outTblIsFile=None
    )
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    disjoint_polygons_rel_points(
        osmdb,
        "pnt_buildings", "pnt_geom",
        "poly_buildings", "poly_geom",
        "yes_builds",
        "poly_geom AS geometry, 11 AS cls",
        ("(SELECT buildings AS pnt_build, geometry AS pnt_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS pnt_buildings"
        ).format(pntTable),
        ("(SELECT buildings AS poly_build, geometry AS poly_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS poly_buildings"
        ).format(polyTable),
        outTblIsFile=None
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    N12 = count_rows_in_query(osmdb, "new_buildings")
    time_d = datetime.datetime.now().replace(microsecond=0)
    N11 = count_rows_in_query(osmdb, "yes_builds")
    time_e = datetime.datetime.now().replace(microsecond=0)
    
    if N11:
        # Add data into grasss
        grsBuild11 = sqlite_to_shp(osmdb, "yes_builds", "yes_builds")
        time_f = datetime.datetime.now().replace(microsecond=0)
        
        # Dissolve
        dissVect = dissolve(
            grsBuild11, "dss_{}".format(grsBuild11),
            field='cls', asCMD=True
        )
        
        add_table(dissVect, None, lyrN=1, asCMD=True)
        time_g = datetime.datetime.now().replace(microsecond=0)
    else:
        dissVect = None
        time_f = None; time_g = None
    
    if N12:
        # Add data into GRASS GIS
        grsBuild12 = sqlite_to_shp(
            osmdb, "new_buildings", "pnt_build")
        
        time_h = datetime.datetime.now().replace(microsecond=0)
        
        # Dissolve
        dissVect12 = dissolve(
            grsBuild12, "dss_{}".format(grsBuild12),
            field='cls', asCMD=True
        )
        
        add_table(dissVect12, None, lyrN=1, asCMD=True)
        time_i = datetime.datetime.now().replace(microsecond=0)
    
    else:
        dissVect12 = None
        time_h = None; time_i = None
    
    return dissVect, dissVect12, {
        0 : ('intersect', time_b - time_a),
        1 : ('disjoint', time_c - time_b),
        2 : ('count_b12', time_d - time_c),
        3 : ('count_b11', time_e - time_d),
        4 : None if not time_f else ('import_b11', time_f - time_e),
        5 : None if not time_g else ('dissolve_b11', time_g - time_f),
        6 : None if not time_h else (
            'import_b12', time_h - time_g if time_g else time_h - time_e),
        7 : None if not time_i else ('dissolve_b12', time_i - time_h)
    }


def num_assign_builds(osmsq, pntTbl, polTbl, folder, cells, srscode, rtemplate):
    """
    Replace buildings with tag yes using the info in the Points Layer
    
    Only used for URBAN ATLAS and CORINE LAND COVER
    """
    
    import datetime
    from threading                 import Thread
    from gasp.fm.sqLite            import sqlq_to_df
    from gasp.cpu.gdl.splite.ovlay import intersect_point_with_polygon
    from gasp.cpu.gdl.splite.ovlay import disjoint_polygons_rel_points
    from gasp.to.rst.gdl           import shp_to_raster
    from gasp.cpu.gdl.anls.exct    import sel_by_attr
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    build12 = "info_builds"
    intersect_point_with_polygon(osmsq,
        "pnt_buildings", "pnt_geom",
        "poly_buildings", "poly_geom",
        build12,
        "pnt_build AS cls",
        "poly_geom AS geometry",
        ("(SELECT buildings as pnt_build, geometry AS pnt_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS pnt_buildings"
        ).format(pntTbl),
        ("(SELECT buildings AS poly_build, geometry AS poly_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS poly_buildings"
        ).format(polTbl),
        outTblIsFile=None
    )
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    build11 = os.path.join(folder, 'unkbuilds.shp')
    disjoint_polygons_rel_points(osmsq,
        "pnt_buildings", "pnt_geom",
        "poly_buildings", "poly_geom",
        build11,
        "poly_geom AS geometry, 11 AS cls",
        ("(SELECT buildings AS pnt_build, geometry AS pnt_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS pnt_buildings"
        ).format(pntTbl),
        ("(SELECT building AS poly_build, geometry AS poly_geom "
         "FROM {} WHERE buildings IS NOT NULL) AS poly_buildings"
        ).format(polTbl),
        outTblIsFile=True
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {
        0 : ('intersect', time_b - time_a),
        1 : ('disjoin', time_c - time_b)
    }
    
    resLyr = {}
    def toRaster(buildShp, cls):
        if not os.path.exists(buildShp): return
        
        # To Raster
        time_x = datetime.datetime.now().replace(microsecond=0)
        rstbuild = shp_to_raster(
            buildShp, cells, -1,
            os.path.join(folder, 'rst_build_{}.tif'.format(cls)),
            srscode, rtemplate
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        resLyr[33] = rstbuild
        
        timeGasto[33] = ('to_rst_{}'.format(cls), time_y - time_x)
    
    def build12_torst(buildTbl):
        LulcCls = sqlq_to_df(osmsq, "SELECT cls FROM {} GROUP BY cls".format(
            buildTbl)).cls.tolist()
        
        for lulc_cls in LulcCls:
            time_m = datetime.datetime.now().replace(microsecond=0)
            
            # To SHP
            shpB = sel_by_attr(
                osmsq, "SELECT * FROM {} WHERE cls={}".format(
                    buildTbl, str(lulc_cls)
                ), os.path.join(folder, 'nshp_build_{}.shp'.format(lulc_cls))
            )
            time_n = datetime.datetime.now().replace(microsecond=0)
            
            # To RST
            brst = shp_to_raster(
                shpB, cells, -1,
                os.path.join(folder, 'nrst_build_{}.tif'.format(lulc_cls)),
                srscode, rtemplate
            )
            time_o = datetime.datetime.now().replace(microsecond=0)
            
            resLyr[int(lulc_cls)] = [brst]
            
            timeGasto[int(lulc_cls)] = ('to_shp_{}'.format(str(lulc_cls)), time_n - time_m)
            timeGasto[int(lulc_cls) + 1] = (
                'to_rst_n_{}'.format(str(lulc_cls)), time_o - time_n
            )
    
    thrds = [
        Thread(name='builds-th-11', target=toRaster, args=(build11, 11)),
        Thread(name='builds-th-12', target=build12_torst, args=(build12,))
    ]
    
    for t in thrds: t.start()
    for t in thrds: t.join()
    
    if 33 in resLyr:
        if 11 in resLyr:
            resLyr[11].append(resLyr[33])
        
        else:
            resLyr[11] = [resLyr[33]]
            
        del resLyr[33]
    
    return resLyr, timeGasto


def arc_pnt_to_build(Nomenclature, pntTbl, polyTbl):
    """
    Replace buildings with tag yes using the info in the Points Layer
    
    Only used for URBAN ATLAS and CORINE LAND COVER
    """
    
    from gasp.osm2lulc.utils     import osm_features_by_rule
    from gasp.cpu.arcg.anls.exct import select_by_attr
    from gasp.cpu.arcg.anls.prox import near_anls
    from gasp.prop.feat          import feat_count
    from gasp.cpu.arcg.mng.fld   import del_field, list_fields
    from gasp.cpu.arcg.mng.gen   import delete
    
    KEY_COL   = DB_SCHEMA["OSM_FEATURES"]["OSM_KEY"]
    VALUE_COL = DB_SCHEMA["OSM_FEATURES"]["OSM_VALUE"]
    LULC_COL  = DB_SCHEMA[Nomenclature]["CLS_FK"]
    
    # Get OSM Features that will be used in this rule
    osmToSelect_poly = osm_features_by_rule(Nomenclature, "buildings")
    
    # Get OSM Features to extract from Polygons layer
    osmToSelect_poly[VALUE_COL] = osmToSelect_poly[KEY_COL] + "='" + \
        osmToSelect_poly[VALUE_COL] + "'"
    
    # Get OSM Features to extract from Points layer
    osmToSelect_pnt = osm_features_by_rule(Nomenclature, "selection")
    osmToSelect_pnt = osmToSelect_pnt[osmToSelect_pnt[LULC_COL] == 12]
    osmToSelect_pnt = osmToSelect_pnt[osmToSelect_pnt[KEY_COL] == 'building']
    osmToSelect_pnt[VALUE_COL] = osmToSelect_pnt[KEY_COL] + "='" + \
        osmToSelect_pnt[VALUE_COL] + "'"
    
    WORK = os.path.dirname(polyTbl)
    # Export Buildings
    buildUnk = select_by_attr(
        polyTbl, str(osmToSelect_poly[VALUE_COL].str.cat(sep=" OR ")),
        os.path.join(WORK, "build_unk")
    )
    
    if not feat_count(buildUnk, gisApi='arcpy'): return 0
    
    # Delete all fields in the last table
    FLDS = [x for x in list_fields(
        buildUnk) if x != 'OBJECTID' and x != 'SHAPE' and x != 'SHAPE_Area' and x != 'SHAPE_Length']
    del_field(buildUnk, FLDS)
    
    # Export POI's
    poiBuild = select_by_attr(
        pntTbl, str(osmToSelect_pnt[VALUE_COL].str.cat(sep=" OR ")),
        os.path.join(WORK, "poi_build"))
    
    if not feat_count(poiBuild, gisApi='arcpy'):
        return {11 : buildUnk}
    
    near_anls(buildUnk, poiBuild, 1, joinData=None)
    
    delete(poiBuild)
    
    # Export Unknow Builds
    realUnk = select_by_attr(
        buildUnk, "NEAR_DIST <> 0",
        os.path.join(WORK, "build_11")
    )
    
    resLyr = {}
    if feat_count(realUnk, gisApi='arcpy'):
        resLyr[11] = realUnk
    
    # Export Know Builds
    buildKnow = select_by_attr(
        buildUnk, "NEAR_DIST = 0", os.path.join(WORK, "build_12")
    )
    
    if count_feat(buildKnow, gisApi='arcpy'):
        resLyr[12] = buildKnow
    
    delete(buildUnk)
    
    return resLyr

