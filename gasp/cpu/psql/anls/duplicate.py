"""
Use duplicates in tables
"""


def show_duplicates_in_xls(conParam, table, pkCols, outFile,
                           tableIsQuery=None):
    """
    Find duplicates and write these objects in a table
    """
    
    import pandas
    
    from gasp         import goToList
    from gasp.fm.psql import sql_query
    from gasp.to.xls  import df_to_xls
    
    pkCols = goToList(pkCols)
    
    if not pkCols:
        raise ValueError("pkCols value is not valid")
    
    if not tableIsQuery:
        q = (
            "SELECT {t}.* FROM {t} INNER JOIN ("
                "SELECT {cls}, COUNT({cnt}) AS conta FROM {t} "
                "GROUP BY {cls}"
            ") AS foo ON {rel} "
            "WHERE conta > 1"
        ).format(
            t=table, cls=", ".join(pkCols), cnt=pkCols[0],
            rel=" AND ".join([
                "{t}.{c} = foo.{c}".format(t=table, c=col) for col in pkCols
            ])
        )
    
    else:
        q = (
            "SELECT foo.* FROM ({q_}) AS foo INNER JOIN ("
                "SELECT {cls}, COUNT({cnt}) AS conta "
                "FROM ({q_}) AS foo2 GROUP BY {cls}"
            ") AS jt ON {rel} "
            "WHERE conta > 1" 
        ).format(
            q_=table, cls=", ".join(pkCols), cnt=pkCols[0],
            rel=" AND ".join([
                "foo.{c} = jt.{c}".format(c=x) for x in pkCols
            ])
        )
    
    data = pandas.DataFrame(sql_query(conParam, q), columns=pkCols)
    
    df_to_xls(data, outFile)
    
    return outFile

