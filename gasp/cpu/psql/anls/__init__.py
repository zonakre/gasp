"""
Query Analysis
"""

import os
import pandas

from gasp.fm.psql         import sql_query
from gasp.to.xls          import df_to_xls
from gasp.cpu.psql.mng.qw import ntbl_by_query

def get_distinct_values(lnk, pgtable, column):
    """
    Get distinct values in one column of one pgtable
    """
    
    from gasp import goToList
    
    data = sql_query(lnk,
        "SELECT {col} FROM {t} GROUP BY {col};".format(
            col=", ".join(goToList(column)), t=pgtable
        )
    )
    
    return data


def run_query_for_values_in_col(conParam, query,
                               table_interest_col, interest_col,
                               outworkspace):
    """
    Execute a query for each value in one column
    In each iteration, the values may participate in the query.
    
    Export the several tables to excel
    
    Example:
    ID_PERCURSO | PARAGEM |    DIA     | GEOM
        0       |   255   |'2018-01-01 | xxxx
        0       |   255   |'2018-01-01 | xxxx
        0       |   254   |'2018-01-01 | xxxx
        0       |   254   |'2018-01-01 | xxxx
        0       |   255   |'2018-01-02 | xxxx
        0       |   255   |'2018-01-02 | xxxx
        0       |   254   |'2018-01-02 | xxxx
        0       |   254   |'2018-01-02 | xxxx
    
    For a query as:
    SELECT ID_PERCURSO, PARAGEM, GEOM, DIA, COUNT(PARAGEM) AS conta FROM
    table WHERE DIA={} GROUP BY PARAGEM, GEOM, DIA;
    
    This method will generate two tables:
    First table:
    ID_PERCURSO | PARAGEM |    DIA     | GEOM | conta
         0     |   255   |'2018-01-01 | xxxx |   2
         0     |   254   |'2018-01-01 | xxxx |   2
    
    Second table:
    ID_PERCURSO | PARAGEM |    DIA     | GEOM | conta
          0     |   255   |'2018-01-02 | xxxx |   2
          0     |   254   |'2018-01-02 | xxxx |   2
    
    {} will be replaced for every value in the interest_column that will
    be iterated one by one
    """
    
    from gasp.fm.psql          import query_to_df
    from gasp.cpu.psql.mng.fld import get_columns_type
    from gasp.to.xls           import df_to_xls
    
    fields_types = get_columns_type(conParam, table_interest_col)
    
    # Get  unique values
    VALUES = sql_query(conParam,
        "SELECT {col} FROM {t} GROUP BY {col}".format(
            col=interest_col, t=table_interest_col
        )
    )
    
    # Aplly query for every value in VALUES
    # Write data in excel
    for value in VALUES:
        data = query_to_df(conParam, query.format(
            str(value[0]) if fields_types[interest_col] != str \
            and fields_types[interest_col] != unicode else \
            "'{}'".format(str(value[0]))
        ))
        
        df_to_xls(data,
            os.path.join(
                outworkspace,
                '{}_{}.xlsx'.format(table_interest_col, str(value[0]))
            )
        )


def get_rows_notin_query(conParam, tblA, tblB, joinCols, newTable,
                         cols_to_mantain=None, tblAisQuery=None,
                         tblBisQuery=None):
    """
    Get rows from tblA that are not present in tblB
    
    joinCols = {colTblA : colTblB}
    """
    
    from gasp             import goToList
    from gasp.pgsql.tbl.w import ntbl_by_query
    
    cols_to_mantain = goToList(cols_to_mantain)
    
    q = (
        "SELECT {cls} FROM {ta} LEFT JOIN {tb} ON "
        "{rel} WHERE {tblB}.{fldB} IS NULL"
    ).format(
        cls=cols_to_mantain if cols_to_mantain else "{}.*".format(tblA),
        ta=tblA if not tblAisQuery else tblAisQuery,
        tb=tblB if not tblBisQuery else tblBisQuery,
        rel=" AND ".join(["{ta}.{ca} = {tb}.{cb}".format(
            ta=tblA, tb=tblB, ca=k, cb=joinCols[k]
        ) for k in joinCols])
    )
    
    newTable = ntbl_by_query(conParam, newTable, q)
    
    return newTable

