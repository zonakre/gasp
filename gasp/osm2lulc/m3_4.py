"""
Rule 3 and 4 - Area upper than and less than
"""

from gasp.osm2lulc.var   import DB_SCHEMA

def rst_area(osmLink, polygonTable, UPPER=True, api='SQLITE'):
    """
    Select features with area upper than.
    
    A field with threshold is needed in the database.
    """
    
    import datetime
    if api == 'POSTGIS':
        from gasp.fm.psql    import query_to_df as sqlq_to_df
        from gasp.to.shp.grs import psql_to_grs as db_to_grs
    else:
        from gasp.fm.sqLite  import sqlq_to_df
        from gasp.to.shp.grs import sqlite_to_shp as db_to_grs
    from gasp.to.rst.grs     import shp_to_raster
    from gasp.osm2lulc.var   import GEOM_AREA
    
    RULE_COL = 'area_upper' if UPPER else 'area_lower'
    OPERATOR = " > " if UPPER else " < "
    
    WHR = "{ga} {op} t_{r} AND {r}={cls_}"
    
    # Get Classes
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = sqlq_to_df(osmLink, (
        "SELECT {r} FROM {tbl} WHERE {ga} {op} t_{r} GROUP BY {r}"
    ).format(
         r=RULE_COL, tbl=polygonTable, ga=GEOM_AREA, op=OPERATOR
    ))[RULE_COL].tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    # Import data into GRASS and convert it to raster
    clsRst = {}
    tk = 1
    for cls in lulcCls:
        time_x = datetime.datetime.now().replace(microsecond=0)
        grsVect = db_to_grs(
            osmLink, polygonTable, "{}_{}".format(RULE_COL, cls),
            where=WHR.format(
                op=OPERATOR, r=RULE_COL, ga=GEOM_AREA, cls_=cls
            ), notTable=True, filterByReg=True
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        timeGasto[tk] = ('import_{}'.format(cls), time_y - time_x)
        
        grsRst = shp_to_raster(
            grsVect, "rst_{}".format(RULE_COL),
            int(cls), as_cmd=True
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        timeGasto[tk+1] = ('torst_{}'.format(cls), time_z - time_y)
        
        clsRst[int(cls)] = grsRst
        tk += 2
        
    return clsRst, timeGasto


def grs_vect_selbyarea(osmcon, polyTbl, UPPER=True, apidb='SQLITE'):
    """
    Select features with area upper than.
    
    A field with threshold is needed in the database.
    """
    
    import datetime
    from gasp.cpu.grs.mng.genze import dissolve
    from gasp.cpu.grs.mng.tbl   import add_table
    from gasp.osm2lulc.var      import GEOM_AREA
    if apidb != 'POSTGIS':
        from gasp.sqLite.i   import count_rows_in_query as cnt_row
        from gasp.to.shp.grs import sqlite_to_shp as db_to_shp
    else:
        from gasp.cpu.psql.i import get_row_number as cnt_row
        from gasp.to.shp.grs import psql_to_grs as db_to_shp
        
    
    OPERATOR  = ">" if UPPER else "<"
    DIRECTION = "upper" if UPPER else "lower"
    
    WHR = "{ga} {op} t_area_{r} and area_{r} IS NOT NULL".format(
        op=OPERATOR, r=DIRECTION, ga=GEOM_AREA
    )
    
    # Check if we have interest data
    time_a = datetime.datetime.now().replace(microsecond=0)
    N = cnt_row(osmcon, polyTbl, where=WHR)
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not N: return None, {0 : ('count_rows', time_b - time_a)}
    
    # Data to GRASS GIS
    grsVect = db_to_shp(
        osmcon, polyTbl, "area_{}".format(DIRECTION), where=WHR,
        filterByReg=True
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    dissVect = dissolve(
        grsVect, "diss_area_{}".format(DIRECTION),
        "area_{}".format(DIRECTION), asCMD=True
    )
    
    add_table(dissVect, None, lyrN=1, asCMD=True)
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    return dissVect, {
        0 : ('count_rows', time_b - time_a),
        1 : ('import', time_c - time_b),
        2 : ('dissolve', time_d - time_c)
    }


def num_selbyarea(osmLink, polyTbl, folder, cellsize, srscode, rstTemplate,
                  UPPER=True, api='SQLITE'):
    """
    Select features with area upper than.
    
    A field with threshold is needed in the database.
    """
    
    import datetime;                import os
    from threading                  import Thread
    if api == 'SQLITE':
        from gasp.fm.sqLite         import sqlq_to_df
        from gasp.cpu.gdl.anls.exct import sel_by_attr
    else:
        from gasp.fm.psql           import query_to_df as sqlq_to_df
        from gasp.to.shp            import psql_to_shp as sel_by_attr
    from gasp.to.rst.gdl            import shp_to_raster
    from gasp.osm2lulc.var          import GEOM_AREA
    
    # Get OSM Features to be selected for this rule
    RULE_COL = 'area_upper' if UPPER else 'area_lower'
    OPERATOR = " > " if UPPER else " < "
    WHR = "{ga} {op} t_{r} AND {r}={cls_}"
    
    # Get Classes
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = sqlq_to_df(osmLink, (
        "SELECT {r} FROM {tbl} WHERE {ga} {op} t_{r} GROUP BY {r}"
    ).format(
        r=RULE_COL, tbl=polyTbl, ga=GEOM_AREA, op=OPERATOR
    ))[RULE_COL].tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    clsRst = {}
    SQL_Q = (
        "SELECT geometry, {c} AS cls FROM {tbl} WHERE {w}"
    )
    def selAndExport(CLS, cnt):
        time_x = datetime.datetime.now().replace(microsecond=0)
        if api == "SQLITE":
            shpCls = sel_by_attr(
                osmLink, SQL_Q.format(c=str(CLS), tbl=polyTbl, w=WHR.format(
                    op=OPERATOR, r=RULE_COL, ga=GEOM_AREA, cls_=CLS
                )),
                os.path.join(folder, "{}_{}.shp".format(RULE_COL,CLS))
            )
        else:
            shpCls = sel_by_attr(
                osmLink, SQL_Q.format(c=str(CLS), tbl=polyTbl, w=WHR.format(
                    op=OPERATOR, r=RULE_COL, ga=GEOM_AREA, cls_=CLS
                )), os.path.join(folder, "{}_{}.shp".format(RULE_COL, str(CLS))),
                api='pgsql2shp', geom_col="geometry", tableIsQuery=True
            )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        rst = shp_to_raster(
            shpCls, cellsize, 0, os.path.join(
                folder, "{}_{}.tif".format(RULE_COL, CLS)
            ), srscode, rstTemplate
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[int(CLS)] = rst
        timeGasto[cnt + 1] = ('sq_to_shp_{}'.format(str(CLS)), time_y - time_x)
        timeGasto[cnt + 2] = ('shp_to_rst_{}'.format(str(CLS)), time_z - time_y)
    
    thrds = [Thread(
        name="area-tk{}".format(lulcCls[i]), target=selAndExport,
        args=(lulcCls[i], (i+1) * 10)
    ) for i in range(len(lulcCls))]
    
    for t in thrds: t.start()
    for t in thrds: t.join()
    
    return clsRst, timeGasto


def arcg_area(polyTbl, lulcNomenclature, UPPER=True):
    """
    Select Features with area upper than
    """
    
    from gasp.osm2lulc.utils     import osm_features_by_rule
    from gasp.cpu.arcg.anls.exct import select_by_attr
    from gasp.cpu.arcg.mng.fld   import add_geom_attr
    from gasp.cpu.arcg.mng.gen   import delete
    from gasp.mng.genze          import dissolve
    from gasp.prop.feat          import feat_count
    
    KEY_COL   = DB_SCHEMA["OSM_FEATURES"]["OSM_KEY"]
    VALUE_COL = DB_SCHEMA["OSM_FEATURES"]["OSM_VALUE"]
    LULC_COL  = DB_SCHEMA[lulcNomenclature]["CLS_FK"]
    RULE_COL  = DB_SCHEMA[lulcNomenclature]["RULES_FIELDS"]["AREA"]
    
    # Get OSM Features to be selected for this rule
    __serv = 'area_upper' if UPPER else 'area_lower'
    osmToSelect = osm_features_by_rule(lulcNomenclature, __serv)
    
    operator = " > " if UPPER else " < "
    osmToSelect[VALUE_COL] = "(" + osmToSelect[KEY_COL] + "='" + \
        osmToSelect[VALUE_COL] + "' AND shp_area" + operator + \
        osmToSelect[RULE_COL].astype(str) + ")"
    
    lulcCls = osmToSelect[LULC_COL].unique()
    
    clsVect = {}
    WORK = os.path.dirname(polyTbl)
    
    for cls in lulcCls:
        # Select and Export
        filterDf = osmToSelect[osmToSelect[LULC_COL] == cls]
        
        fShp = select_by_attr(
            polyTbl, 
            str(filterDf[VALUE_COL].str.cat(sep=" OR ")),
            os.path.join(WORK, "{}_{}".format(__serv, str(cls)))
        )
        
        if not feat_count(fShp, gisApi='arcpy'): continue
        
        # Dissolve
        dissShp = dissolve(
            fShp, os.path.join(WORK, "{}_d_{}".format(__serv, str(cls))),
            "OBJECTID", geomMultiPart=None, api='arcpy'
        )
        
        if not feat_count(dissShp, gisApi='arcpy'): continue
        
        clsVect[int(cls)] = dissShp
        
        delete(fShp)
    
    return clsVect


def sel_by_dist_to_pop():
    """
    The assign of OSM Features to the 3 or 14 LULC Class depends one the
    distance to the population 
    """
    
    # For POPULATION DATASET or Residential Building Dataset:
    # To Point | Focal Statistic | Select areas > than threshold |
    # Distance to these areas | Assign classes based on the distance relation
    
    # Other option is:
    # Check if inside the polygons are things normaly within green urban spaces
    # parques infantis, etc.
    
    return None