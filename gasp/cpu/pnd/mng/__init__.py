"""
Manage Pandas DataFrame
"""

def split_df(df, N):
    """
    Split Dataframe making each sub dataframe
    having only N rows
    """
    
    __len = int(df.shape[0])
    
    if __len < N:
        L = [df]
    
    else:
        L= []
        for i in range(0, __len, N):
            if i + N < __len:
                L.append(df.iloc[i:i+N])
            else:
                L.append(df.iloc[i:__len])
    
    return L


def split_df_inN(df, N_new_Df):
    """
    Split df in several dataframe in number equal to N_new_Df
    """
    
    __len = float(df.shape[0])
    
    N = int(round(__len / N_new_Df, 0))
    
    return split_df(df, N)


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


def same_attr_to_shp(inShps, interestCol, outFolder, basename="data_",
                     resultDict=None):
    """
    For several SHPS with the same field, this program will list
    all values in such field and will create a new shp for all
    values with the respective geometry regardeless the origin shp.
    """
    
    import os
    from gasp         import goToList
    from gasp.fm.shp  import shp_to_df
    from gasp.mng.gen import merge_df
    from gasp.to.shp  import df_to_shp
    
    EXT = os.path.splitext(inShps[0])[1]
    
    shpDfs = [shp_to_df(shp) for shp in inShps]
    
    DF = merge_df(shpDfs, ignIndex=True)
    #DF.dropna(axis=0, how='any', inplace=True)
    
    uniqueVal = DF[interestCol].unique()
    
    nShps = [] if not resultDict else {}
    for val in uniqueVal:
        ndf = DF[DF[interestCol] == val]
        
        KEY = str(val).split('.')[0] if '.' in str(val) else str(val)
        
        nshp = df_to_shp(ndf, os.path.join(
            outFolder, '{}{}{}'.format(basename, KEY, EXT)
        ))
        
        if not resultDict:
            nShps.append(nshp)
        else:
            nShps[KEY] = nshp
    
    return nShps

