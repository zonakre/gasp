"""
MODULE: sqlite
"""


import sqlite3


def update_query(db, table, new_values, wherePairs, whrLogic="OR"):
    """
    Update SQLITE Table
    """
    
    conn = sqlite3.connect(db)
    cs   = conn.cursor()
    
    LOGIC_OPERATOR = " OR " if whrLogic == "OR" else " AND " \
        if whrLogic == "AND" else None
    
    if not LOGIC_OPERATOR:
        raise ValueError("whrLogic value is not valid")
    
    Q = "UPDATE {} SET {} WHERE {}".format(
        table, ", ".join(["{}={}".format(
            k, new_values[k]) for k in new_values
        ]),
        LOGIC_OPERATOR.join(["{}={}".format(
            k, wherePairs[k]) for k in wherePairs
        ])
    )
    
    cs.execute(Q)
    
    conn.commit()
    cs.close()
    conn.close()


def set_values_use_pndref(sqliteDB, table, colToUpdate,
                        pndDf, valCol, whrCol, newCol=None):
    """
    Update Column based on conditions
    
    Add distinct values in pndCol in sqliteCol using other column as Where
    """
    
    conn = sqlite3.connect(sqliteDB)
    cs   = conn.cursor()
    
    if newCol:
        cs.execute("ALTER TABLE {} ADD COLUMN {} integer".format(
            table, colToUpdate
        ))
    
    VALUES = pndDf[valCol].unique()
    
    for val in VALUES:
        filterDf = pndDf[pndDf[valCol] == val]
        
        cs.execute("UPDATE {} SET {}={} WHERE {}".format(
            table, colToUpdate, val,
            str(filterDf[whrCol].str.cat(sep=" OR "))
        ))
    
    conn.commit()
    cs.close()
    conn.close()


def exec_write_query(db, queries):
    """
    Execute Queries and save result in database
    """
    
    from gasp import goToList
    
    con = sqlite3.connect(db)
    cs  = con.cursor()
    
    qs = goToList(queries)
    
    if not qs:
        raise ValueError("queries value is not valid")
    
    for q in qs:
        cs.execute(q)
    
    con.commit()
    cs.close()
    con.close()

