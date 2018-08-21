"""
Generalization tools using SpatiaLite
"""

def st_dissolve(db, table, geomColumn, outTable, whrClause=None,
                diss_cols=None, outTblIsFile=None):
    """
    Dissolve a Polygon table
    """
    
    from gasp import goToList
    
    diss_cols = goToList(diss_cols) if diss_cols else None
    
    sql = (
        "SELECT{selCols} ST_UnaryUnion(ST_Collect({geom})) AS geometry "
        "FROM {tbl}{whr}{grpBy}"
    ).format(
        selCols="" if not diss_cols else " {}".format(", ".join(diss_cols)),
        geom=geomColumn, tbl=table,
        whr="" if not whrClause else " WHERE {}".format(whrClause),
        grpBy="" if not diss_cols else " GROUP BY {}".format(
            ", ".join(diss_cols)
        )
    )
    
    if outTblIsFile:
        from gasp.cpu.gdl.anls.exct import sel_by_attr
        
        sel_by_attr(db, sql, outTable)
    
    else:
        from gasp.cpu.gdl.sqdb import create_new_table_by_query
        
        create_new_table_by_query(db, outTable, sql)
    
    return outTable

