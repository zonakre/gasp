"""
Table Meta
"""

def check_last_id(lnk, pk, table):
    """
    Check last ID of a given table
    
    return 0 if there is no data
    
    TODO: Do this with Pandas
    """
    
    from gasp.sql.c import psqlcon
    
    con = psqlcon(lnk)
    cs = con.cursor()
    cs.execute(
        "SELECT {fid} FROM {tbl};".format(
            fid=pk, tbl=table
        )
    )
    f = [x[0] for x in cs.fetchall()]
    cs.close()
    con.close()
    if len(f) == 0:
        return 0
    else:
        return max(f)


"""
Geometric Properties
"""

def get_tbl_extent(conParam, table, geomCol):
    """
    Return extent of the geometries in one pgtable
    """
    
    from gasp.fm.sql import query_to_df
    
    q = (
        "SELECT MIN(ST_X(pnt_geom)) AS eleft, MAX(ST_X(pnt_geom)) AS eright, "
        "MIN(ST_Y(pnt_geom)) AS bottom, MAX(ST_Y(pnt_geom)) AS top "
        "FROM ("
            "SELECT (ST_DumpPoints({geomcol})).geom AS pnt_geom "
            "FROM {tbl}"
        ") AS foo"
    ).format(tbl=table, geomcol=geomCol)
    
    ext = query_to_df(conParam, q, db_api='psql').to_dict(orient='index')[0]
    
    return [
        ext['eleft'], ext['bottom'], ext['eright'], ext['top']
    ]

