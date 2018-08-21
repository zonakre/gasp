"""
Rule 1 - Selection
"""

def grs_rst(osmdata, polyTbl):
    """
    Simple selection, convert result to Raster
    """
    
    import datetime
    from gasp.fm.sqLite  import sqlq_to_df
    from gasp.to.shp.grs import sqlite_to_shp
    from gasp.to.rst.grs import shp_to_raster
    
    # Get Classes 
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = sqlq_to_df(osmdata, (
        "SELECT selection FROM {} "
        "WHERE selection IS NOT NULL "
        "GROUP BY selection"
    ).format(polyTbl)).selection.tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    # Import data into GRASS and convert it to raster
    clsRst = {}
    tk = 1
    for cls in lulcCls:
        time_x = datetime.datetime.now().replace(microsecond=0)
        grsVect = sqlite_to_shp(
            osmdata, polyTbl, "rule1_{}".format(str(cls)),
            where="selection = {}".format(str(cls)), notTable=True
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        grsRst = shp_to_raster(
            grsVect, "rst_rule1_{}".format(str(cls)),
            int(cls), as_cmd=True
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[int(cls)] = grsRst
        timeGasto[tk] = ('import_{}'.format(cls), time_y - time_x)
        timeGasto[tk+1] = ('torst_{}'.format(cls), time_z - time_y)
        
        tk += 2
    
    return clsRst, timeGasto


def grs_vector(osmdata, polyTable):
    """
    Simple Selection using GRASS GIS
    """
    
    import datetime
    from gasp.cpu.grs.mng.genze import dissolve
    from gasp.cpu.grs.mng.tbl   import add_table
    from gasp.sqLite.i          import count_rows_in_query
    from gasp.to.shp.grs        import sqlite_to_shp
    
    WHR = "selection IS NOT NULL"
    
    # Check if we have interest data
    time_a = datetime.datetime.now().replace(microsecond=0)
    N = count_rows_in_query(osmdata, polyTable, where=WHR)
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not N: return None, {0 : ('count_rows', time_b - time_a)}
    
    # Data to GRASS GIS
    grsVect = sqlite_to_shp(osmdata, polyTable, "sel_rule", where=WHR)
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    dissVect = dissolve(
        grsVect, "diss_sel_rule", field="selection", asCMD=True)
    
    add_table(dissVect, None, lyrN=1, asCMD=True)
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    return dissVect, {
        0 : ('count_rows', time_b - time_a),
        1 : ('import', time_c - time_b),
        2 : ('dissolve', time_d - time_c)
    }


def num_selection(osmdata, polyTbl, folder,
                  cellsize, srscode, rstTemplate):
    """
    Select and Convert to Raster
    """
    
    import datetime;            import os
    from threading              import Thread
    from gasp.fm.sqLite         import sqlq_to_df
    from gasp.cpu.gdl.anls.exct import sel_by_attr
    from gasp.to.rst.gdl        import shp_to_raster
    
    # Get classes in data
    time_a = datetime.datetime.now().replace(microsecond=0)
    classes = sqlq_to_df(osmdata, (
        "SELECT selection FROM {} "
        "WHERE selection IS NOT NULL "
        "GROUP BY selection"
    ).format(polyTbl)).selection.tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    # Select and Export
    clsRst = {}
    SQL_Q = "SELECT {lc} AS cls, geometry FROM {tbl} WHERE selection={lc}"
    def FilterAndExport(CLS, cnt):
        time_x = datetime.datetime.now().replace(microsecond=0)
        shp = sel_by_attr(
            osmdata, SQL_Q.format(lc=str(CLS), tbl=polyTbl),
            os.path.join(folder, 'sel_{}.shp'.format(str(CLS)))
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        rstCls = shp_to_raster(
            shp, cellsize, -1,
            os.path.join(folder, 'sel_{}.tif'.format(str(CLS))),
            srscode, rstTemplate
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        clsRst[int(CLS)] = rstCls
        timeGasto[cnt + 1] = ('toshp_{}'.format(str(CLS)), time_y - time_x)
        timeGasto[cnt + 2] = ('torst_{}'.format(str(CLS)), time_z - time_y)
    
    trs = []
    for i in range(len(classes)):
        trs.append(Thread(
            name="lll{}".format(str(classes[i])),
            target=FilterAndExport, args=(classes[i], (i+1) * 10)
        ))
    
    for t in trs: t.start()
    for t in trs: t.join()
    
    return clsRst, timeGasto


def arcg_selection(db, polTbl, fld):
    """
    Select, Dissolve and Reproject using ArcGIS
    """
    
    import datetime;            import os
    from gasp.mng.genze         import dissolve
    from gasp.fm.sqLite         import sqlq_to_df
    from gasp.cpu.gdl.anls.exct import sel_by_attr
    
    # Get LULC Classes
    time_a = datetime.datetime.now().replace(microsecond=0)
    lulcCls = sqlq_to_df(db, (
        "SELECT selection FROM {} "
        "WHERE selection IS NOT NULL GROUP BY selection"
    ).format(polTbl)).selection.tolist()
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    timeGasto = {0 : ('check_cls', time_b - time_a)}
    
    # Extract Shps from DB
    clsShp = {}
    tk = 1
    SQL = "SELECT selection, geometry FROM {} WHERE selection={}"
    for cls in lulcCls:
        time_x = datetime.datetime.now().replace(microsecond=0)
        shp = sel_by_attr(
            db, SQL.format(polTbl, str(cls)),
            os.path.join(fld, 'rule1_{}.shp'.format(cls))
        )
        time_y = datetime.datetime.now().replace(microsecond=0)
        
        dShp = dissolve(
            shp, os.path.join(fld, "rul1_d_{}.shp".format(str(cls))),
            "FID", geomMultiPart=True
        )
        time_z = datetime.datetime.now().replace(microsecond=0)
        
        clsShp[int(cls)] = dShp
        timeGasto[tk]   = ("export_{}".format(cls), time_y - time_x)
        timeGasto[tk+1] = ("dissolve_{}".format(cls), time_z - time_y)
        
        tk += 2
    
    return clsShp, timeGasto

