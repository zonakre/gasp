"""
SQLITE Tables
"""

def new_table(sqlitedb, table, fields):
    """
    Create a table in a SQLITE DB
    """
    
    conn = sqlite3.connect(sqlitedb)
    cursor = conn.cursor()
    
    cursor.execute(
        "CREATE TABLE {} ({})".format(
            table,
            ', '.join([
                "{} {}".format(k, fields[k]) for k in fields
            ])
        )
    )
    
    conn.commit()
    
    cursor.close()
    conn.close()


def new_view(sqliteDb, newView, q):
    """
    Create view in a SQLITE DB
    """
    
    conn = sqlite3.connect(sqliteDb)
    cs = conn.cursor()
    
    cs.execute("CREATE VIEW {} AS {}".format(newView, q))
    
    conn.commit()
    cs.close()
    conn.close()
    
    return newView

