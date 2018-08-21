"""
Write new tables
"""

from gasp          import goToList
from gasp.cpu.psql import connection


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

    __logic_operator = ' OR ' if logic_operator == 'OR' else ' AND ' \
        if logic_operator == 'AND' else None

    if not __logic_operator:
        raise ValueError((
            'Defined operator is not valid.\n '
            'The valid options are \'OR\' and \'AND\'')
        )

    con = connection(con_pgsql)

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
    
    con = connection(con_pgsql)
    
    cursor = con.cursor()
    
    cursor.execute(
        "UPDATE {t} SET {nullF}=COALESCE({repF}) WHERE {nullF} IS NULL".format(
            t=pgtable, nullF=nullFld, repF=replaceFld
        )
    )
    
    con.commit()
    cursor.close()
    con.close()


def write_new_table(lnk, pgtable, outtable, where=None,
                    cols_to_mantain=None, pk_cols=None):
    """
    Execute a query and write a new table
    """
    
    con = connection(lnk)
    
    curs = con.cursor()
    
    whr = "" if not where else " WHERE {}".format(where)
    
    cols_to_mantain = '*' if not cols_to_mantain else ', '.join(
        goToList(cols_to_mantain)
    )
    
    curs.execute(
        "CREATE TABLE {} AS SELECT {} FROM {}{};".format(
            outtable, cols_to_mantain, pgtable, whr
        )
    )
    
    if pk_cols:
        pk_cols = goToList(pk_cols)
        curs.execute((
            "ALTER TABLE {t} ADD CONSTRAINT {t}_pk PRIMARY KEY"
            " ({cols})"
        ).format(t=outtable, cols=', '.join(pk_cols)))
    
    con.commit()
    curs.close()
    con.close()
    
    return outtable


def ntbl_by_query(lnk, outbl, query):
    """
    Create table by query
    """
    
    con = connection(lnk)
    
    curs = con.cursor()
    
    _q = "CREATE TABLE {} AS {}".format(outbl, query)
    
    curs.execute(_q)
    
    con.commit()
    curs.close()
    con.close()
    
    return outbl


def distinct_to_table(lnk, pgtable, columns, outable):
    """
    Distinct values of one column to a new table
    """
    
    con = connection(lnk)
    
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


def exec_write_q(conPGSQL, queries):
    """
    Execute Queries and save result in the database
    """
    
    from gasp import goToList
    
    qs = goToList(queries)
    
    if not qs:
        raise ValueError("queries value is not valid")
    
    con = connection(conPGSQL)
    
    cs = con.cursor()
    
    for q in qs:
        cs.execute(q)
    
    con.commit()
    cs.close()
    con.close()

