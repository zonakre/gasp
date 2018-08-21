"""
Get information about things
"""

from gasp.cpu.psql import connection


"""
Databases Info
"""

def list_db(conParam):
    """
    List all PostgreSQL databases
    """
    
    con = connection(conParam)
    
    cursor = con.cursor()
    
    cursor.execute("SELECT datname FROM pg_database")
    
    return [d[0] for d in cursor.fetchall()]


def db_exists(lnk, db):
    """
    Database exists
    """
    con = connection(lnk)
        
    cursor = con.cursor()
    
    cursor.execute("SELECT datname FROM pg_database")
    
    dbs = [d[0] for d in cursor.fetchall()]
    
    return 1 if db in dbs else 0


"""
Tables Info
"""
def lst_tbl(dic_con, schema='public'):
    """
    list tables in a database
    """
    
    conn = connection(dic_con)
    
    cs = conn.cursor()
    cs.execute((
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='{s}'".format(s=schema)
    ))
    
    f = [x[0] for x in cs.fetchall()]
    
    cs.close()
    conn.close()
    
    return f


def lst_tbl_basename(basename, dic_con, schema='public'):
    """
    List tables with name that includes basename
    """
    
    conn = connection(dic_con)
    
    cs = conn.cursor()
    cs.execute((
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='{}' AND table_name LIKE '%{}%'".format(
            schema, basename
        )
    ))
    
    f = [x[0] for x in cs.fetchall()]
    
    cs.close()
    conn.close()
    
    return f


def check_last_id(lnk, pk, table):
    """
    Check last ID of a given table
    
    return 0 if there is no data
    
    TODO: Do this with Pandas
    """
    con = connection(lnk)
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


def get_row_number(conP, table):
    """
    Return the number of rows in a PostgreSQL table
    """
    
    from gasp.fm.psql import query_to_df
    
    d = query_to_df(conP, "SELECT COUNT(*) AS nrows FROM {}".format(table))
    
    return int(d.iloc[0].nrows)


"""
Geometric Properties
"""

def get_tbl_extent(conParam, table, geomCol):
    """
    Return extent of the geometries in one pgtable
    """
    
    from gasp.fm.psql import query_to_df
    
    q = (
        "SELECT MIN(ST_X(pnt_geom)) AS eleft, MAX(ST_X(pnt_geom)) AS eright, "
        "MIN(ST_Y(pnt_geom)) AS bottom, MAX(ST_Y(pnt_geom)) AS top "
        "FROM ("
            "SELECT (ST_DumpPoints({geomcol})).geom AS pnt_geom "
            "FROM {tbl}"
        ") AS foo"
    ).format(tbl=table, geomcol=geomCol)
    
    ext = query_to_df(conParam, q).to_dict(orient='index')[0]
    
    return [
        ext['eleft'], ext['bottom'], ext['eright'], ext['top']
    ]

