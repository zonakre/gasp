"""
OGR Overlay with SpatialLite
"""

def intersect_point_with_polygon(sqDB, pntTbl, pntGeom,
                                 polyTbl, polyGeom, outTbl,
                                 pntSelect=None, polySelect=None,
                                 pntQuery=None, polyQuery=None,
                                 outTblIsFile=None):
    """
    Intersect Points with Polygons
    """
    
    import os
    
    if not pntSelect and not polySelect:
        raise ValueError("You have to select something")
    
    sql = (
        "SELECT {colPnt}{colPoly} FROM {pnt_tq} "
        "INNER JOIN {poly_tq} ON "
        "ST_Within({pnt}.{pnGeom}, {poly}.{pgeom})"
    ).format(
        colPnt  = pntSelect if pntSelect else "",
        colPoly = polySelect if polySelect and not pntSelect else \
            ", " + polySelect if polySelect and pntSelect else "",
        pnt_tq  = pntTbl if not pntQuery else pntQuery,
        poly_tq = polyTbl if not polyQuery else polyQuery,
        pnt     = pntTbl,
        poly    = polyTbl,
        pnGeom  = pntGeom,
        pgeom   = polyGeom
    )
    
    if outTblIsFile:
        from gasp.cpu.gdl.anls.exct import sel_by_attr
        
        sel_by_attr(sqDB, sql, outTbl)
    
    else:
        from gasp.cpu.gdl.sqdb import create_new_table_by_query
        
        create_new_table_by_query(sqDB, outTbl, sql)


def disjoint_polygons_rel_points(sqBD, pntTbl, pntGeom,
                                polyTbl, polyGeom, outTbl,
                                polySelect=None,
                                pntQuery=None, polyQuery=None,
                                outTblIsFile=None):
    """
    Get Disjoint relation
    """
    
    import os
    
    if not polySelect:
        raise ValueError("Man, select something!")
    
    sql = (
        "SELECT {selCols} FROM {polTable} WHERE ("
        "{polName}.{polGeom} not in ("
            "SELECT {polName}.{polGeom} FROM {pntTable} "
            "INNER JOIN {polTable} ON "
            "ST_Within({pntName}.{pntGeom_}, {polName}.{polGeom})"
        "))"
    ).format(
        selCols  = "*" if not polySelect else polySelect,
        polTable = polyTbl if not polyQuery else polyQuery,
        polGeom  = polyGeom,
        pntTable = pntTbl if not pntQuery else pntQuery,
        pntGeom_ = pntGeom,
        pntName  = pntTbl,
        polName  = polyTbl
    )
    
    if outTblIsFile:
        from gasp.cpu.gdl.anls.exct import sel_by_attr
        
        sel_by_attr(sqBD, sql, outTbl)
    
    else:
        from gasp.cpu.gdl.sqdb import create_new_table_by_query
        
        create_new_table_by_query(sqBD, outTbl, sql)

