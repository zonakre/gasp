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
    if apidb == 'POSTGIS':
        from gasp.fm.psql             import query_to_df as sqlq_to_df
        from gasp.cpu.psql.anls.prox  import st_buffer
    else:
        from gasp.fm.sqLite           import sqlq_to_df
        from gasp.cpu.gdl.splite.prox import st_buffer
    from gasp.to.rst.grs              import shp_to_raster
    from gasp.to.shp.grs              import shp_to_grs
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = sqlq_to_df(osmLink, (
        "SELECT basic_buffer FROM {} WHERE basic_buffer IS NOT NULL "
        "GROUP BY basic_buffer"
    ).format(lineTable)).basic_buffer.tolist()
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
            grsVect, "rbb_{}".format(int(cls)), int(cls), as_cmd=True
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
    from gasp.cpu.grs.anls.prox import Buffer
    from gasp.cpu.grs.mng.genze import dissolve
    from gasp.cpu.grs.mng.tbl   import add_table
    
    if api_db != 'POSTGIS':
        from gasp.to.shp.grs    import sqlite_to_shp as db_to_shp
        from gasp.sqLite.i      import count_rows_in_query as cnt_row
    else:
        from gasp.to.shp.grs import psql_to_grs    as db_to_shp
        from gasp.cpu.psql.i import get_row_number as cnt_row
    
    WHR = "basic_buffer IS NOT NULL"
    
    # Check if we have data
    time_a = datetime.datetime.now().replace(microsecond=0)
    N = cnt_row(osmdata, lineTbl, where=WHR)
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not N: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    grsVect = db_to_shp(
        osmdata, lineTbl, "bb_lnh", where=WHR, filterByReg=True
    )
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    grsBuf  = Buffer(grsVect, "line", "bf_basic_buffer", "bb_poly", cmdAS=True)
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    grsDiss = dissolve(grsBuf, "bb_diss", "basic_buffer", asCMD=True)
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
    from threading                import Thread
    if api=='SQLITE':
        from gasp.fm.sqLite           import sqlq_to_df
        from gasp.cpu.gdl.splite.prox import st_buffer
    else:
        from gasp.fm.psql import query_to_df as sqlq_to_df
        from gasp.cpu.psql.anls.prox import st_buffer
    from gasp.to.rst.gdl          import shp_to_raster
    
    # Get LULC Classes to be selected
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = sqlq_to_df(osmLink, (
        "SELECT basic_buffer FROM {} WHERE basic_buffer IS NOT NULL "
        "GROUP BY basic_buffer"
    ).format(lineTbl)).basic_buffer.tolist()
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
            bb_file, cells, 0,
            os.path.join(folder, 'rst_bbfr_{}.tif'.format(CLS)),
            srscode, rtemplate
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
    from gasp.cpu.arcg.anls.prox import Buffer
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
            
            bfShp = Buffer(
                fShp, os.path.join(
                    WORK, "bufbf_{}_{}".format(
                        str(cls), str(dist).replace(".", "_"))
                ),
                str(dist).replace('.', ','), dissolve="ALL"
            )
            
            if cls not in resCls:
                resCls[int(cls)] = [bfShp]
            
            else:
                resCls[int(cls)].append(bfShp)
            
            delete(fShp)
    
    return resCls

