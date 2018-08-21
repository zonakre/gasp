"""
Overlay operations with GeoPandas
"""


def gp_intersection(inShp, intersectShp, outShp):
    """
    Intersection between ESRI Shapefile
    """
    
    import geopandas
    
    from gasp.fm.shp import shp_to_df
    from gasp.to.shp import df_to_shp
    
    dfShp       = shp_to_df(inShp)
    dfIntersect = shp_to_df(intersectShp)
    
    res_interse = geopandas.overlay(dfShp, dfIntersect, how='intersection')
    
    df_to_shp(res_interse, outShp)

 
def snap_points_to_near_line(lineShp, pointShp, epsg, workGrass,
                             outPoints, location='overlap_pnts'):
    """
    Move points to overlap near line
    
    Uses GRASS GIS to find near lines.
    """
    
    import os;        import numpy
    from geopandas    import GeoDataFrame
    from gasp.oss     import get_filename
    from gasp.cpu.grs import run_grass
    from gasp.fm.shp  import shp_to_df
    from gasp.to.shp  import df_to_shp
    
    # Create GRASS GIS Location
    grassBase = run_grass(workGrass, location=location, srs=epsg)
    
    import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grassBase, workGrass, location, 'PERMANENT')
    
    # Import some GRASS GIS tools
    from gasp.cpu.grs.anls.prox import near
    from gasp.cpu.grs.mng.feat  import geomattr_to_db
    from gasp.to.shp.grs        import shp_to_grs, grs_to_shp
    
    # Import data into GRASS GIS
    grsLines = shp_to_grs(
        lineShp, get_filename(lineShp, forceLower=True)
    )
    
    grsPoint = shp_to_grs(
        pointShp, get_filename(pointShp, forceLower=True)
    )
    
    # Get distance from points to near line
    near(grsPoint, grsLines, nearCatCol="tocat", nearDistCol="todistance")
    
    # Get coord of start/end points of polylines
    geomattr_to_db(grsLines, ['sta_pnt_x', 'sta_pnt_y'], 'start', 'line')
    geomattr_to_db(grsLines, ['end_pnt_x', 'end_pnt_y'],   'end', 'line')
    
    # Export data from GRASS GIS
    ogrPoint = grs_to_shp(grsPoint, os.path.join(
        workGrass, grsPoint + '.shp', 'point', asMultiPart=True
    ))

    ogrLine = grs_to_shp(grsLines, os.path.join(
        workGrass, grsLines + '.shp', 'point', asMultiPart=True
    ))
    
    # Points to GeoDataFrame
    pntDf = shp_to_df(ogrPoint)
    # Lines to GeoDataFrame
    lnhDf = shp_to_df(ogrLine)
    
    # Erase unecessary fields
    pntDf.drop(["todistance"], axis=1, inplace=True)
    lnhDf.drop([c for c in lnhDf.columns.values if c != 'geometry' and
                c != 'cat' and c != 'sta_pnt_x' and c != 'sta_pnt_y' and 
                c != 'end_pnt_x' and c != 'end_pnt_y'],
                axis=1, inplace=True)
    
    # Join Geometries - Table with Point Geometry and Geometry of the 
    # nearest line
    resultDf = pntDf.merge(
        lnhDf, how='inner', left_on='tocat', right_on='cat')
    
    # Move points
    resultDf['geometry'] = [geoms[0].interpolate(
        geoms[0].project(geoms[1])
    ) for geoms in zip(resultDf.geometry_y, resultDf.geometry_x)]
    
    resultDf.drop(["geometry_x", "geometry_y", "cat_x", "cat_y"],
                  axis=1, inplace=True)
    
    resultDf = GeoDataFrame(
        resultDf, crs={"init" : 'epsg:{}'.format(epsg)}, geometry="geometry"
    )
    
    # Check if points are equal to any start/end points
    resultDf["x"] = resultDf.geometry.x
    resultDf["y"] = resultDf.geometry.y
    
    resultDf["check"] = numpy.where(
        (resultDf["x"] == resultDf["sta_pnt_x"]) & (resultDf["y"] == resultDf["sta_pnt_y"]),
        1, 0
    )
    
    resultDf["check"] = numpy.where(
        (resultDf["x"] == resultDf["end_pnt_x"]) & (resultDf["y"] == resultDf["end_pnt_y"]),
        1, 0
    )
    
    # To file
    df_to_shp(resultDf, outPoints)
    
    return outPoints


def break_lines_on_points(lineShp, pointShp, lineIdInPntShp,
                         splitedShp, srsEpsgCode):
    """
    Break lines on points location
    
    The points should be contained by the lines;
    The points table should have a column with the id of the
    line that contains the point.
    """
    
    from shapely.ops      import split
    from shapely.geometry import Point, LineString
    from gasp.fm.shp      import shp_to_array
    from gasp.fm.shp      import shp_to_dict
    from gasp.cpu.pnd.mng import col_list_val_to_row
    from gasp.to.obj      import dict_to_df
    from gasp.to.shp      import df_to_shp
    
    # Sanitize line geometry
    def fix_line(line, point):
        buff = point.buffer(0.0001)
        
        splitLine = split(line, buff)
        
        nline = LineString(
            list(splitLine[0].coords) + list(point.coords) +
            list(splitLine[-1].coords)
        )
        
        return nline
    
    pnts  = shp_to_array(pointShp, fields='ALL')
    lines = shp_to_dict(lineShp, fields='ALL')
    
    for point in pnts:
        rel_line = lines[point[lineIdInPntShp]]
        
        if type(rel_line["GEOM"]) != list:
            line_geom = fix_line(rel_line["GEOM"], point["GEOM"])
            
            split_lines = split(line_geom, point["GEOM"])
            
            lines[point[lineIdInPntShp]]["GEOM"] = [l for l in split_lines]
        
        else:
            for i in range(len(rel_line["GEOM"])):
                if rel_line["GEOM"][i].distance(point["GEOM"]) < 1e-8:
                    line_geom = fix_line(rel_line["GEOM"][i], point["GEOM"])
                    split_lines = split(line_geom, point["GEOM"])
                    split_lines = [l for l in split_lines]
                    
                    lines[point[lineIdInPntShp]]["GEOM"][i] = split_lines[0]
                    lines[point[lineIdInPntShp]]["GEOM"] += split_lines[1:]
                    
                    break
                
                else:
                    continue
    
    # Result to Dataframe
    linesDf = dict_to_df(lines)
    
    # Where GEOM is a List, create a new row for each element in list
    linesDf = col_list_val_to_row(
        linesDf, "GEOM", geomCol="GEOM", epsg=srsEpsgCode
    )
    
    # Save result
    return df_to_shp(linesDf, splitedShp)

