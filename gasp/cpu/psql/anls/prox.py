"""
Tools for process geographic data on PostGIS
"""

from gasp.cpu.psql import connection


def st_near(link, inTbl, inTblPK, inGeom, nearTbl, nearGeom, output,
            near_col='near', untilDist=None, colsInTbl=None, colsNearTbl=None):
    """
    Near tool for PostGIS
    """
    
    from gasp import goToList
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    _out = ntbl_by_query(link, output, (
        "SELECT DISTINCT ON (s.{colPk}) "
        "{inTblCols}, {nearTblCols}"
        "ST_Distance("
            "s.{ingeomCol}, h.{negeomCol}"
        ") AS {nearCol} FROM {in_tbl} AS s "
        "LEFT JOIN {near_tbl} AS h "
        "ON ST_DWithin(s.{ingeomCol}, h.{negeomCol}, {dist_v}) "
        "ORDER BY s.{colPk}, ST_Distance(s.{ingeomCol}, h.{negeomCol})"
    ).format(
        colPk=inTblPK,
        inTblCols="s.*" if not colsInTbl else ", ".join([
            "s.{}".format(x) for x in goToList(colsInTbl)
        ]),
        nearTblCols="" if not colsNearTbl else ", ".join([
            "h.{}".format(x) for x in goToList(colsNearTbl)
        ]) + ", ",
        ingeomCol=inGeom, negeomCol=nearGeom,
        nearCol=near_col, in_tbl=inTbl, near_tbl=nearTbl,
        dist_v="100000" if not untilDist else untilDist
    ))
    
    
    return output


def st_near2(link, inTbl, inGeom, nearTbl, nearGeom, output,
            near_col='near'):
    """
    Near tool for PostGIS
    """
    
    from gasp                 import goToList
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    _out = ntbl_by_query(link, output, (
        "SELECT m.*, ST_Distance(m.{ingeom}, j.geom) AS {distCol} "
        "FROM {t} AS m, ("
            "SELECT ST_UnaryUnion(ST_Collect({neargeom})) AS geom "
            "FROM {tblNear}"
        ") AS j"
    ).format(
        ingeom=inGeom, distCol=near_col, t=inTbl, neargeom=nearGeom,
        tblNear=nearTbl
    ))
    
    
    return output


def st_buffer(conParam, inTbl, bfDist, geomCol, outTbl, bufferField="geometry",
              whrClause=None, dissolve=None, cols_select=None, outTblIsFile=None):
    """
    Using Buffer on PostGIS Data
    """
    
    from gasp import goToList
    
    dissolve = goToList(dissolve) if dissolve != "ALL" else "ALL"
    
    SEL_COLS = "" if not cols_select else ", ".join(goToList(cols_select))
    DISS_COLS = "" if not dissolve or dissolve == "ALL" else ", ".join(dissolve)
    GRP_BY = "" if not dissolve else "{}, {}".format(SEL_COLS, DISS_COLS) if \
        SEL_COLS != "" and DISS_COLS != "" else SEL_COLS \
        if SEL_COLS != "" else DISS_COLS if DISS_COLS != "" else ""
    
    Q = (
        "SELECT{sel}{spFunc}{geom}, {_dist}{endFunc} AS {bf} "
        "FROM {t}{whr}{grpBy}"
    ).format(
        sel = " " if not cols_select else " {}, ".format(SEL_COLS),
        spFunc="ST_Buffer(" if not dissolve else \
            "ST_UnaryUnion(ST_Collect(ST_Buffer(",
        geom=geomCol, _dist=bfDist,
        endFunc=")" if not dissolve else ")))",
        t=inTbl,
        grpBy=" GROUP BY {}".format(GRP_BY) if GRP_BY != "" else "",
        whr="" if not whrClause else " WHERE {}".format(whrClause),
        bf=bufferField
    )
    
    if not outTblIsFile:
        from gasp.cpu.psql.mng.qw import ntbl_by_query
        
        outTbl = ntbl_by_query(conParam, outTbl, Q)
    else:
        from gasp.to.shp import psql_to_shp
        
        psql_to_shp(
            conParam, Q, outTbl, api='pgsql2shp',
            geom_col=bufferField, tableIsQuery=True
        )
    
    return outTbl

