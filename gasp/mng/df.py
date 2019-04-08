"""
Manage Pandas DataFrame
"""


def col_list_val_to_row(pndDf, colWithLists, geomCol=None, epsg=None):
    """
    Convert a dataframe:
    
       | col_a | col_b | col_c
     0 |   X   |   X   |   1
     1 |   X   |   X   | [2,3]
     
    To:
       | col_a | col_b | col_c
     0 |   X   |   X   |   1
     1 |   X   |   X   |   2
     2 |   X   |   X   |   3
    """
    
    def desmembrate(row, row_acc, target_col):
        if type(row[target_col]) != list:
            row_acc.append(row.to_dict())
        
        else:
            for geom in row[target_col]:
                new_row = row.to_dict()
                new_row[target_col] = geom
                row_acc.append(new_row)
    
    new_rows = []
    pndDf.apply(lambda x: desmembrate(
        x, new_rows, colWithLists), axis=1
    )
    
    # Convert again to DataFrame
    if geomCol and epsg:
        from gasp.to.obj import obj_to_geodf
        
        return obj_to_geodf(new_rows, geomCol, epsg)
    
    else:
        import pandas
        
        return pandas.DataFrame(new_rows)


def df_groupBy(df, grpCols, STAT=None, STAT_FIELD=None):
    """
    Group By Pandas Dataframe
    
    STAT OPTIONS:
    * MIN
    * MAX
    """
    
    from gasp import goToList
    
    grpCols = goToList(grpCols)
    
    if not grpCols:
        raise ValueError("grpCols value is not valid")
    
    if not STAT:
        newDf = df.groupby(grpCols, axis=0, as_index=False)
    
    else:
        if not STAT_FIELD:
            raise ValueError("To use STAT, you must specify STAT_FIELD")
        
        if STAT == 'MIN':
            newDf = df.groupby(
                grpCols, axis=0, as_index=False
            )[STAT_FIELD].min()
        
        elif STAT == 'MAX':
            newDf = df.groupby(
                grpCols, axis=0, as_index=False
            )[STAT_FIELD].max()
        
        elif STAT == 'SUM':
            newDf = df.groupby(
                grpCols, axis=0, as_index=False
            )[STAT_FIELD].sum()
        
        else:
            raise ValueError("{} is not a valid option".format(STAT))
    
    return newDf

