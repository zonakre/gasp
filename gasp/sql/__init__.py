"""
SQL
"""


def pgsql_special_words():
    return ['table', 'column', 'natural', 'group', 'left', 'right', 'order']


def run_sql_file(lnk, database, sqlfile):
    """
    Run a sql file do whatever is on that script
    """
    
    from gasp import exec_cmd
    
    cmd = 'psql -h {host} -U {usr} -p {port} -w {db} < {sql_script}'.format(
        host = lnk['HOST'], usr = lnk['USER'], port = lnk['PORT'],
        db  = database    , sql_script = sqlfile
    )
    
    outcmd = exec_cmd(cmd)

