"""
Write new tables or edit tables in Database
"""


def ntbl_by_query(lnk, outbl, query, ntblIsView=None, api='psql'):
    """
    Create table by query
    
    API's Available:
    * psql;
    * ogr2ogr
    """
    
    if api == 'psql':
        from gasp.sql.c import psqlcon
    
        con = psqlcon(lnk)
    
        curs = con.cursor()
    
        _q = "CREATE {} {} AS {}".format(
            "TABLE" if not ntblIsView else "VIEW",
            outbl, query
        )
    
        curs.execute(_q)
    
        con.commit()
        curs.close()
        con.close()
    
    elif api == 'ogr2ogr':
        """
        Execute a SQL Query in a SQLITE Database and store the result in the
        same database. Uses OGR2OGR instead of the regular SQLITE API
        """
        
        from gasp import exec_cmd
        
        cmd = (
            'ogr2ogr -update -append -f "SQLite" {db} -nln "{nt}" '
            '-dialect sqlite -sql "{q}" {db}' 
        ).format(
             db=lnk, nt=outbl, q=query
        )
        
        outcmd = exec_cmd(cmd)
    
    else:
        raise ValueError('API {} is not available!'.format(api))
    
    return outbl

def update_table(con_pgsql, pg_table, dic_new_values, dic_ref_values=None, 
                 logic_operator='OR'):
    """
    Update Values on a PostgreSQL table

    new_values and ref_values are dict with fields as keys and values as 
    keys values.
    If the values (ref and new) are strings, they must be inside ''
    e.g.
    dic_new_values = {field: '\'value\''}
    """
    
    from gasp.sql.c import psqlcon

    __logic_operator = ' OR ' if logic_operator == 'OR' else ' AND ' \
        if logic_operator == 'AND' else None

    if not __logic_operator:
        raise ValueError((
            'Defined operator is not valid.\n '
            'The valid options are \'OR\' and \'AND\'')
        )

    con = psqlcon(con_pgsql)

    cursor = con.cursor()
    
    if dic_ref_values:
        whrLst = []
        for x in dic_ref_values:
            if dic_ref_values[x] == 'NULL':
                whrLst.append('{} IS NULL'.format(x))
            else:
                whrLst.append('{}={}'.format(x, dic_ref_values[x]))
        
        whr = " WHERE {}".format(__logic_operator.join(whrLst))
    
    else:
        whr = ""

    update_query = "UPDATE {tbl} SET {pair_new}{where};".format(
        tbl=pg_table,
        pair_new=",".join(["{fld}={v}".format(
            fld=x, v=dic_new_values[x]) for x in dic_new_values]),
        where = whr
    )

    cursor.execute(update_query)

    con.commit()
    cursor.close()
    con.close()


def update_query(db, table, new_values, wherePairs, whrLogic="OR"):
    """
    Update SQLITE Table
    """
    
    import sqlite3
    
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


def replace_null_with_other_col_value(con_pgsql, pgtable, nullFld, replaceFld):
    """
    Do the following
    
    Convert the next table:
    FID | COL1 | COL2
     0  |  1   | -99
     1  |  2   | -99
     2  | NULL | -88
     3  | NULL | -87
     4  |  7   | -99
     5  |  9   | -99
     
    Into:
    FID | COL1 | COL2
     0  |  1   | -99
     1  |  2   | -99
     2  | -88  | -88
     3  | -87  | -87
     4  |  7   | -99
     5  |  9   | -99
    """
    
    con = psqlcon(con_pgsql)
    
    cursor = con.cursor()
    
    cursor.execute(
        "UPDATE {t} SET {nullF}=COALESCE({repF}) WHERE {nullF} IS NULL".format(
            t=pgtable, nullF=nullFld, repF=replaceFld
        )
    )
    
    con.commit()
    cursor.close()
    con.close()


def distinct_to_table(lnk, pgtable, columns, outable):
    """
    Distinct values of one column to a new table
    """
    
    con = psqlcon(lnk)
    
    cs = con.cursor()
    
    cs.execute(
        "CREATE TABLE {nt} AS SELECT {cls} FROM {t} GROUP BY {cls}".format(
            nt=outable, cls=', '.join(goToList(columns)),
            t=pgtable
        )
    )
    
    con.commit()
    cs.close()
    con.close()
    
    return outable


def exec_write_q(conDB, queries, api='psql'):
    """
    Execute Queries and save result in the database
    """
    
    from gasp import goToList
    
    qs = goToList(queries)
    
    if not qs:
        raise ValueError("queries value is not valid")
    
    if api == 'psql':
        from gasp.sql.c import psqlcon
        
        con = psqlcon(conDB)
    
        cs = con.cursor()
    
        for q in qs:
            cs.execute(q)
    
        con.commit()
        cs.close()
        con.close()
    
    elif api == 'sqlite':
        import sqlite3
        
        con = sqlite3.connect(conDB)
        cs  = con.cursor()
        
        for q in qs:
            cs.execute(q)
        
        con.commit()
        cs.close()
        con.close()
    
    else:
        raise ValueError('API {} is not available'.format(api))

