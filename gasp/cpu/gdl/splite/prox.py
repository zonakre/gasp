"""
Proximity operations
"""


def st_buffer(db, table, dist, geomField, outTbl,
              cols_select=None, bufferField="geometry",
              whrClause=None, outTblIsFile=None, dissolve=None):
    """
    Run ST_Buffer
    
    if not dissolve, no generalization will be applied; 
    if dissolve == to str or list, a generalization will be accomplish
    using the fields referenced by this object;
    if dissolve == 'ALL', all features will be dissolved.
    """
    
    from gasp import goToList
    
    dissolve = goToList(dissolve) if dissolve != "ALL" else "ALL"
    
    sql = (
        "SELECT{sel}{spFunc}{geom}, {_dist}{endFunc} AS {bf} "
        "FROM {tbl}{whr}{grpBy}"
    ).format(
        sel = " " if not cols_select else " {}, ".format(
            ", ".join(goToList(cols_select))
        ),
        tbl=table,
        geom=geomField, _dist=str(dist), bf=bufferField,
        whr="" if not whrClause else " WHERE {}".format(whrClause),
        spFunc="ST_Buffer(" if not dissolve else \
            "ST_UnaryUnion(ST_Collect(ST_Buffer(",
        endFunc = ")" if not dissolve else ")))",
        grpBy="" if not dissolve or dissolve == "ALL" else " GROUP BY {}".format(
            ", ".join(dissolve)
        )
    )
    
    if outTblIsFile:
        from gasp.cpu.gdl.anls.exct import sel_by_attr
        
        sel_by_attr(db, sql, outTbl)
    
    else:
        from gasp.cpu.gdl.sqdb import create_new_table_by_query
        
        create_new_table_by_query(db, outTbl, sql)
    
    return outTbl


def st_near(sqdb, tbl, nearTbl, tblGeom, nearGeom, output, whrNear=None,
            outIsFile=None):
    """
    Near Analysis using Spatialite
    """
    
    Q = (
        "SELECT m.*, ST_Distance(m.{inGeom}, j.geom) AS dist_near "
        "FROM {t} AS m, ("
            "SELECT ST_UnaryUnion(ST_Collect({neargeom})) AS geom "
            "FROM {tblNear}{nearwhr}"
        ") AS j"
    ).format(
        inGeom=tblGeom, t=tbl, neargeom=nearGeom, tblNear=nearTbl,
        nearwhr="" if not whrNear else " WHERE {}".format(whrNear)
    )
    
    if outIsFile:
        from gasp.cpu.gdl.anls.exct import sel_by_attr
        
        sel_by_attr(sqdb, Q, output)
    
    else:
        from gasp.cpu.gdl.sqdb import create_new_table_by_query
        
        create_new_table_by_query(sqdb, output, Q)
    
    return output

