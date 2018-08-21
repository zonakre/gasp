"""
Join Tables operations
"""


def join_dfs(df_a, df_b, colA, colB, onlyCombinations=True):
    """
    Join two Pandas Dataframes
    """
    
    from gasp import goToList
    
    _HOW_ = 'inner' if onlyCombinations else 'outer'
    
    if colA == 'index' and colB == 'index':
        newDf = df_a.merge(
            df_b, how=_HOW_, left_index=True, right_index=True
        )
    
    elif colA == 'index' and colB != 'index':
        newDf = df_a.merge(
            df_b, how=_HOW_, left_index=True,
            right_on=goToList(colB)
        )
    
    elif colA != 'index' and colB == 'index':
        newDf = df_a.merge(
            df_b, how=_HOW_, left_on=goToList(colA),
            right_index=True
        )
    
    else:
        newDf = df_a.merge(
            df_b, how=_HOW_, left_on=goToList(colA),
            right_on=goToList(colB)
        )
    
    return newDf


def sum_field_of_two_tables(df_one, join_field_one,
                            df_two, join_field_two,
                            field_to_sum):
    """
    Sum same field in different tables
    
    Table 1:
    id | field
    0 |  10
    1 |  11
    2 |  13
    3 |  10
    
    Table 2:
    id | field
    0 |  10
    1 |   9
    2 |  17
    4 |  15
    
    Create the new table
    id | field
    0 |  20
    1 |  20
    2 |  30
    3 |  10
    4 |  15
    """
    
    df_two.rename(columns={field_to_sum : 'sum_pro'}, inplace=True)
    
    if join_field_two == join_field_one:
        df_two.rename(columns={join_field_two : 'id_table_two'}, inplace=True)
        
        join_field_two = 'id_table_two'
    
    result = df_one.merge(
        df_two, how='outer', left_on=join_field_one, right_on=join_field_two
    )
    
    result.fillna(0, inplace=True)
    
    result[field_to_sum] = result[field_to_sum] + result['sum_pro']
    
    result[join_field_one].replace(0, result[join_field_two], inplace=True)
    
    result.drop(join_field_two, axis=1, inplace=True)
    result.drop('sum_pro', axis=1, inplace=True)
    
    return result


def combine_dfs(mainDf, joinDfs, int_col):
    """
    Join two tables using a interest column with the same name in both
    dataframes and return a new table with the result
    """
    
    joinDfs = [joinDfs] if type(joinDfs) != list else joinDfs
    join_field = 'id_entity'
    
    for jdf in joinDfs:
        jdf.rename(columns={int_col : join_field}, inplace=True)
    
        mainDf = mainDf.merge(
            jdf, how='outer',
            left_on=int_col, right_on=join_field
        )
        
        mainDf.fillna(0, inplace=True)
        
        mainDf[int_col].replace(0, mainDf[join_field], inplace=True)
        
        mainDf.drop(join_field, axis=1, inplace=True)
    
    return mainDf


def join_attr_by_distance(mainTable, joinTable, workGrass, epsg_code,
                          output):
    """
    Find nearest feature and join attributes of the nearest feature
    to the mainTable
    
    Uses GRASS GIS to find near lines.
    """
    
    import os
    from gasp.cpu.grs import run_grass
    from gasp.fm.shp  import shp_to_df
    from gasp.cpu.pnd import regulardf_to_geodf
    from gasp.to.shp  import df_to_shp
    from gasp.oss     import get_filename
    
    # Create GRASS GIS Location
    grassBase = run_grass(workGrass, location='join_loc', srs=epsg_code)
    
    import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grassBase, workGrass, 'join_loc', 'PERMANENT')
    
    # Import some GRASS GIS tools
    from gasp.cpu.grs.anls.prox import near
    from gasp.cpu.grs.mng.feat  import geomattr_to_db
    from gasp.to.shp.grs        import shp_to_grs, grs_to_shp
    
    # Import data into GRASS GIS
    grsMain = shp_to_grs(mainTable, get_filename(
        mainTable, forceLower=True)
    ); grsJoin = shp_to_grs(joinTable, get_filename(
        joinTable, forceLower=True)
    )
    
    # Get distance from each feature of mainTable to the nearest feature
    # of the join table
    near(grsMain, grsJoin, nearCatCol="tocat", nearDistCol="todistance")
    
    # Export data from GRASS GIS
    ogrMain = grs_to_shp(grsMain, os.path.join(
        workGrass, 'join_loc', grsMain + '_grs.shp'), None, asMultiPart=True
    ); ogrJoin = grs_to_shp(grsJoin, os.path.join(
        workGrass, 'join_loc', grsJoin + '_grs.shp'), None, asMultiPart=True)
    
    dfMain = shp_to_df(ogrMain)
    dfJoin = shp_to_df(ogrJoin)
    
    dfResult = dfMain.merge(dfJoin, how='inner',
                            left_on='tocat', right_on='cat')
    
    dfResult.drop(["geometry_y", "cat_y"], axis=1, inplace=True)
    dfResult.rename(columns={"cat_x" : "cat_grass"}, inplace=True)
    
    dfResult["tocat"]     = dfResult["tocat"] - 1
    dfResult["cat_grass"] = dfResult["cat_grass"] - 1
    
    dfResult = regulardf_to_geodf(dfResult, "geometry_x", epsg_code)
    
    df_to_shp(dfResult, output)
    
    return output
