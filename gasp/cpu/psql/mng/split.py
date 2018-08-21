"""
Split table methods
"""

def split_table_by_range(conP, table, row_number):
    """
    Split tables in several
    """
    
    from gasp.cpu.psql.mng.fld import cols_name
    from gasp.cpu.psql.i       import get_row_number
    from gasp.cpu.psql.mng.qw  import ntbl_by_query
    
    rowsN = get_row_number(conP, table)
    
    nrTables = int(rowsN / float(row_number)) + 1
    
    COLS = cols_name(conP, table)
    
    offset = 0
    for i in range(nrTables):
        ntbl_by_query(
            conP, '{}_{}'.format(table, str(i)),
            "SELECT * FROM {} ORDER BY {} OFFSET {} LIMIT {} ;".format(
                table, ', '.join(COLS), str(offset), str(row_number) 
            )
        )
        
        offset += row_number


def split_table_entity_number(conP, table, entity_field, entity_number):
    """
    Split tables in several using as reference a number of entities per table
    
    If a table has 1 000 000 entities and the entity_number is 250 000,
    this method will create four tables, each one with 250 000 entities.
    250 000 entities, not rows. Don't forget that the main table may have
    more than one reference to the same entity.
    """
    
    import pandas
    from gasp.fm.psql          import sql_query
    from gasp.cpu.psql.mng.qw  import write_new_table
    from gasp.cpu.psql.mng.fld import get_columns_type
    
    # Select entities in table
    entities = pandas.DataFrame(sql_query(
        conP,
        "SELECT {c} FROM {t} GROUP BY {c}".format(
            c=entity_field, t=table)
    ), columns=[entity_field])
    
    # Split entities into groups acoording entity_number
    entityGroup = []
    
    lower = 0
    high = entity_number
    while lower <= len(entities.index):
        if high > len(entities.index):
            high = len(entities.index)
        
        entityGroup.append(entities.iloc[lower : high])
        
        lower += entity_number
        high  += entity_number
    
    # For each dataframe, create a new table
    COLS_TYPE = get_columns_type(conP, table)
    
    c = 0
    for df in entityGroup:
        if COLS_TYPE[entity_field] != str:
            df[entity_field] = '{}='.format(entity_field) + df[entity_field].astype(str)
        else:
            df[entity_field] = '{}=\''.format(entity_field) + df[entity_field].astype(str) + '\''
        
        whr = ' OR '.join(df[entity_field])
        
        write_new_table(conP, table, '{}_{}'.format(table, str(c)), where=whr)
        
        c += 1


def split_table_by_col_distinct(conParam, pgtable, column):
    """
    Create a new table for each value in one column
    """
    
    from gasp.fm.psql          import sql_query
    from gasp.cpu.psql.mng.fld import get_columns_type
    from gasp.cpu.psql.mng.qw  import write_new_table
    
    fields_types = get_columns_type(conParam, pgtable)
    
    # Get unique values
    VALUES = sql_query(
        conParam,
        "SELECT {col} FROM {t} GROUP BY {col}".format(
            col=interest_column, t=pgtable
        )
    )
    
    whr = '{}=\'{}\'' if fields_types[interest_column] == str else '{}={}'
    
    for row in VALUES:
        write_new_table(
            conParam, pgtable, '{}_{}'.format(pgtable, str(row[0])),
            where=whr.format(interest_column, str(row[0]))
        )

