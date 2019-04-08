"""
Generalization tools using SpatiaLite
"""

def st_dissolve(db, table, geomColumn, outTable, whrClause=None,
                diss_cols=None, outTblIsFile=None, api='sqlite'):
    """
    Dissolve a Polygon table
    """
    
    from gasp import goToList
    
    diss_cols = goToList(diss_cols) if diss_cols else None
    geomcol = "geometry" if api == 'sqlite' else 'geom'
    
    sql = (
        "SELECT{selCols} ST_UnaryUnion(ST_Collect({geom})) AS {gout} "
        "FROM {tbl}{whr}{grpBy}"
    ).format(
        selCols="" if not diss_cols else " {},".format(", ".join(diss_cols)),
        geom=geomColumn, tbl=table,
        whr="" if not whrClause else " WHERE {}".format(whrClause),
        grpBy="" if not diss_cols else " GROUP BY {}".format(
            ", ".join(diss_cols)
        ), gout=geomcol
    )
    
    if outTblIsFile:
        if api == 'sqlite':
            from gasp.anls.exct import sel_by_attr
            
            sel_by_attr(db, sql, outTable, api_gis='ogr')
        
        elif api == 'psql':
            from gasp.to.shp import psql_to_shp
            
            psql_to_shp(
                db, table, outTable, api='pgsql2shp',
                geom_col=geomColumn, tableIsQuery=True
            )
    
    else:
        from gasp.sql.mng.qw import ntbl_by_query
        
        ntbl_by_query(
            db, outTable, sql, api='ogr2ogr' if api == 'sqlite' else 'psql'
        )
    
    return outTable

