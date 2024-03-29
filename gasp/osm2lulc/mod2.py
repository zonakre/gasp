"""
Rule 2 - Select Roads
"""

def grs_rst_roads(osmdb, lineTbl, polyTbl, dataFolder, LULC_CLS):
    """
    Raster Roads for GRASS
    """
    
    import os; import datetime
    from gasp.to.shp.grs    import shp_to_grs, sqlite_to_shp
    from gasp.to.rst        import shp_to_raster
    from gasp.sql.anls.prox import splite_buffer
    from gasp.sql.mng.tbl   import row_num
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    NR = row_num(osmdb, lineTbl, where="roads IS NOT NULL", api='sqlite')
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    roadFile = splite_buffer(
        osmdb, lineTbl, "bf_roads", "geometry", 'bfu_roads',
        #os.path.join(dataFolder, 'bf_roads.gml'),
        whrClause="roads IS NOT NULL",
        outTblIsFile=None, dissolve="ALL"
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    #roadGrs = shp_to_grs(roadFile, "bf_roads", filterByReg=True, asCMD=True)
    roadGrs = sqlite_to_shp(osmdb, "bfu_roads", 'bf_roads', notTable=True)
    time_d = datetime.datetime.now().replace(microsecond=0)
    roadRst = shp_to_raster(
        roadGrs, int(LULC_CLS), None, None, "rst_roads", api="grass"
    )
    time_e = datetime.datetime.now().replace(microsecond=0)
    
    # Builds to GRASS and to RASTER
    NB = row_num(osmdb, polyTbl, where="building IS NOT NULL", api='sqlite')
    time_f = datetime.datetime.now().replace(microsecond=0)
    
    if NB:
        from gasp.spanlst.algebra import rstcalc
        from gasp.spanlst.rcls    import set_null, null_to_value
        
        buildsShp = sqlite_to_shp(
            osmdb, polyTbl, "all_builds", where="building IS NOT NULL",
            notTable=True
        )
        time_g = datetime.datetime.now().replace(microsecond=0)
        
        buildsRst = shp_to_raster(
            buildsShp, 1, None, None, "rst_builds", api="grass"
        )
        time_h = datetime.datetime.now().replace(microsecond=0)
        
        # Buildings to nodata | Nodata to 0
        null_to_value(buildsRst, 0, as_cmd=True)
        time_i = datetime.datetime.now().replace(microsecond=0)
        set_null(buildsRst, 1, ascmd=True)
        time_j = datetime.datetime.now().replace(microsecond=0)
        
        # Do the math: roads + builds | if builds and roads at the same cell
        # cell will be null in the road layer
        roadsRes = rstcalc(
            "{} + {}".format(roadRst, buildsRst), "cls_roads", api="grass")
        time_l = datetime.datetime.now().replace(microsecond=0)
        
        return {LULC_CLS : roadsRes}, {
            0 : ('count_rows_roads', time_b - time_a),
            1 : ('buffer_roads', time_c - time_b),
            2 : ('import_roads', time_d - time_c),
            3 : ('roads_to_rst', time_e - time_d),
            4 : ('count_build', time_f - time_e),
            5 : ('builds_to_grs', time_g - time_f),
            6 : ('builds_to_rst', time_h - time_g),
            7 : ('bnull_to_val', time_i - time_h),
            8 : ('builds_to_nd', time_j - time_i),
            9 : ('roads_build_mc', time_l - time_j)
        }
    
    else:
        return {LULC_CLS : roadRst}, {
            0 : ('count_rows_roads', time_b - time_a),
            1 : ('buffer_roads', time_c - time_b),
            2 : ('import_roads', time_d - time_c),
            3 : ('roads_to_rst', time_e - time_d),
            4 : ('count_build', time_f - time_e)
        }


def grs_vec_roads(osmdb, lineTbl, polyTbl):
    """
    Select Roads for GRASS GIS
    """
    
    import datetime
    from gasp.sql.mng.tbl  import row_num
    from gasp.to.shp.grs   import sqlite_to_shp
    from gasp.anls.prox.bf import _buffer
    from gasp.mng.genze    import dissolve
    from gasp.mng.grstbl   import add_table
    
    # Roads to GRASS GIS
    time_a = datetime.datetime.now().replace(microsecond=0)
    NR = row_num(osmdb, lineTbl, where="roads IS NOT NULL", api='sqlite')
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    roadsVect = sqlite_to_shp(
        osmdb, lineTbl, "all_roads", where="roads IS NOT NULL"
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    # Buildings to GRASS GIS
    NB = row_num(osmdb, polyTbl, where="building IS NOT NULL", api='sqlite')
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    if NB:
        from gasp.anls.prox  import grs_near as near
        from gasp.mng.grstbl import update_table
        
        builds = sqlite_to_shp(
            osmdb, polyTbl, "all_builds", where="building IS NOT NULL",
            filterByReg=True
        )
        time_e = datetime.datetime.now().replace(microsecond=0)
        
        near(roadsVect, builds, nearDistCol="todist", maxDist=12, as_cmd=True)
        time_f = datetime.datetime.now().replace(microsecond=0)
        update_table(
            roadsVect, "bf_roads", "round(todist,0)",
            "\"todist > 0\"",
            lyrN=1, ascmd=True
        )
        time_g = datetime.datetime.now().replace(microsecond=0)
    
    else:
        time_e = None; time_f = None; time_g = None
    
    # Run Buffer tool
    roadsBf = _buffer(
        roadsVect, "bf_roads", "bf_roads",
        api='grass', geom_type="line"
    )
    time_h = datetime.datetime.now().replace(microsecond=0)
    
    # Dissolve Roads
    roadsDiss = dissolve(roadsBf, "diss_roads", field="roads", api="grass")
    
    add_table(roadsDiss, None, lyrN=1, asCMD=True)
    time_i = datetime.datetime.now().replace(microsecond=0)
    
    return roadsDiss, {
        0 : ('count_rows_roads', time_b - time_a),
        1 : ('import_roads', time_c - time_b),
        2 : ('count_rows_build', time_d - time_c),
        3 : None if not time_e else ('import_builds', time_e - time_d),
        4 : None if not time_f else ('near_analysis', time_f - time_e),
        5 : None if not time_g else ('update_buffer_tbl', time_g - time_f),
        6 : ('buffer_roads', time_h - time_g if time_g else time_h - time_d),
        7 : ('diss_roads', time_i - time_h)
    }


def roads_sqdb(osmcon, lnhTbl, plTbl, apidb='SQLITE', asRst=None):
    """
    Raods procedings using SQLITE
    """
    
    import datetime
    from gasp.sql.mng.tbl       import row_num as cnt_rows
    if apidb=='SQLITE':
        from gasp.sql.anls.prox import splite_buffer as st_buffer
        from gasp.to.shp.grs    import sqlite_to_shp as db_to_shp
    else:
        from gasp.sql.anls.prox import st_buffer
        from gasp.to.shp.grs    import psql_to_grs as db_to_shp
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    NR = cnt_rows(osmcon, lnhTbl, where="roads IS NOT NULL",
        api='psql' if apidb == 'POSTGIS' else 'sqlite'
    )
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    NB = cnt_rows(osmcon, plTbl, where="building IS NOT NULL",
        api='psql' if apidb == 'POSTGIS' else 'sqlite'
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    if NB:
        from gasp.sql.mng.qw import exec_write_q
        
        ROADS_Q = "(SELECT{} roads, bf_roads, geometry FROM {} WHERE roads IS NOT NULL)".format(
            "" if apidb == 'SQLITE' else " gid,", lnhTbl)
        if apidb == 'SQLITE':
            from gasp.sql.anls.prox import splite_near
        
            nroads = splite_near(
                osmcon, ROADS_Q,
                plTbl, "geometry", "geometry", "near_roads",
                whrNear="building IS NOT NULL"
            )
            time_d = datetime.datetime.now().replace(microsecond=0)
        
            # Update buffer distance field
            exec_write_q(osmcon, [(
                "UPDATE near_roads SET bf_roads = CAST(round(dist_near, 0) AS integer) "
                "WHERE dist_near >= 1 AND dist_near <= 12"
            ), (
                "UPDATE near_roads SET bf_roads = 1 WHERE dist_near >= 0 AND "
                "dist_near < 1"
            )], api='sqlite')
            time_e = datetime.datetime.now().replace(microsecond=0)
        
        else:
            from gasp.sql.anls.prox import st_near
            
            nroads = st_near(
                osmcon, ROADS_Q, 'gid', 'geometry',
                "(SELECT * FROM {} WHERE building IS NOT NULL)".format(plTbl),
                "geometry", "near_roads", untilDist="12", near_col="dist_near"
            )
            time_d = datetime.datetime.now().replace(microsecond=0)
            
            exec_write_q(osmcon, [(
                "UPDATE near_roads SET "
                "bf_roads = CAST(round(CAST(dist_near AS numeric), 0) AS integer) "
                "WHERE dist_near >= 1 AND dist_near <= 12"
            ), (
                "UPDATE near_roads SET bf_roads = 1 WHERE dist_near >= 0 AND "
                 "dist_near < 1"
            ), (
                "CREATE INDEX near_dist_idx ON near_roads USING gist (geometry)"
            )], api='psql')
            time_e = datetime.datetime.now().replace(microsecond=0)
    
    else:
        nroads =  (
            "(SELECT roads, bf_roads, geometry "
            "FROM {} WHERE roads IS NOT NULL) AS foo"
        ).format(lnhTbl)
        
        time_d = None; time_e = None
    
    # Execute Buffer
    bfTbl = st_buffer(
        osmcon, nroads, "bf_roads", "geometry", "bf_roads",
        cols_select="roads", outTblIsFile=None, dissolve="ALL"
    )
    time_f = datetime.datetime.now().replace(microsecond=0)
    
    # Send data to GRASS GIS
    roadsGrs = db_to_shp(
        osmcon, bfTbl, "froads", notTable=None, filterByReg=True
    )
    time_g = datetime.datetime.now().replace(microsecond=0)
    
    if asRst:
        from gasp.to.rst import shp_to_raster
        
        roadsGrs = shp_to_raster(
            roadsGrs, int(asRst), None, None, "rst_roads", api="grass"
        )
        
        time_h = datetime.datetime.now().replace(microsecond=0)
    else:
        time_h = None
    
    return roadsGrs, {
        0 : ('count_rows_roads', time_b - time_a),
        1 : ('count_rows_build', time_c - time_b),
        2 : None if not time_d else ('near_analysis', time_d - time_c),
        3 : None if not time_e else ('update_buffer_tbl', time_e - time_d),
        4 : ('buffer_roads', time_f - time_e if time_e else time_f - time_c),
        5 : ('import_roads', time_g - time_f),
        6 : None if not time_h else ('roads_to_raster', time_h - time_g)
    }


def num_roads(osmdata, nom, lineTbl, polyTbl, folder, cellsize, srs, rstTemplate):
    """
    Select Roads and convert To Raster
    """
    
    import datetime;        import os
    import numpy            as np
    from osgeo              import gdal
    from threading          import Thread
    from gasp.fm.rst        import rst_to_array
    from gasp.anls.exct     import sel_by_attr
    from gasp.sql.anls.prox import splite_buffer
    from gasp.to.rst        import shp_to_raster, array_to_raster
    from gasp.sql.mng.tbl   import row_num
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    NR = row_num(osmdata, lineTbl, where="roads IS NOT NULL", api='sqlite')
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    timeGasto = {0 : ('count_rows_roads', time_b - time_a)}
    
    # Get Roads Buffer
    LULC_CLS = '1221' if nom != "GLOBE_LAND_30" else '801'
    bfShps = []
    def exportAndBuffer():
        time_cc = datetime.datetime.now().replace(microsecond=0)
        roadFile = splite_buffer(
            osmdata, lineTbl, "bf_roads", "geometry",
            os.path.join(folder, 'bf_roads.gml'),
            whrClause="roads IS NOT NULL",
            outTblIsFile=True, dissolve=None
        )
        time_c = datetime.datetime.now().replace(microsecond=0)
        
        distRst = shp_to_raster(
            roadFile, None, cellsize, -1,
            os.path.join(folder, 'rst_roads.tif'),
            epsg=srs, rst_template=rstTemplate, api="gdal"
        )
        time_d = datetime.datetime.now().replace(microsecond=0)
        
        bfShps.append(distRst)
        
        timeGasto[1] = ('buffer_roads', time_c - time_cc)
        timeGasto[2] = ('to_rst_roads', time_d - time_c)
    
    BUILDINGS = []
    def exportBuild():
        time_ee = datetime.datetime.now().replace(microsecond=0)
        NB = row_num(
            osmdata, polyTbl, where="building IS NOT NULL", api='sqlite'
        )
        
        time_e = datetime.datetime.now().replace(microsecond=0)
        
        timeGasto[3] = ('check_builds', time_e - time_ee)
        
        if not NB:
            return
        
        bShp = sel_by_attr(
            osmdata,
            "SELECT geometry FROM {} WHERE building IS NOT NULL".format(
                polyTbl
            ),
            os.path.join(folder, 'road_builds.shp'),
            api_gis='ogr'
        )
        time_f = datetime.datetime.now().replace(microsecond=0)
        
        bRst = shp_to_raster(
            bShp, None, cellsize, -1,
            os.path.join(folder, 'road_builds.tif'),
            epsg=srs, rst_template=rstTemplate, api='gdal'
        )
        time_g = datetime.datetime.now().replace(microsecond=0)
        
        BUILDINGS.append(bRst)
        
        timeGasto[4] = ('export_builds', time_f - time_e)
        timeGasto[5] = ('builds_to_rst', time_g - time_f)
    
    thrds = [
        Thread(name="build-th", target=exportBuild),
        Thread(name='roads-th', target=exportAndBuffer)
    ]
    
    for t in thrds: t.start()
    for t in thrds: t.join()
    
    if not len(BUILDINGS):
        return {LULC_CLS : bfShps[0]}
    
    time_x = datetime.datetime.now().replace(microsecond=0)
    BUILD_ARRAY = rst_to_array(BUILDINGS[0], with_nodata=True)
    rst_array = rst_to_array(bfShps[0], with_nodata=True)
    np.place(rst_array, BUILD_ARRAY==1, 0)
        
    newRaster = array_to_raster(
        rst_array, os.path.join(folder, 'fin_roads.tif'),
        rstTemplate, srs, gdal.GDT_Byte, noData=-1,
        gisApi='gdal'
    )
    
    time_z = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto[6] = ('sanitize_roads', time_z - time_x)
    
    return {int(LULC_CLS) : newRaster}, timeGasto


def arc_roadsrule(osmDb, lineTbl, polyTbl, folder):
    """
    Select Roads and Transform them into polygons
    """
    
    import datetime
    from gasp.anls.exct    import sel_by_attr
    from gasp.sql.mng.tbl  import row_num
    from gasp.anls.prox.bf import _buffer
    
    # Roads to ArcGIS
    time_a = datetime.datetime.now().replace(microsecond=0)
    NR = row_num(osmDb, lineTbl, where="roads IS NOT NULL", api='sqlite')
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    # Export all roads
    allRoads = sel_by_attr(osmDb, (
        "SELECT roads, bf_roads, geometry "
        "FROM {} WHERE roads IS NOT NULL"
    ).format(lineTbl), os.path.join(folder, 'all_roads.shp'), api_gis='ogr')
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    # Export Buildings
    NB = row_num(osmDb, polyTbl, where="building IS NOT NULL", api='sqlite')
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    if NB:
        from gasp.arcg.anls.prox import near_anls
        
        builds = sel_by_attr(osmDb, (
            "SELECT geometry FROM {} "
            "WHERE building IS NOT NULL"
        ), os.path.join(folder, "all_builds.shp"), api_gis='ogr')
        time_e = datetime.datetime.now().replace(microsecond=0)
        
        near_anls(allRoads, builds, searchRadius=12)
        
        # Update table
        
    
    
    # Execute near
    if allBuildings:
        near_anls(allRoads, allBuildings, searchRadius=12)
    
        # Create Buffer for roads near buildings
        nearBuildRoadsLnh = select_by_attr(
            allRoads, "NEAR_FID <> -1",
            os.path.join(WORK, 'roads_near')
        )
    
        nearBuildRoads = _buffer(
            nearBuildRoadsLnh, "NEAR_DIST",
            os.path.join(WORK, 'roads_bf_near'), dissolve="ALL", api='arcpy'
        )
        
        L.append(nearBuildRoads)
    
    for dist in distInstances:
        # Buffer and export
        filterDf = osmToSelect[osmToSelect[BF_COL] == dist]
        
        Q = "{}" if not allBuildings else "({}) AND NEAR_FID = -1"
        
        rdvShp = select_by_attr(
            allRoads,
            Q.format(str(filterDf[VALUE_COL].str.cat(sep=" OR "))),
            os.path.join(WORK, "roads_{}".format(str(dist)))
        )
        
        if not feat_count(rdvShp, gisApi='arcpy'): continue
        
        roadsShp = Buffer(
            rdvShp, os.path.join(WORK, "roads_bf_{}".format(str(dist))),
            str(int(dist)), dissolve="ALL"
        )
        
        L.append(roadsShp)
        
        delete(rdvShp)
    
    delete(allBuildings)
    
    LULC_CLS = 1221 if nomenclature != 'GLOBE_LAND_30' else 801
    return {LULC_CLS : L}


def pg_num_roads(osmLink, nom, lnhTbl, polyTbl, folder, cellsize, srs, rstT):
    """
    Select, Calculate Buffer distance using POSTGIS, make buffer of roads
    and convert roads to raster
    """
    
    import datetime;        import os
    from osgeo              import gdal
    from gasp.sql.mng.tbl   import row_num
    from gasp.sql.anls.prox import st_buffer
    from gasp.to.rst        import shp_to_raster
    
    # There are roads?
    time_a = datetime.datetime.now().replace(microsecond=0)
    NR = row_num(osmLink, lnhTbl, where="roads IS NOT NULL", api='psql')
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    # There are buildings?
    NB = row_num(osmLink, polyTbl, where="building IS NOT NULL", api='psql')
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    if NB:
        from gasp.sql.anls.prox import st_near
        from gasp.sql.mng.qw    import exec_write_q
        
        nroads = st_near(
            osmLink, (
                "(SELECT gid, roads, bf_roads, geometry FROM {} "
                "WHERE roads IS NOT NULL)"
            ).format(lnhTbl), "gid", "geometry", (
                "(SELECT * FROM {} WHERE building IS NOT NULL)"
            ).format(polyTbl), "geometry", "near_roads", untilDist="12",
            near_col="dist_near"
        )
        time_d = datetime.datetime.now().replace(microsecond=0)
        
        exec_write_q(osmLink, [(
            "UPDATE near_roads SET "
            "bf_roads = CAST(round(CAST(dist_near AS numeric), 0) AS integer) "
            "WHERE dist_near >= 1 AND dist_near <= 12"
        ), "CREATE INDEX near_dist_idx ON near_roads USING gist (geometry)"])
        time_e = datetime.datetime.now().replace(microsecond=0)
    
    else:
        nroads = (
            "(SELECT roads, bf_roads, geometry FROM {} "
            "WHERE roads IS NOT NULL) AS foo"
        ).format(lnhTbl)
        
        time_d = None; time_e=None
    
    # Execute Buffer
    bufferShp = st_buffer(
        osmLink, nroads, "bf_roads", "geometry",
        os.path.join(folder, "bf_roads.shp"),
        cols_select="roads", outTblIsFile=True, dissolve=None
    )
    time_f = datetime.datetime.now().replace(microsecond=0)
    
    # Convert to Raster
    roadsRst = shp_to_raster(
        bufferShp, None, cellsize, 0,
        os.path.join(folder, "rst_roads.tif"), epsg=srs, rst_template=rstT,
        api='gdal'
    )
    time_g = datetime.datetime.now().replace(microsecond=0)
    
    LULC_CLS = '1221' if nom != "GLOBE_LAND_30" else '801'
    
    return {int(LULC_CLS) : roadsRst}, {
        0 : ('count_rows_roads', time_b - time_a),
        1 : ('count_rows_build', time_c - time_b),
        2 : None if not time_d else ('near_analysis', time_d - time_c),
        3 : None if not time_e else ('update_buffer_tbl', time_e - time_d),
        4 : ('buffer_roads', time_f - time_e if time_e else time_f - time_c),
        5 : ('roads_to_raster', time_g - time_f)
    }
