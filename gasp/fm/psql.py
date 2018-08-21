"""
PostgreSQL Database data to Python Object/Array
"""

from gasp.cpu.psql import connection

def sql_query(conParam, query, encoding=None):
    """
    Retrive data from a SQL query
    """
    conn = connection(conParam)
    
    if encoding:
        conn.set_client_encoding(encoding)
    
    cursor = conn.cursor()
    cursor.execute(query)
    table = cursor.fetchall()
    cursor.close()
    conn.close()
    return table


def pgtable_to_dict(pgTable, pgCon, sanitizeColsName=True, cols=None):
    """
    PG TABLE DATA to Python dict
    """
    
    from gasp                  import goToList
    from gasp.cpu.psql.mng.fld import cols_name
    
    cols = cols_name(pgCon, pgTable) if not cols else \
        goToList(cols)
    
    data = sql_query(
        pgCon,
        'SELECT {cols_} FROM {table}'.format(
            cols_=', '.join(cols),
            table=pgTable
        )
    )
    
    if not sanitizeColsName:
        from gasp.cpu.psql import pgsql_special_words
        for i in range(len(cols)):
            if cols[i][1:-1] in pgsql_special_words():
                cols[i] = cols[i][1:-1]
    
    return [
        {cols[i] : row[i] for i in range(len(cols))} for row in data
    ]


def sql_query_with_innerjoin(
    dic4con, main_table_lst, relation_table_lst,
    fld_of_interest, obj_of_interest, fields_to_select):
    """
    Select data based on it relation with something
    
    Applies the SQL INNERJOIN method
    
    * Table lists objects:
    [0] is the table name
    [1] is the foreign key column name
    """
    
    main_table, main_foreign = main_table_lst
    relate_table, relate_foreign = relation_table_lst
    
    con = connection(dic4con)
    
    obj_o_int = '\'{}\''.format(str(obj_of_interest)) if type(obj_of_interest) == str \
        or type(obj_of_interest) == unicode else str(obj_of_interest)
    
    table = sql_query(
        dic4con,
        ("SELECT {cols} FROM {m} INNER JOIN {r} ON {m}.{fld1_join} "
         "= {r}.{fld2_join} WHERE {fld}={c};").format(
            cols = ','.join(fields_to_select),
            m = main_table, fld1_join = main_foreign,
            r=relate_table, fld2_join = relate_foreign,
            fld = fld_of_interest, c = obj_o_int
        )
    )
    if len(fields_to_select) == 1:
        from itertools import chain
        l = list(chain.from_iterable(table))
    
    elif len(fields_to_select) == 2:
        l = dict(table)
    
    elif len(fields_to_select) > 2:
        l = dict([[k[0], k[1:]] for k in table])
    
    return l


def query_to_df(conParam, query):
    """
    Query database and convert data to Pandas Dataframe
    """
    import pandas
    from gasp.cpu.psql import alchemy_engine
    
    pgengine = alchemy_engine(conParam)
    
    df = pandas.read_sql(query, pgengine, columns=None)
    
    return df

def psql_to_geodf(conParam, query, geomCol='geom',
                    epsg=None):
    """
    Query database and convert data to Pandas GeoDataframe
    """
    
    from geopandas     import GeoDataFrame
    from gasp.cpu.psql import connection
    
    con = connection(conParam)
    
    df = GeoDataFrame.from_postgis(
        query, con, geom_col=geomCol,
        crs="epsg:{}".format(str(epsg)) if epsg else None
    )
    
    return df
