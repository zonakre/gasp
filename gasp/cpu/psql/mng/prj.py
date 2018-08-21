"""
Tools for process geographic data on PostGIS
"""


import os
import psycopg2

from gasp.cpu.psql import connection

def re_project(lnk, in_tbl, fld_geom, outEpsg, out_tbl,
               newgeom_fld=None, new_pk=None, colsSelect=None,
               whr=None):
    """
    Reproject geometric layer to another spatial reference system (srs)
    
    lnk is a dict with parameters for connecting to PostgreSQL
    tbl_geom is the table to project
    fld_geom is the column of the previous table with geometric data
    outEpsg is the srs of destiny
    out_tbl is the repreoject table (output)
    """
    
    from gasp                 import goToList
    from gasp.cpu.psql.pgkeys import create_pk
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    colsSelect = goToList(colsSelect)
    
    newGeom = newgeom_fld if newgeom_fld else fld_geom if \
        colsSelect else "proj_{}".format(fld_geom)
    
    ntbl_by_query(
        lnk, out_tbl,
        "SELECT {}, ST_Transform({}, {}) AS {} FROM {}{}".format(
            "*" if not colsSelect else ", ".join(colsSelect),
            fld_geom, str(outEpsg), newGeom, in_tbl,
            "" if not whr else " WHERE {}".format(whr)        
        )
    )
    
    if new_pk:
        create_pk(lnk, out_tbl, new_pk)
    
    return out_tbl

