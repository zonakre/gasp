"""
Query methods
"""

from gasp.cpu.psql import connection

def create_pk(lnk, tbl, new_col):
    """
    Creates a new primary key field on a existent table
    """
    conn = connection(lnk)
    
    cs = conn.cursor()
    cs.execute(
        "ALTER TABLE {t} ADD COLUMN {new_fid} BIGSERIAL PRIMARY KEY;".format(
            t=tbl, new_fid=new_col
        )
    )
    conn.commit()
    cs.close()
    conn.close()


def pkIsValid(lnk, table, cols):
    """
    See if the given columns are a valid Primary Key
    
    TODO: We don't need Pandas
    """
    
    import pandas
    
    from gasp         import goToList
    from gasp.fm.psql import sql_query
    
    # Get data
    data = sql_query(lnk,
        "SELECT {} FROM {}".format(
            ', '.join(goToList(cols)), table
        )
    )
    
    # See if data have duplicated values
    tblDataFrame = pandas.DataFrame(data)
    dupDataFrame = tblDataFrame.drop_duplicates()
    
    if len(tblDataFrame) == len(dupDataFrame):
        return 'Given columns are a valid primary key'
    
    else:
        return 'Given columns are not a valid primary key'


def multiCols_FK_to_singleCol(conParam, tbl_wPk, pkCol, tbl_multiFk,
                              fkCols, newTable,
                              colsSel=None, whrCls=None):
    """
    For two tables as:
    
    Main table:
    PK | col_1 | col_2 | col_n
    1  |   0   |   0   |   0
    2  |   1   |   1   |   1
    3  |   0   |   2   |   2
    4  |   1   |   2   |   3
    
    Table with a foreign key with several columns:
    col_1 | col_2 | col_n
      0   |   0   |   0
      0   |   0   |   0
      0   |   2   |   2
      1   |   1   |   1
      1   |   2   |   3
      1   |   1   |   1
    
    Create a new table with a foreign key in a single column:
    col_1 | col_2 | col_n | FK
      0   |   0   |   0   | 1
      0   |   0   |   0   | 1
      0   |   2   |   2   | 3
      1   |   1   |   1   | 2
      1   |   2   |   3   | 4
      1   |   1   |   1   | 2
    
    In this example:
    pk_field = PK
    cols_foreign = {col_1 : col_1, col_2: col_2, col_n : col_n}
    (Keys are cols of tbl_wPk and values are cols of the tbl_multiFk
    """
    
    if type(fkCols) != dict:
        raise ValueError(
            "fkCols parameter should be a dict"
        )
    
    from gasp                 import goToList
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    colsSel = goToList(colsSel)
    
    q = (
        "SELECT {tpk}.{pk}, {cls} FROM {tfk} "
        "INNER JOIN {tpk} ON {tblRel}{whr}"
    ).format(
        tpk=tbl_wPk, pk=pkCol, tfk=tbl_multiFk,
        cls="{}.*".format(tbl_multiFk) if not colsSel else \
            ", ".join(["{}.{}".format(tbl_wPk, pkCol) for c in colsSel]),
        tblRel=" AND ".join([
            "{}.{} = {}.{}".format(
                tbl_multiFk, fkCols[k], tbl_wPk, k
            ) for k in fkCols
        ]),
        whr="" if not whrCls else " WHERE {}".format(whrCls)
    )
    
    outbl = ntbl_by_query(conParam, newTable, q)
    
    return outbl

