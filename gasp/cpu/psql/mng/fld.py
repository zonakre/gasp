"""
Manage fields
"""

from gasp.cpu.psql        import connection
from gasp.cpu.psql.mng.qw import ntbl_by_query


def pgsql_map_pgtypes(oid, python=True):
    """
    Relation between the oid and typename of the pg_type table
    
    To get the type associated to the key (oid), use:
    SELECT oid, typname FROM pg_type WHERE oid=18;
    """
    
    index = 1 if not python else 0
    
    pg_types = {
        18     : [str,        'text'],
        20     : [int,        'integer'],
        21     : [int,        'integer'],
        23     : [int,        'integer'],
        25     : [str,        'text'],
        700    : [float,      'decimal'],
        701    : [float,      'decimal'],
        1043   : [str,        'text'],
        1700   : [float,       'numeric'],
        16400  : ['geometry', 'geometry'],
        18013  : ['geometry', 'geometry'],
        18823  : ['geometry', 'geometry'],
        20155  : [str,        'hstore'],
        24270  : [str,        'hstore'],
        28386  : [str,        'hstore'],
        29254  : [str,        'hstore'],
        38467  : [str,        'hstore'],
        77768  : ['geometry', 'geometry'],
        147348 : ['geometry', 'geometry'],
        157351 : ['geometry', 'geometry'],
        244228 : ['geometry', 'geometry'],
        321695 : ['geometry', 'geometry']
    }
    
    if oid not in pg_types and oid >= 100000:
        return 'geometry'
    
    elif oid not in pg_types and (oid > 20155 and oid < 38467):
        if python:
            return str
        else:
            return 'text'
    
    elif oid not in pg_types and oid < 100000:
        raise ValueError('OID {} not in pg_types'.format(str(oid)))
    
    return pg_types[oid][index]


def pandas_maps_pgtypes(type_):
    __types = {
        'int32'   : 'bigint',
        'int64'   : 'bigint',
        'float32' : 'decimal',
        'float64' : 'decimal',
        'object'  : 'text'
    }
    
    return __types[type_]


def add_field(lnk, pgtable, columns):
    """
    Add new field to a table
    """
    
    # Verify is columns is a dict
    if type(columns) != dict:
        raise ValueError(
            'columns should be a dict (name as keys; field type as values)'
        )
    
    con = connection(lnk)
    
    cursor = con.cursor()
    
    cursor.execute(
        "ALTER TABLE {} ADD {};".format(
            pgtable,
            ", ".join(["{} {}".format(x, columns[x]) for x in columns])
        )
    )
    
    con.commit()
    cursor.close()
    con.close()


def drop_column(lnk, pg_table, columns):
    """
    Delete column from pg_table
    """
    
    from gasp import goToList
    
    con = connection(lnk)
    
    cursor = con.cursor()
    
    columns = goToList(columns)
    
    cursor.execute('ALTER TABLE {} {};'.format(
        pg_table, ', '.join(['DROP COLUMN {}'.format(x) for x in columns])
    ))
    
    con.commit()
    cursor.close()
    con.close()


def cols_name(postDic, table, sanitizeSpecialWords=True):
    """
    Return the columns names of a PostgreSQL table
    """
    
    from gasp.cpu.psql import pgsql_special_words
    
    c = connection(postDic)
    
    cursor = c.cursor()
    cursor.execute("SELECT * FROM {} LIMIT 50;".format(table))
    colnames = [desc[0] for desc in cursor.description]
    
    if sanitizeSpecialWords:
        # Prepare one wayout for special words
        special_words = pgsql_special_words()
    
        for i in range(len(colnames)):
            if colnames[i] in special_words:
                colnames[i] = '"{}"'.format(colnames[i])
    
    return colnames


def get_columns_type(pgsqlDic, table, sanitizeColName=True, pyType=True):
    """
    Return columns names and types of a PostgreSQL table
    """
    
    from gasp.cpu.psql import pgsql_special_words
    
    c = connection(pgsqlDic)
    
    cursor = c.cursor()
    cursor.execute("SELECT * FROM {} LIMIT 50;".format(table))
    coltypes = {
        desc[0]: pgsql_map_pgtypes(
            desc[1], python=pyType) for desc in cursor.description
    }
    
    
    if sanitizeColName:
        # Prepare one wayout for special words
        special_words = pgsql_special_words()
        
        for name in coltypes:
            if name in special_words:
                n = '"{}"'.format(name)
                coltypes[n] = coltypes[name]
                del coltypes[name]
    
    return coltypes


def pgtypes_from_pandasdf(df):
    """
    Get PGTypes from pandas dataframe
    """
    
    dataTypes = dict(df.dtypes)
    
    return {col : pandas_maps_pgtypes(
        str(dataTypes[col])) for col in dataTypes}


def change_field_type(lnk, table, fields, outable,
                        cols=None):
    """
    Imagine a table with numeric data saved as text. This method convert
    that numeric data to a numeric field.
    
    fields = {'field_name' : 'field_type'}
    """
    
    if not cols:
        cols = cols_name(lnk, table)
    
    else:
        from gasp import goToList
        
        cols = goToList(cols)
    
    select_fields = [f for f in cols if f not in fields]
    
    con = connection(lnk)
    
    # Create new table with the new field with converted values
    cursor = con.cursor()
    
    cursor.execute((
        'CREATE TABLE {} AS SELECT {}, {} FROM {}'
    ).format(
        outable,
        ', '.join(select_fields),
        ', '.join(['CAST({f_} AS {t}) AS {f_}'.format(
            f_=f, t=fields[f]) for f in fields
        ]),
        table
    ))
    
    con.commit()
    cursor.close()
    con.close()


def split_column_value_into_columns(lnkPgsql, table, column, splitChar,
                                    new_cols, new_table):
    """
    Split column value into several columns
    """
    
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    if type(new_cols) != list:
        raise ValueError(
            'new_cols should be a list'
        )
    
    nr_cols = len(new_cols)
    
    if nr_cols < 2:
        raise ValueError(
            'new_cols should have 2 or more elements'
        )
    
    # Get columns types from table
    tblCols = cols_name(lnkPgsql, table)
    
    # SQL construction
    SQL = "SELECT {}, {} FROM {}".format(
        ", ".join(tblCols),
        ", ".join([
            "split_part({}, '{}', {}) AS {}".format(
                column, splitChar, i+1, new_cols[i]
            ) for i in range(len(new_cols))
        ]),
        table
    )
    
    ntbl_by_query(lnkPgsql, new_table, SQL)
    
    return new_table


def text_columns_to_column(conParam, inTable, columns, strSep, newCol, outTable=None):
    """
    Several text columns to a single column
    """
    
    from gasp                 import goToList
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    mergeCols = goToList(columns)
    
    tblCols = get_columns_type(
        conParam, inTable, sanitizeColName=None, pyType=False)
    
    for col in mergeCols:
        if tblCols[col] != 'text' and tblCols[col] != 'varchar':
            raise ValueError('{} should be of type text'.format(col))
    
    coalesce = ""
    for i in range(len(mergeCols)):
        if not i:
            coalesce += "COALESCE({}, '')".format(mergeCols[i])
        
        else:
            coalesce += " || '{}' || COALESCE({}, '')".format(
                strSep, mergeCols[i])
    
    
    if outTable:
        # Write new table
        colsToSelect = [_c for _c in tblCols if _c not in mergeCols]
        
        if not colsToSelect:
            sel = coalesce + " AS {}".format(newCol)
        else:
            sel = "{}, {}".format(
                ", ".join(colsToSelect), coalesce + " AS {}".format(newCol)
            )
        
        ntbl_by_query(
            conParam, outTable, "SELECT {} FROM {}".format(sel, inTable)
        )
        
        return outTable
    
    else:
        # Add column to inTable
        from gasp.cpu.psql.mng.qw import update_table
        
        add_field(conParam, inTable, {newCol : 'text'})
        
        update_table(
            conParam, inTable, {newCol : coalesce}
        )
        
        return inTable


def columns_to_timestamp(conParam, inTbl, dayCol, hourCol, minCol, secCol, newTimeCol,
                         outTbl, selColumns=None, whr=None):
    
    """
    Columns to timestamp column
    """
    
    from gasp                 import goToList
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    selCols = goToList(selColumns)
    
    sql = (
        "SELECT {C}, TO_TIMESTAMP("
            "COALESCE(CAST({day} AS text), '') || ' ' || "
            "COALESCE(CAST({hor} AS text), '') || ':' || "
            "COALESCE(CAST({min} AS text), '') || ':' || "
            "COALESCE(CAST({sec} AS text), ''), 'YYYY-MM-DD HH24:MI:SS'"
        ") AS {TC} FROM {T}{W}"
    ).format(
        C   = "*" if not selCols else ", ".join(selCols),
        day = dayCol, hor=hourCol, min=minCol, sec=secCol,
        TC  = newTimeCol, T=inTbl,
        W   = "" if not whr else " WHERE {}".format(whr)
    )
    
    ntbl_by_query(conParam, outTbl, sql)
    
    return outTbl


def trim_char_in_col(conParam, pgtable, cols, trim_str, outTable,
                     onlyTrailing=None, onlyLeading=None):
    """
    Python implementation of the TRIM PSQL Function
    
    The PostgreSQL trim function is used to remove spaces or set of
    characters from the leading or trailing or both side from a string.
    """
    
    from gasp                 import goToList
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    cols = goToList(cols)
    
    colsTypes = get_columns_type(conParam, pgtable,
                                 sanitizeColName=None, pyType=False)
    
    for col in cols:
        if colsTypes[col] != 'text' and colsTypes[col] != 'varchar':
            raise ValueError('{} should be of type text'.format(col))
    
    colsToSelect = [_c for _c in colsTypes if _c not in cols]
    
    tail_lead_str = "" if not onlyTrailing and not onlyLeading else \
        "TRAILING " if onlyTrailing and not onlyLeading else \
        "LEADING " if not onlyTrailing and onlyLeading else ""
    
    trimCols = [
        "TRIM({tol}{char} FROM {c}) AS {c}".format(
            c=col, tol=tail_lead_str, char=trim_str
        ) for col in cols
    ]
    
    if not colsToSelect:
        cols_to_select = "{}".format(", ".join(trimCols))
    else:
        cols_to_select = "{}, {}".format(
            ", ".join(colsToSelect), ", ".join(colsReplace)
        )
    
    ntbl_by_query(conParam, outTable,
        "SELECT {} FROM {}".format(colsToSelect, pgtable)
    )


def replace_char_in_col(conParam, pgtable, cols, match_str, replace_str, outTable):
    """
    Replace char in all columns in cols for the value of replace_str
    
    Python implementation of the REPLACE PSQL Function
    """
    
    from gasp                 import goToList
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    
    cols = goToList(cols)
    
    colsTypes = get_columns_type(conParam, pgtable,
                                 sanitizeColName=None, pyType=False)
    
    for col in cols:
        if colsTypes[col] != 'text' and colsTypes[col] != 'varchar':
            raise ValueError('{} should be of type text'.format(col))
    
    colsToSelect = [_c for _c in colsTypes if _c not in cols]
    
    colsReplace  = [
        "REPLACE({c}, '{char}', '{nchar}') AS {c}".format(
            c=col, char=match_str, nchar=replace_str
        ) for col in cols
    ]
    
    if not colsToSelect:
        cols_to_select = "{}".format(", ".join(colsReplace))
    else:
        cols_to_select = "{}, {}".format(
            ", ".join(colsToSelect), ", ".join(colsReplace))
    
    ntbl_by_query(conParam, outTable,
        "SELECT {cols} FROM {tbl}".format(
            cols  = cols_to_select,
            tbl   = pgtable
        )
    )
    
    return outTable


def substring_to_newfield(conParam, table, field, newCol,
                          idxFrom, idxTo):
    """
    Get substring of string by range
    """
    
    from gasp.to.psql import insert_query
    
    # Add new field to table
    add_field(conParam, table, {newCol : "text"})
    
    # Update table
    insert_query(conParam,
        ("UPDATE {tbl} SET {nf} = substring({f} from {frm} for {to}) "
         "WHERE {nf} IS NULL").format(
             tbl=table, nf=newCol, f=field, frm=idxFrom,
             to=idxTo
        )
    )
    
    return table


def add_geomtype_to_col(conParam, table, newCol, geomCol):
    """
    Add Geom Type to Column
    """
    
    from gasp.to.psql import insert_query
    
    # Add new field to table
    add_field(conParam, table, {newCol : "text"})
    
    insert_query(conParam, "UPDATE {} SET {} = ST_GeometryType({})".format(
        table, newCol, geomCol
    ))
    
    return table

