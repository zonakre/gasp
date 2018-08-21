"""
Backup and restore PostgreSQL data
"""

from gasp import exec_cmd

def dump_table(conParam, table, outsql):
    """
    Dump one table into a SQL File
    """
    
    outcmd = exec_cmd((
        "pg_dump -Fc -U {user} -h {host} -p {port} "
        "-w -t {tbl} {db} > {out}"
    ).format(
        user=conParam["USER"], host=conParam["HOST"],
        port=conParam["PORT"], tbl=table,
        db=conParam["DATABASE"], out=outsql
    ))
    
    return outsql


def restore_table(conParam, sql, tablename):
    """
    Restore one table from a sql Script
    """
    
    outcmd = exec_cmd((
        "pg_restore -U {user} -h {host} -p {port} "
        "-w -t {tbl} -d {db} {sqls}"
    ).format(
        user=conParam["USER"], host=conParam["HOST"],
        port=conParam["PORT"], tbl=tablename,
        db=conParam["DATABASE"], sqls=sql
    ))
    
    return tablename
