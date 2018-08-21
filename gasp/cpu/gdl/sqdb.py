"""
SQLITE DATABASE THINGS
"""


def create_new_table_by_query(sqdb, newTable, sql):
    """
    Execute a SQL Query in a SQLITE Database and store the result in the 
    same database.
    """
    
    from gasp import exec_cmd
    
    cmd = (
        'ogr2ogr -update -append -f "SQLite" {db} -nln "{nt}" '
        '-dialect sqlite -sql "{q}" {db}' 
    ).format(
        db=sqdb, nt=newTable, q=sql
    )
    
    outcmd = exec_cmd(cmd)

