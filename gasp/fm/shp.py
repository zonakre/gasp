"""
ESRI Shapefile to Something
"""

def shp_to_df(shp):
    """
    ESRI Shapefile to Pandas Dataframe
    """
    
    import geopandas
    
    return geopandas.read_file(shp)


def shp_to_dict(shp, fields="ALL", geomCol=None):
    """
    Convert one Shape to Dict
    """
    
    from gasp.cpu.pnd.mng.fld import del_fld_notin_geodf
    
    geodf = shp_to_df(shp)
    
    if not geomCol:
        for c in geodf.columns.values:
            if c == 'geometry' or c == 'geom':
                geomCol = c
                break 
    
    if fields != "ALL":
        geodf = del_fld_notin_geodf(geodf, fields, geomCol=geomCol)
    
    geodf.rename(columns={geomCol : "GEOM"}, inplace=True)
    
    return geodf.to_dict(orient="index")


def shp_to_array(shp, fields='ALL', geomCol=None):
    """
    Feature Class to ARRAY:
    
    ARRAY = [
        {"FID" : X, GEOM : geom, OTHER_FIELD1 : X, ..., OTHER_FIELDN : X},
        ...,
        {"FID" : X, GEOM : geom, OTHER_FIELD1 : X, ..., OTHER_FIELDN : X}
    ]
    
    Values of "GEOM" keys will be Shapely Geometry Object
    """
    
    from gasp.cpu.pnd.mng.fld import del_fld_notin_geodf
    
    shpDf = shp_to_df(shp)
    shpDf["FID"] = shpDf.index
    
    if not geomCol:
        for c in shpDf.columns.values:
            if c == 'geometry' or c == 'geom':
                geomCol = c
                break 
    
    if fields != 'ALL':
        shpDf = del_fld_notin_geodf(shpDf, fields, geomCol=geomCol)
    
    shpDf.rename(columns={geomCol : "GEOM"}, inplace=True)
    
    return shpDf.to_dict(orient='records')


def points_to_list(pntShp, listVal='tuple', inEpsg=None, outEpsg=None):
    """
    Return a list as:
    
    if listVal == 'tuple'
    l = [(x_coord, y_coord), ..., (x_coord, y_coord)]
    
    elif listVal == 'dict'
    l = [
        {id : fid_value, x : x_coord, y : y_coord},
        ...
        {id : fid_value, x : x_coord, y : y_coord}
    ]
    """
    
    geoDf = shp_to_df(pntShp)
    
    if inEpsg and outEpsg:
        if inEpsg != outEpsg:
            from gasp.cpu.pnd.mng.prj import project_df
            geoDf = project_df(geoDf, outEpsg)
    
    geoDf["x"] = geoDf.geometry.x.astype(float)
    geoDf["y"] = geoDf.geometry.y.astype(float)
    
    if listVal == 'tuple':
        subset = geoDf[['x', 'y']]
    
        coords = [tuple(x) for x in subset.values]
    
    elif listVal == 'dict':
        geoDf["id"] = geoDf.index
        subset = geoDf[['id', 'x', 'y']]
        
        coords = subset.to_dict(orient='records')
    
    else:
        raise ValueError(
            'Value of listVal is not Valid. Please use "tuple" or "dict"'
        )
    
    return coords


def shape_to_tree(shape, fields):
    """
    fields = {
        1 : {FIELD_1 : FIELD_2},
        2 : {FIELD_2 : FIELD_3}
    }
    
    result = {
        field_1:1 : {
            field_2:1 : field_3,
            field_2:2 : field_3
            ... 
        },
        field_1:2 {
            field_2:1 : field_3,
            field_2:2 : field_3
        },
        ...
    }
    
    fields = {FIELD_1 : {FIELD_2 : FIELD_3}}
    
    TODO: Adapt this to work with Pandas
    """
    
    import arcpy
    
    def getNode(feature, node, dicFields):
        for field in dicFields:
            root = feature.getValue(field)
            
            if type(dicFields[field]) == dict:
                if root not in node:
                    node[root] = {}
                
                getNode(feature, node[root], dicFields[field])
                    
            else:
                node[root] = feature.getValue(dicFields[field])
    
    from gasp.cpu.arcg.lyr import feat_lyr
    
    lyr = feat_lyr(shape)
    
    cursor = arcpy.SearchCursor(lyr)
    dataTree = {}
    for feat in cursor:
        getNode(feat, dataTree, fields)
    
    return dataTree

