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


"""
Custom Joins with GRASS GIS
"""

def join_table(inShp, jnTable, shpCol, joinCol):
    """
    Join Tables GRASS GIS
    """
    
    from gasp import exec_cmd
    
    rcmd = exec_cmd(
        "v.db.join map={} column={} other_table={} other_column={}".format(
            inShp, shpCol, jnTable, joinCol
            )
        )


def join_attr_by_distance(mainTable, joinTable, workGrass, epsg_code,
                          output):
    """
    Find nearest feature and join attributes of the nearest feature
    to the mainTable
    
    Uses GRASS GIS to find near lines.
    """
    
    import os
    from gasp.session import run_grass
    from gasp.fm      import tbl_to_obj
    from gasp.to.geom import regulardf_to_geodf
    from gasp.to.shp  import df_to_shp
    from gasp.oss     import get_filename
    
    # Create GRASS GIS Location
    grassBase = run_grass(workGrass, location='join_loc', srs=epsg_code)
    
    import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grassBase, workGrass, 'join_loc', 'PERMANENT')
    
    # Import some GRASS GIS tools
    from gasp.anls.prox        import grs_near as near
    from gasp.cpu.grs.mng.feat import geomattr_to_db
    from gasp.to.shp.grs       import shp_to_grs, grs_to_shp
    
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
    
    dfMain = tbl_to_obj(ogrMain)
    dfJoin = tbl_to_obj(ogrJoin)
    
    dfResult = dfMain.merge(dfJoin, how='inner',
                            left_on='tocat', right_on='cat')
    
    dfResult.drop(["geometry_y", "cat_y"], axis=1, inplace=True)
    dfResult.rename(columns={"cat_x" : "cat_grass"}, inplace=True)
    
    dfResult["tocat"]     = dfResult["tocat"] - 1
    dfResult["cat_grass"] = dfResult["cat_grass"] - 1
    
    dfResult = regulardf_to_geodf(dfResult, "geometry_x", epsg_code)
    
    df_to_shp(dfResult, output)
    
    return output


def joinLines_by_spatial_rel_raster(mainLines, mainId, joinLines,
                                    joinCol, outfile, epsg):
    """
    Join Attributes based on a spatial overlap.
    An raster based approach
    """
    
    import os;          import pandas
    from geopandas      import GeoDataFrame
    from gasp.to.geom   import regulardf_to_geodf
    from gasp.session   import run_grass
    from gasp.oss       import get_filename
    from gasp.oss.ops   import create_folder
    from gasp.mng.ext   import shpextent_to_boundary
    from gasp.mng.joins import join_dfs
    from gasp.mng.df    import df_groupBy
    from gasp.to.rst    import shp_to_raster
    from gasp.fm        import tbl_to_obj
    from gasp.to.shp    import df_to_shp
    
    workspace = create_folder(os.path.join(
        os.path.dirname(mainLines, 'tmp_dt')
    ))
    
    # Create boundary file
    boundary = shpextent_to_boundary(
        mainLines, os.path.join(workspace, "bound.shp"),
        epsg
    )
    
    boundRst = shp_to_raster(boundary, None, 5, -99, os.path.join(
        workspace, "rst_base.tif"), epsg=epsg, api='gdal')
    
    # Start GRASS GIS Session
    gbase = run_grass(workspace, location="grs_loc", srs=boundRst)
    
    import grass.script       as grass
    import grass.script.setup as gsetup
    
    gsetup.init(gbase, workspace, "grs_loc", "PERMANENT")
    
    from gasp.spanlst.local   import combine
    from gasp.cpu.grs.spanlst import get_rst_report_data
    from gasp.to.shp.grs      import shp_to_grs, grs_to_shp
    from gasp.to.rst          import shp_to_raster
    
    # Add data to GRASS GIS
    mainVector = shp_to_grs(
        mainLines, get_filename(mainLines, forceLower=True))
    joinVector = shp_to_grs(
        joinLines, get_filename(joinLines, forceLower=True))
    
    mainRst = shp_to_raster(
        mainVector, mainId, None, None, "rst_" + mainVector, api='pygrass'
    ); joinRst = shp_to_raster(
        joinVector, joinCol, None, None, "rst_" + joinVector, api='pygrass'
    )
    
    combRst = combine(mainRst, joinRst, "combine_rst", api="pygrass")
    
    combine_data = get_rst_report_data(combRst, UNITS="c")
    
    combDf = pandas.DataFrame(combine_data, columns=[
        "comb_cat", "rst_1", "rst_2", "ncells"
    ])
    combDf = combDf[combDf["rst_2"] != '0']
    combDf["ncells"] = combDf["ncells"].astype(int)
    
    gbdata = df_groupBy(combDf, ["rst_1"], "MAX", "ncells")
    
    fTable = join_dfs(gbdata, combDf, ["rst_1", "ncells"], ["rst_1", "ncells"])
    
    fTable["rst_2"] = fTable["rst_2"].astype(int)
    fTable = df_groupBy(
        fTable, ["rst_1", "ncells"],
        STAT='MIN', STAT_FIELD="rst_2"
    )
    
    mainLinesCat = grs_to_shp(
        mainVector, os.path.join(workspace, mainVector + '.shp'), 'line')
    
    mainLinesDf = tbl_to_obj(mainLinesCat)
    
    resultDf = join_dfs(
        mainLinesDf, fTable, "cat", "rst_1",
        onlyCombinations=None
    )
    
    resultDf.rename(columns={"rst_2" : joinCol}, inplace=True)
    
    resultDf = regulardf_to_geodf(resultDf, "geometry", epsg)
    
    df_to_shp(resultDf, outfile)
    
    return outfile


"""
Do Joins and stuff with excel tables
"""

def join_xls_table(main_table, fid_main, join_table, fid_join, copy_fields, out_table,
                   main_sheet=None, join_sheet=None):
    """
    Join tables using a commum attribute
    
    Relations:
    - 1 to 1
    - N to 1
    
    TODO: Use Pandas Instead
    """
    
    import xlwt
    from gasp.fm          import tbl_to_obj
    from gasp.mng.fld.xls import columns_by_order
    
    copy_fields = [copy_fields] if type(copy_fields) == str or type(copy_fields) == unicode \
        else copy_fields if type(copy_fields) == list else None
    
    if not copy_fields:
        raise ValueError(
            'copy_fields should be a list or a string'
        )
    
    # main_table to dict
    mainData = tbl_to_obj(
        main_table, sheet=main_sheet, useFirstColAsIndex=True, output='dict'
    )
    
    # join table to dict
    joinData = tbl_to_obj(
        join_table, sheet=join_sheet, useFirstColAsIndex=True, output='dict'
    )
    
    # write output data
    out_sheet_name = 'data' if not main_sheet and not join_sheet else join_sheet \
        if join_sheet and not main_sheet else main_sheet
    
    out_xls = xlwt.Workbook()
    new_sheet = out_xls.add_sheet(out_sheet_name)
    
    # Write tiles
    COLUMNS_ORDER = columns_by_order(main_table, sheet_name=main_sheet)
    
    TITLES = COLUMNS_ORDER + copy_fields
    for i in range(len(TITLES)):
        new_sheet.write(0, i, TITLES[i])
    
    # parse data
    l = 1
    for fid in mainData:
        new_sheet.write(l, 0, fid)
        
        c = 1
        for col in COLUMNS_ORDER[1:]:
            new_sheet.write(l, c, mainData[fid][col])
            c+=1
        
        for col in copy_fields:
            if fid in joinData:
                new_sheet.write(l, c, joinData[fid][col])
            c+=1
        
        l += 1
    
    out_xls.save(out_table)


def join_tables_in_table(mainTable, mainIdField, joinTables, outTable):
    """
    Join one table with all tables in a folder
    
    joinTables = {
        r'D:\TRENMO_JASP\CARRIS\valid_by_para\period_16_17h59\sabado\fvalidacoes_v6_2018-01-06.xlsx' : {
            "JOIN_FIELD"    : 'paragem',
            "COLS_TO_JOIN"  : {'n_validacao' : 'dia_6'}
        },
        r'D:\TRENMO_JASP\CARRIS\valid_by_para\period_16_17h59\sabado\fvalidacoes_v6_2018-01-13.xlsx' : {
            "JOIN_FIELD"    : 'paragem',
            "COLS_TO_JOIN"  : {'n_validacao' : 'dia_13'}
        },
        r'D:\TRENMO_JASP\CARRIS\valid_by_para\period_16_17h59\sabado\fvalidacoes_v6_2018-01-20.xlsx' : {
            "JOIN_FIELD"    : 'paragem',
            "COLS_TO_JOIN"  : {'n_validacao' : 'dia_20'}
        },
        r'D:\TRENMO_JASP\CARRIS\valid_by_para\period_16_17h59\sabado\fvalidacoes_v6_2018-01-27.xlsx' : {
            "JOIN_FIELD"    : 'paragem',
            "COLS_TO_JOIN"  : {'n_validacao' : 'dia_27'}
        }
    }
    
    #TODO: only works with xlsx tables as join TABLES
    """
    
    # Modules
    import os;   import pandas
    from gasp.fm import tbl_to_obj
    from gasp.to import obj_to_tbl
    
    # Get table format
    tableType = os.path.splitext(mainTable)[1]
    
    tableDf = tbl_to_obj(mainTable)
    
    for table in joinTables:
        xlsDf = tbl_to_obj(table)
        
        join_field = 'id_entity' if joinTables[table]["JOIN_FIELD"] == mainIdField \
            else joinTables[table]["JOIN_FIELD"]
        
        if joinTables[table]["JOIN_FIELD"] == mainIdField:
            xlsDf.rename(columns={mainIdField : join_field}, inplace=True)
        
        xlsDf.rename(columns=joinTables[table]["COLS_TO_JOIN"], inplace=True)
        
        tableDf = tableDf.merge(
            xlsDf, how='outer', left_on=mainIdField,
            right_on=join_field
        )
        
        tableDf.fillna(0, inplace=True)
        tableDf[mainIdField].replace(0, tableDf[join_field], inplace=True)
        
        tableDf.drop(join_field, axis=1, inplace=True)
    
    obj_to_tbl(tableDf, outTable)
    
    return outTable


def field_sum_two_tables(tableOne, tableTwo,
                         joinFieldOne, joinFieldTwo,
                         field_to_sum, outTable):
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
    
    from gasp.fm        import tbl_to_obj
    from gasp.to        import obj_to_tbl
    from gasp.mng.joins import sum_field_of_two_tables
    
    # Open two tables
    df_one = tbl_to_obj(tableOne)
    df_two = tbl_to_obj(tableTwo)
    
    # Do it!
    outDf = sum_field_of_two_tables(
        df_one, joinFieldOne,
        df_two, joinFieldTwo,
        field_to_sum
    )
    
    obj_to_tbl(outDf, outTable)
    
    return outTable


def field_sum_by_table_folder(folderOne, joinFieldOne,
                              folderTwo, joinFieldTwo,
                              sum_field, outFolder):
    
    import os
    from gasp.oss import list_files
    from gasp.oss import get_filename
    
    tablesOne = list_files(folderOne, file_format=['.xls', '.xlsx'])
    tablesTwo = list_files(folderTwo, file_format=['.xls', '.xlsx'])
    
    for table in tablesOne:
        table_name = get_filename(table)
        
        for __table in tablesTwo:
            __table_name = get_filename(__table)
            
            if table_name == __table_name:
                field_sum_two_tables(
                    table, __table, joinFieldOne, joinFieldTwo, sum_field,
                    os.path.join(outFolder, os.path.basename(table))
                )
                
                break

