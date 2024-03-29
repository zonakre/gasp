"""
Rule 5 - Basic buffer
"""

import os
from gasp.osm2lulc.var   import DB_SCHEMA

def basic_buffer(osmLink, lineTable, dataFolder, apidb='SQLITE'):
    """
    Data from Lines table to Polygons using a basic buffering stratagie
    """
    
    import datetime
    from gasp.fm.sql            import query_to_df
    if apidb == 'POSTGIS':
        from gasp.sql.anls.prox import st_buffer
    else:
        from gasp.sql.anls.prox import splite_buffer as st_buffer
    from gasp.to.rst            import shp_to_raster
    from gasp.to.shp.grs        import shp_to_grs
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = query_to_df(osmLink, (
        "SELECT basic_buffer FROM {} WHERE basic_buffer IS NOT NULL "
        "GROUP BY basic_buffer"
    ).format(
        lineTable
    ), db_api='psql' if apidb=='POSTGIS' else 'sqlite').basic_buffer.tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    clsRst = {}
    tk = 1
    for cls in lulcCls:
        # Run BUFFER Tool
        time_x = datetime.datetime.now().replace(microsecond=0)
        bb_file = st_buffer(
            osmLink, lineTable, "bf_basic_buffer", "geometry",
            os.path.join(dataFolder, 'bb_rule5_{}.shp'.format(str(int(cls)))),
            whrClause="basic_buffer={}".format(str(int(cls))),
            outTblIsFile=True, dissolve="ALL", cols_select="basic_buffer"
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        # Data TO GRASS
        grsVect = shp_to_grs(
            bb_file, "bb_{}".format(int(cls)), asCMD=True,
            filterByReg=True
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        # Data to Raster
        rstVect = shp_to_raster(
            grsVect, int(cls), None, None, "rbb_{}".format(int(cls)), 
            api="grass"
        )
        time_w = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[int(cls)] = rstVect
        
        timeGasto[tk]   = ('do_buffer_{}'.format(cls), time_y - time_x)
        timeGasto[tk+1] = ('import_{}'.format(cls), time_z - time_y)
        timeGasto[tk+2] = ('torst_{}'.format(cls), time_w - time_z)
        
        tk += 3
    
    return clsRst, timeGasto


def grs_vect_bbuffer(osmdata, lineTbl, api_db='SQLITE'):
    """
    Basic Buffer strategie
    """
    
    import datetime
    from gasp.anls.prox.bf   import _buffer
    from gasp.mng.genze      import dissolve
    from gasp.mng.grstbl     import add_table
    from gasp.sql.mng.tbl    import row_num as cnt_row
    if api_db != 'POSTGIS':
        from gasp.to.shp.grs import sqlite_to_shp as db_to_shp
    else:
        from gasp.to.shp.grs import psql_to_grs   as db_to_shp
    
    WHR = "basic_buffer IS NOT NULL"
    
    # Check if we have data
    time_a = datetime.datetime.now().replace(microsecond=0)
    N = cnt_row(osmdata, lineTbl, where=WHR,
        api='psql' if api_db == 'POSTGIS' else 'sqlite'
    )
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not N: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    grsVect = db_to_shp(
        osmdata, lineTbl, "bb_lnh", where=WHR, filterByReg=True
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    grsBuf  = _buffer(
        grsVect, "bf_basic_buffer", "bb_poly", api="grass", geom_type="line"
    )
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    grsDiss = dissolve(grsBuf, "bb_diss", "basic_buffer", api="grass")
    add_table(grsDiss, None, lyrN=1, asCMD=True)
    time_e = datetime.datetime.now().replace(microsecond=0)
    
    return grsDiss, {
        0 : ('count_rows', time_b - time_a),
        1 : ('import', time_c - time_b),
        2 : ('buffer', time_d - time_c),
        3 : ('dissolve', time_e - time_d)
    }


def num_base_buffer(osmLink, lineTbl, folder, cells, srscode, rtemplate,
                    api='SQLITE'):
    """
    Data from Lines to Polygons
    """
    
    import datetime
    from threading              import Thread
    from gasp.fm.sql            import query_to_df
    if api=='SQLITE':
        from gasp.sql.anls.prox import splite_buffer as st_buffer
    else:
        from gasp.sql.anls.prox import st_buffer
    from gasp.to.rst            import shp_to_raster
    
    # Get LULC Classes to be selected
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = query_to_df(osmLink, (
        "SELECT basic_buffer FROM {} WHERE basic_buffer IS NOT NULL "
        "GROUP BY basic_buffer"
    ).format(
        lineTbl
    ), db_api='psql' if api == 'POSTGIS' else 'sqlite').basic_buffer.tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    SQL_Q = "SELECT {} AS cls, geometry FROM {} WHERE {}"
    clsRst = {}
    
    def exportAndBufferB(CLS, cnt):
        # Run BUFFER Tool
        time_x = datetime.datetime.now().replace(microsecond=0)
        bb_file = st_buffer(
            osmLink, lineTbl, "bf_basic_buffer", "geometry",
            os.path.join(folder, 'bb_rule5_{}.shp'.format(str(int(CLS)))),
            whrClause="basic_buffer={}".format(str(int(CLS))),
            outTblIsFile=True, dissolve=None, cols_select="basic_buffer"
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        # To raster
        rstCls = shp_to_raster(
            bb_file, None, cells, 0,
            os.path.join(folder, 'rst_bbfr_{}.tif'.format(CLS)),
            epsg=srscode, rst_template=rtemplate, api='gdal'
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[CLS] = rstCls
        timeGasto[cnt + 1] = ('buffer_{}'.format(str(CLS)), time_y - time_x)
        timeGasto[cnt + 2] = ('torst_{}'.format(str(CLS)), time_z - time_y)
    
    thrds = [Thread(
        name="r5-{}".format(lulcCls[i]), target=exportAndBufferB,
        args=(lulcCls[i], (i+1) * 10)
    ) for i in range(len(lulcCls))]
    
    for t in thrds: t.start()
    for t in thrds: t.join()
    
    return clsRst, timeGasto


def arcg_buffering(lineTbl, nomenclature):
    """
    Create a beautiful buffer from osm line features
    """
    
    from gasp.osm2lulc.utils     import osm_features_by_rule
    from gasp.cpu.arcg.anls.exct import select_by_attr
    from gasp.anls.prox.bf       import _buffer
    from gasp.cpu.arcg.mng.gen   import delete
    from gasp.prop.feat          import feat_count
    
    KEY_COL   = DB_SCHEMA["OSM_FEATURES"]["OSM_KEY"]
    VALUE_COL = DB_SCHEMA["OSM_FEATURES"]["OSM_VALUE"]
    LULC_COL  = DB_SCHEMA[nomenclature]["CLS_FK"]
    BF_COL    = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"]
    
    # Get OSM Features to be selected for this rule
    osmToSelect = osm_features_by_rule(nomenclature, 'basic_buffer')
    
    osmToSelect[VALUE_COL] = osmToSelect[KEY_COL] + "='" + \
        osmToSelect[VALUE_COL] + "'"
    
    # Get LULC Classes to be selected
    lulcCls = osmToSelect[LULC_COL].unique()
    
    resCls = {}
    WORK = os.path.dirname(lineTbl)
    for cls in lulcCls:
        filterDf = osmToSelect[osmToSelect[LULC_COL] == cls]
        
        # Get distances for this cls
        distances = filterDf[BF_COL].unique()
        
        for dist in distances:
            __filter = filterDf[filterDf[BF_COL] == dist]
            
            fShp = select_by_attr(
                lineTbl,
                str(__filter[VALUE_COL].str.cat(sep=" OR ")),
                os.path.join(
                    WORK, "buf_{}_{}".format(str(cls), str(int(dist)))
                )
            )
            
            if not feat_count(fShp, gisApi='arcpy'): continue
            
            bfShp = _buffer(
                fShp, str(dist).replace('.', ','), os.path.join(
                    WORK, "bufbf_{}_{}".format(
                        str(cls), str(dist).replace(".", "_"))
                ),
                api='arcpy', dissolve="ALL"
            )
            
            if cls not in resCls:
                resCls[int(cls)] = [bfShp]
            
            else:
                resCls[int(cls)].append(bfShp)
            
            delete(fShp)
    
    return resCls


def water_lines_to_polygon():
    """
    Convert OSM Lines to Polygons expressing existence of water bodies
    with the help of Sattelite imagery and Normalized Difference Watter
    Index.
    """
    
    """
    Procedure:
    1 - Apply NWDI
    2 - Reclassify: Water - 1; No Water - NoData
    3 - Region Group
    4 - See if Water Lines overlap Water Regions and which regions
    4.1 - Regions overlaped with Water Lines are considered as water bodies
    """
    
    return None

