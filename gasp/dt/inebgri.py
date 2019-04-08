"""
Do things with BGRI from INE
"""

"""
Using ArcGIS
"""
def assign_units_to_polygons(bgri, polygons, id_bgri, id_polygon,
                             field_bgri='pol_assigned', workspace=None):
    """
    Permite verificar a que municipio ou area de influencia uma subsecao
    estatistica pertence (territorialmente).
    
    Se uma subseccao se intersectar com mais de um poligono, a primeira fica
    relacionada ao poligono que ocupa maior parte da sua area (isto pode 
    levantar algumas questoes, mas para ja fica assim).
    
    A relacao entre a subsecao e o poligono que com ela intersecta ficara 
    escrita num novo campo da bgri
    
    Use Arcgis to accomplish this
    """
    
    import arcpy;                 import os
    from gasp.cpu.arcg.lyr        import feat_lyr
    from gasp.cpu.arcg            import get_geom_field, get_feat_area
    from gasp.cpu.arcg.anls.ovlay import intersect
    from gasp.cpu.arcg.mng.fld    import add_field
    
    arcpy.env.overwriteOutput = True
    workspace = workspace if workspace else os.path.dirname(bgri)
    
    # Create feature layers of the inputs
    bgriLyr, polygLyr = [feat_lyr(bgri), feature_lyr(polygons)]
    
    # Intersect
    int_fc = os.path.join(workspace, 'bgri_and_polygons.shp')
    int_fc = intersect([bgriLyr, polygLyr], int_fc)
    
    # Relate bgri unit with polygon entities
    intLyr = feat_lyr(int_fc)
    
    cursor = arcpy.SearchCursor(intLyr)
    bgri_polygons = {}
    geomField = get_geom_field(intLyr)
    for linha in cursor:
        fid_bgri = linha.getValue(id_bgri)
        fid_polygon = linha.getValue(id_polygon)
        
        area = get_feat_area(linha, geomField)
        
        if fid_bgri not in bgri_polygons.keys():
            bgri_polygons[fid_bgri] = [fid_polygon, area]
        
        else:
            if area > bgri_polygons[fid_bgri][1]:
                bgri_polygons[fid_bgri] = [fid_polygon, area]
            
            else:
                continue
    
    # Write output
    del cursor, linha
    
    add_field(bgriLyr, field_bgri, "TEXT", "15")
    
    cursor = arcpy.UpdateCursor(bgriLyr)
    for linha in cursor:
        fid_bgri = linha.getValue(id_bgri)
        linha.setValue(field_bgri, bgri_polygons[fid_bgri][0])
        cursor.updateRow(linha)
    
    del cursor, linha, bgriLyr, polygLyr


"""
Using GeoPandas
"""
def join_bgrishp_with_bgridata(bgriShp, bgriCsv, outShp,
                               shpJoinField="BGRI11",
                               dataJoinField="GEO_COD",
                               joinFieldsMantain=None,
                               newNames=None):
    """
    Join BGRI ESRI Shapefile with the CSV with the BGRI Data
    """
    
    from gasp        import goToList
    from gasp.fm     import tbl_to_obj
    from gasp.to.shp import df_to_shp
    
    # Read main_table
    mainDf = tbl_to_obj(bgriShp)
    
    # Read join table
    joinDf = tbl_to_obj(bgriCsv, _delimiter=';', encoding_='utf-8')
    
    # Sanitize GEO_COD of bgriCsv
    joinDf[dataJoinField] = joinDf[dataJoinField].str.replace("'", "")
    
    if joinFieldsMantain:
        joinFieldsMantain = goToList(joinFieldsMantain)
        
        dropCols = []
        for col in joinDf.columns.values:
            if col not in [dataJoinField] + joinFieldsMantain:
                dropCols.append(col)
        
        joinDf.drop(dropCols, axis=1, inplace=True)
    
    resultDf = mainDf.merge(
        joinDf, how='inner', left_on=shpJoinField, right_on=dataJoinField
    )
    if newNames:
        newNames = goToList(newNames)
        renDict = {
            joinFieldsMantain[n] : newNames[n] for n in range(len(joinFieldsMantain))
        }
        
        resultDf.rename(columns=renDict, inplace=True)
    
    df_to_shp(resultDf, outShp)
    
    return outShp

