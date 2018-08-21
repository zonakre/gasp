"""
Custom Joins with GRASS GIS
"""


def join_table(inShp, jnTable, shpCol, joinCol):
    """
    Join Tables GRASS GIS
    """
    
    from gasp import exec_cmd
    
    rcmd = exec_cmd("v.db.join map={} column={} other_table={} other_column={}".format(
        inShp, shpCol, jnTable, joinCol
    ))


def joinLines_by_spatial_rel_raster(mainLines, mainId, joinLines,
                                    joinCol, outfile, epsg):
    """
    Join Attributes based on a spatial overlap.
    An raster based approach
    """
    
    import os; import pandas
    from geopandas            import GeoDataFrame
    from gasp.cpu.pnd         import regulardf_to_geodf
    from gasp.cpu.grs         import run_grass
    from gasp.oss             import get_filename
    from gasp.oss.ops         import create_folder
    from gasp.cpu.gdl.mng.ext import shpextent_to_boundary
    from gasp.cpu.pnd.joins   import join_dfs
    from gasp.cpu.pnd.mng     import df_groupBy
    from gasp.to.rst.gdl      import shp_to_raster
    from gasp.fm.shp          import shp_to_df
    from gasp.to.shp          import df_to_shp
    
    workspace = create_folder(os.path.join(
        os.path.dirname(mainLines, 'tmp_dt')
    ))
    
    # Create boundary file
    boundary = shpextent_to_boundary(
        mainLines, os.path.join(workspace, "bound.shp"),
        epsg
    )
    
    boundRst = shp_to_raster(boundary, 5, -99, os.path.join(
        workspace, "rst_base.tif"), epsg=epsg)
    
    # Start GRASS GIS Session
    gbase = run_grass(workspace, location="grs_loc", srs=boundRst)
    
    import grass.script       as grass
    import grass.script.setup as gsetup
    
    gsetup.init(gbase, workspace, "grs_loc", "PERMANENT")
    
    from gasp.cpu.grs.spanlst import combine
    from gasp.cpu.grs.spanlst import get_rst_report_data
    from gasp.to.shp.grs      import shp_to_grs, grs_to_shp
    from gasp.to.rst.grs      import shp_to_raster
    
    # Add data to GRASS GIS
    mainVector = shp_to_grs(
        mainLines, get_filename(mainLines, forceLower=True))
    joinVector = shp_to_grs(
        joinLines, get_filename(joinLines, forceLower=True))
    
    mainRst = shp_to_raster(mainVector, "rst_" + mainVector, mainId)
    joinRst = shp_to_raster(joinVector, "rst_" + joinVector, joinCol)
    
    combRst = combine(mainRst, joinRst, "combine_rst")
    
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
    
    mainLinesDf = shp_to_df(mainLinesCat)
    
    resultDf = join_dfs(
        mainLinesDf, fTable, "cat", "rst_1",
        onlyCombinations=None
    )
    
    resultDf.rename(columns={"rst_2" : joinCol}, inplace=True)
    
    resultDf = regulardf_to_geodf(resultDf, "geometry", epsg)
    
    df_to_shp(resultDf, outfile)
    
    return outfile

