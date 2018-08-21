"""
Methods to produce Indicators relating Population and their
accessibility to things
"""

"""
ArcPy Based Solutions
"""

def arcg_mean_time_WByPop(netDt, rdv, infraestruturas, unidades, conjuntos,
                          popf, w, output, oneway=None):
    """
    Tempo medio ponderado pela populacao residente a infra-estrutura mais
    proxima (min)
    
    * netDt = Path to Network Dataset
    * infraestruturas = Points of destiny
    * unidades = BGRI; Freg; Concelhos
    * conjuntos = Freg; Concelhos; NUT - field
    * popf = Field with the population of the statistic unity
    * w = Workspace
    * output = Path to store the final output
    * rdv = Name of feature class with the streets network
    """
    
    import arcpy
    import os
    from gasp.cpu.arcg.lyr              import feat_lyr
    from gasp.cpu.arcg.mng.feat         import feat_to_pnt
    from gasp.cpu.arcg.mng.fld          import add_field
    from gasp.cpu.arcg.mng.fld          import calc_fld
    from gasp.cpu.arcg.mng.joins        import join_table
    from gasp.mng.genze                 import dissolve
    from gasp.cpu.arcg.mng.gen          import copy_features
    from gasp.cpu.arcg.netanlst.closest import closest_facility
    
    def get_freg_denominator(shp, groups, population, fld_time="Total_Minu"):
        cursor = arcpy.SearchCursor(shp)
        
        groups_sum = {}
        for lnh in cursor:
            group = lnh.getValue(groups)
            nrInd = float(lnh.getValue(population))
            time  = float(lnh.getValue(fld_time))
            
            if group not in groups_sum.keys():
                groups_sum[group] = time * nrInd
            
            else:
                groups_sum[group] += time * nrInd
        
        del cursor, lnh
        
        return groups_sum
    
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = w
    
    # Start Procedure #
    # Create copy of statitic unities to preserve the original data
    copy_unities = copy_features(
        unidades,
        os.path.join(w, os.path.basename(unidades))
    )
    
    # Generate centroids of the statistic unities - unidades
    lyr_unidades = feat_lyr(copy_unities)
    pnt_unidades = feat_to_pnt(lyr_unidades, 'pnt_unidades.shp')
    
    # Network Processing - Distance between CENTROID and Destiny points
    closest_facility(
        netDt, rdv, infraestruturas, pnt_unidades,
        os.path.join(w, "cls_table.dbf"), oneway_restriction=oneway
    )
    add_field("cls_table.dbf", 'j', "SHORT", "6")
    calc_fld("cls_table.dbf", 'j', "[IncidentID]-1")
    join_table(lyr_unidades, "FID", "cls_table.dbf", "j", "Total_Minu")
    
    # Calculo dos somatorios por freguesia (conjunto)
    groups = get_freg_denominator(lyr_unidades, conjuntos, popf)
    add_field(lyr_unidades, "tm", "FLOAT", "10", "3")
    
    cs = arcpy.UpdateCursor(lyr_unidades)
    linha = cs.next()
    while linha:
        group = linha.getValue(conjuntos)
        t = float(linha.getValue("Total_Minu"))
        p = int(linha.getValue(popf))
        total = groups[group]
        indi = ((t * p) / total) * t
        linha.setValue("tm", indi)
        cs.updateRow(linha)
        linha = cs.next()
    
    return dissolve(
        lyr_unidades, output, conjuntos, statistics="tm SUM", api="arcpy"
    )


def arcg_mean_time_WByPop2(netDt, rdv, infraestruturas, unidades, conjuntos,
                          popf, w, output, oneway=None):
    """
    Tempo medio ponderado pela populacao residente a infra-estrutura mais
    proxima (min)
    
    * netDt = Path to Network Dataset
    * infraestruturas = Points of destiny
    * unidades = BGRI; Freg; Concelhos
    * conjuntos = Freg; Concelhos; NUT - field
    * popf = Field with the population of the statistic unity
    * w = Workspace
    * output = Path to store the final output
    * rdv = Name of feature class with the streets network
    """
    
    import arcpy
    import os
    from gasp.cpu.arcg.lyr              import feat_lyr
    from gasp.cpu.arcg.mng.feat         import feat_to_pnt
    from gasp.cpu.arcg.mng.fld          import add_field, calc_fld
    from gasp.cpu.arcg.mng.joins        import join_table
    from gasp.mng.genze                 import dissolve
    from gasp.cpu.arcg.mng.gen          import copy_features
    from gasp.cpu.arcg.netanlst.closest import closest_facility
    from gasp.fm.shp                    import shp_to_df
    
    def get_freg_denominator(shp, groups, population, fld_time="Total_Minu"):
        cursor = arcpy.SearchCursor(shp)
        
        groups_sum = {}
        for lnh in cursor:
            group = lnh.getValue(groups)
            nrInd = float(lnh.getValue(population))
            time  = float(lnh.getValue(fld_time))
            
            if group not in groups_sum.keys():
                groups_sum[group] = time * nrInd
            
            else:
                groups_sum[group] += time * nrInd
        
        del cursor, lnh
        
        return groups_sum
    
    if not os.path.exists(w):
        from gasp.oss.ops import create_folder
        w = create_folder(w, overwrite=False)
    
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = w
    
    # Start Procedure #
    # Create copy of statitic unities to preserve the original data
    copy_unities = copy_features(
        unidades,
        os.path.join(w, os.path.basename(unidades))
    )
    
    # Generate centroids of the statistic unities - unidades
    lyr_unidades = feat_lyr(copy_unities)
    pnt_unidades = feat_to_pnt(lyr_unidades, 'pnt_unidades.shp')
    
    # Network Processing - Distance between CENTROID and Destiny points
    closest_facility(
        netDt, rdv, infraestruturas, pnt_unidades,
        os.path.join(w, "cls_table.dbf"), oneway_restriction=oneway
    )
    add_field("cls_table.dbf", 'j', "SHORT", "6")
    calc_fld("cls_table.dbf", 'j', "[IncidentID]-1")
    join_table(lyr_unidades, "FID", "cls_table.dbf", "j", "Total_Minu")
    del lyr_unidades
    
    # Calculo dos somatorios por freguesia (conjunto)
    # To GeoDf
    unidadesDf = shp_to_df(copy_unities)
    
    """
    groups = get_freg_denominator(lyr_unidades, conjuntos, popf)
    add_field(lyr_unidades, "tm", "FLOAT", "10", "3")
    
    cs = arcpy.UpdateCursor(lyr_unidades)
    linha = cs.next()
    while linha:
        group = linha.getValue(conjuntos)
        t = float(linha.getValue("Total_Minu"))
        p = int(linha.getValue(popf))
        total = groups[group]
        indi = ((t * p) / total) * t
        linha.setValue("tm", indi)
        cs.updateRow(linha)
        linha = cs.next()
    
    return dissolve(lyr_unidades, output, conjuntos, "tm SUM")"""
    return unidadesDf


def mean_time_by_influence_area(netDt, rdv, infraestruturas,
                          fld_infraestruturas, unidades, id_unidade,
                          conjuntos, popf, influence_areas_unities, w, output,
                          oneway=True):
    """
    Tempo medio ponderado pela populacao residente a infra-estrutura mais
    proxima (min), por area de influencia
    
    * netDt - Path to Network Dataset
    * infraestruturas - Points of destiny
    * fld_infraestruturas - Field on destiny points to relate with influence area
    * unidades - BGRI; Freg; Concelhos
    * conjuntos - Freg; Concelhos; NUT - field
    * popf - Field with the population of the statistic unity
    * influence_areas_unities - Field on statistic unities layer to relate
    with influence area
    * w = Workspace
    * output = Path to store the final output
    * rdv - Name of feature class with the streets network
    * junctions - Name of feature class with the junctions
    """
    
    import arcpy; import os
    from gasp.cpu.arcg.lyr              import feat_lyr
    from gasp.cpu.arcg.mng.feat         import feat_to_pnt
    from gasp.cpu.arcg.mng.gen          import merge
    from gasp.cpu.arcg.mng.gen          import copy_features
    from gasp.mng.genze                 import dissolve
    from gasp.cpu.arcg.mng.fld          import add_field
    from gasp.cpu.arcg.mng.fld          import calc_fld
    from gasp.cpu.arcg.mng.fld          import field_statistics
    from gasp.cpu.arcg.mng.fld          import type_fields
    from gasp.cpu.arcg.mng.joins        import join_table
    from gasp.cpu.arcg.anls.exct        import select_by_attr
    from gasp.cpu.arcg.netanlst.closest import closest_facility
    
    """if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
    
    else:
        raise ValueError('Network analyst extension is not avaiable')"""
    
    def ListGroupArea(lyr, fld_ia, fld_grp):
        d = {}
        cs = arcpy.SearchCursor(lyr)
        for lnh in cs:
            id_group = lnh.getValue(fld_grp)
            id_ia = lnh.getValue(fld_ia)
            if id_group not in d.keys():
                d[id_group] = [id_ia]
            else:
                if id_ia not in d[id_group]:
                    d[id_group].append(id_ia)
        return d
    
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = w
    
    # Procedure #
    copy_unities = copy_features(
        unidades,
        os.path.join(w, os.path.basename(unidades))
    )
    
    # Generate centroids of the statistic unities - unidades
    lyr_unidades = feat_lyr(copy_unities)
    pnt_unidades = feat_to_pnt(lyr_unidades, 'pnt_unidades.shp',
                                    pnt_position="INSIDE")
    # List all groups of unities (conjuntos)
    group_areas = ListGroupArea(lyr_unidades, influence_areas_unities, conjuntos)
    # Create Layers
    lyr_pnt_unidades   = feat_lyr(pnt_unidades)
    lyr_pnt_facilities = feat_lyr(infraestruturas)
    
    result_list = []
    
    fld_type_unities = type_fields(lyr_pnt_unidades, field=conjuntos)
    SELECT_UNITIES = '{fld}=\'{c}\'' if str(fld_type_unities) == 'String' \
        else '{fld}={c}'
    
    fld_type_facilities = type_fields(
        lyr_pnt_facilities, field=fld_infraestruturas)
    SELECT_FACILITIES = '{fld}=\'{obj}\'' if str(fld_type_facilities) == 'String' \
        else '{fld}={obj}'
    for group in group_areas.keys():
        # Select centroids of interest
        interest_centroids = select_by_attr(
            lyr_pnt_unidades,
            SELECT_UNITIES.format(c=str(group), fld=conjuntos),
            'pnt_{c}.shp'.format(c=str(group))
        )
        # Select facilities of interest
        expression = ' OR '.join(
            [SELECT_FACILITIES.format(
                fld=fld_infraestruturas, obj=str(group_areas[group][i])
            ) for i in range(len(group_areas[group]))]
        )
        
        interest_facilities = select_by_attr(
            lyr_pnt_facilities,
            expression,
            'facilities_{c}.shp'.format(c=str(group))
        )
        # Run closest facilitie - Distance between selected CENTROID and selected facilities
        cls_fac_table = os.path.join(w, "clsf_{c}.dbf".format(c=str(group)))
        closest_facility(
            netDt, rdv, interest_facilities, interest_centroids,
            cls_fac_table, oneway_restriction=oneway
        )
        add_field(cls_fac_table, 'j', "SHORT", "6")
        calc_fld(cls_fac_table, 'j', "[IncidentID]-1")
        join_table(interest_centroids, "FID", cls_fac_table, "j", "Total_Minu")
        # Calculate sum of time x population
        add_field(interest_centroids, 'sum', "DOUBLE", "10", "3")
        calc_fld(
            interest_centroids, 'sum',
            "[{pop}]*[Total_Minu]".format(
                pop=popf
            )
        )
        denominador = field_statistics(interest_centroids, 'sum', 'SUM')
        add_field(interest_centroids, 'tm', "DOUBLE", "10", "3")
        calc_fld(
            interest_centroids, 'tm',
            "([sum]/{sumatorio})*[Total_Minu]".format(
                sumatorio=str(denominador)
            )
        )
        result_list.append(interest_centroids)
    
    merge_shp = merge(result_list, "merge_centroids.shp")
    join_table(lyr_unidades, id_unidade, "merge_centroids.shp", id_unidade, "tm")
    
    return dissolve(lyr_unidades, output, conjuntos, statistics="tm SUM", api='arcpy')


def pop_less_dist_x(
    net_dataset, rdv_name, junctions_name,
    locations, interval, unities, fld_groups, fld_pop,
    w, output):
    """
    Network processing - executar service area de modo a conhecer as areas a
    menos de x minutos de qualquer coisa
    """
    
    import arcpy;                      import os
    from gasp.cpu.arcg.lyr             import feat_lyr
    from gasp.mng.genze                import dissolve
    from gasp.cpu.arcg.anls.ovlay      import intersect
    from gasp.cpu.arcg.mng.fld         import add_field
    from gasp.cpu.arcg.netanlst.svarea import service_area_polygon
    
    def GetUnitiesIntersected(shpintersected, shpUnities):
        # AND IF SHPUNITIES HAS LESS THAN 6 CHARACTERS
        if len(os.path.basename(shpUnities)) > 6:
            fld_tag = os.path.basename(shpUnities)[:6]
        else:
            fld_tag = os.path.basename(shpUnities)
        c = arcpy.SearchCursor(shpintersected)
        l = c.next()
        u = []
        while l:
            fid_entity = int(l.getValue("FID_{name}".format(
                name=fld_tag
            )))
            if fid_entity not in u:
                u.append(fid_entity)
            l = c.next()
            return l
    
    def WritePopLessXMin(shp, fld_pop, lst_intersected):
        add_field(shp, "poxX", "SHORT", "8")
        cursor = arcpy.UpdateCursor(shp)
        linha = cursor.next()
        while linha:
            bgri = int(linha.getValue("FID"))
            if bgri in lst_intersected:
                p = int(linha.getValue(fld_pop))
                linha.setValue("popX", p)
                cursor.UpdateRow(linha)
            linha = cursor.next()
        return "popX"
    
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = w
    
    # Procedure #
    # Generate Service Area
    ServiceArea = service_area_polygon(
        net_dataset, rdv_name, junctions_name, interval, locations,
        "servarea.shp"
    )
    
    # Intersect unities with Service Area
    lyr_unities = feat_lyr(unities)
    unities_servarea = intersect(
        [lyr_unities, ServiceArea], "unidades_mx.shp"
    )
    
    # Get the FID of the unities that intersects with the service area
    id_unities = GetUnitiesIntersected(unities_servarea, unities)
    # Update original shape with the population a menos de x minutes
    fld_pop_less_x = WritePopLessXMin(lyr_unities, fld_pop, id_unities)
    groups = dissolve(
        lyr_unities, output, fld_groups,
        "{pop} SUM;{popx} SUM".format(
            pop=fld_pop, popx=fld_pop_less_x
        )
    )
    # Estimate population percent
    if len(fld_pop) > 6:
        fld_pop_tag = fld_pop[:6]
    else:
        fld_pop_tag = fld_pop
    
    add_field(shp, "lessX", "FLOAT", "8", "3")
    cursor = arcpy.UpdateCursor(output)
    linha = cursor.next()
    
    while linha:
        p = float(linha.getValue("SUM_{pop}".format(pop=fld_pop_tag)))
        pt = float(linha.getValue("SUM_{p}".format(p=fld_pop_less_x)))
        per = (p/pt)*100.0
        linha.setValue("lessX", per)
        cursor.updateRow(linha)
        linha = cursor.next()
    return output


def pop_less_dist_x2(net_dataset, rdv_name, locations, interval,
                     unities, fld_groups, fld_pop,
                     w, output, useOneway=None):
    """
    Network processing - executar service area de modo a conhecer as areas a
    menos de x minutos de qualquer coisa
    """
    
    import arcpy; import numpy; import os; import pandas
    from gasp.cpu.arcg.lyr             import feat_lyr
    from gasp.mng.genze                import dissolve
    from gasp.cpu.arcg.anls.ovlay      import intersect
    from gasp.cpu.arcg.mng.fld         import calc_fld
    from gasp.cpu.arcg.netanlst.svarea import service_area_polygon
    from gasp.fm.shp                   import shp_to_df
    from gasp.oss                      import get_filename
    from gasp.to.shp                   import df_to_shp
    from gasp.cpu.arcg.mng.fld         import del_field
    
    if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
    # Procedure #
    # Generate Service Area
    svArea = service_area_polygon(
        net_dataset, rdv_name, interval, locations,
        os.path.join(w, "servarea.shp"),
        ONEWAY_RESTRICTION=useOneway
    )
    
    # Dissolve Service Area
    svArea = dissolve(
        svArea, os.path.join(w, 'svarea_diss.shp'), "FID",
        api="arcpy"
    )
    
    # Intersect unities with Service Area
    lyr_unities = feat_lyr(unities)
    unities_servarea = intersect(
        [lyr_unities, svArea],
        os.path.join(w, "unidades_mx.shp")
    )
    
    # In the original Unities SHP, create a col with the population
    # only for the unities intersected with service area
    intersectDf = shp_to_df(unities_servarea)
    
    unities_less_than = intersectDf[fld_pop].unique()
    unities_less_than = pandas.DataFrame(unities_less_than, columns=['cod_'])
    
    popDf = shp_to_df(unities)
    popDf = popDf.merge(
        unities_less_than, how='outer',
        left_on=fld_pop, right_on="cod_"
    )
    popDf["less_than"] = popDf.cod_.fillna(value='0')
    popDf["less_than"] = numpy.where(popDf["less_than"] != '0', '1', '0')
    popDf["population"] = numpy.where(
        popDf["less_than"] == '1', popDf[fld_pop], 0
    )
    popDf["original"] = popDf[fld_pop]
    
    newUnities = df_to_shp(popDf, os.path.join(w, 'unities_pop.shp'))
    
    # Dissolve and Get result
    result = dissolve(
        newUnities, output, fld_groups,
        statistics="original SUM;population SUM",
        api="arcpy"
    )
    
    calc_fld(
        result, "pop_{}".format(interval),
        "[SUM_popula]",
        {"TYPE" : "INTEGER", "LENGTH" : "10", "PRECISION" : ""}
    )
    
    calc_fld(
        result, fld_pop,
        "[SUM_origin]",
        {"TYPE" : "INTEGER", "LENGTH" : "10", "PRECISION" : ""}
    )
    
    calc_fld(
        result, "pop_{}_p".format(interval),
        "([pop_{}] / [{}]) *100".format(interval, fld_pop),
        {"TYPE" : "DOUBLE", "LENGTH" : "6", "PRECISION": "2"}
    )
    
    del_field(result, "SUM_popula")
    del_field(result, "SUM_origin")
    
    return result

def mean_time_in_povoated_areas(network, rdv_name, stat_units, popFld,
                                destinations, output, workspace,
                                ONEWAY=True, GRID_REF_CELLSIZE=10):
    """
    Receive statistical units and some destinations. Estimates the mean distance
    to that destinations for each statistical unit.
    The mean for each statistical will be calculated using a point grid:
    -> Statistical unit to grid point;
    -> Distance from grid point to destination;
    -> Mean of these distances.
    
    This method will only do the math for areas (statistic units)
    with population.
    """
    
    import os; import arcpy
    from gasp.cpu.arcg.lyr              import feat_lyr
    from gasp.cpu.arcg.anls.exct        import select_by_attr
    from gasp.cpu.arcg.mng.fld          import field_statistics
    from gasp.cpu.arcg.mng.fld          import add_field
    from gasp.cpu.arcg.mng.gen          import merge
    from gasp.cpu.arcg.mng.gen          import copy_features
    from gasp.cpu.arcg.netanlst.closest import closest_facility
    from gasp.to.shp.arcg               import rst_to_pnt
    from gasp.to.rst.arcg               import shp_to_raster
    
    if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
    
    else:
        raise ValueError('Network analyst extension is not avaiable')
    
    arcpy.env.overwriteOutput = True
    
    WORK = workspace
    
    # Add field
    stat_units = copy_features(
        stat_units, os.path.join(WORK, os.path.basename(stat_units))
    )
    add_field(stat_units, "TIME", "DOUBLE", "10", precision="3")
    
    # Split stat_units into two layers
    # One with population
    # One with no population
    withPop = select_by_attr(stat_units, '{}>0'.format(popFld),
                             os.path.join(WORK, 'with_pop.shp'))
    noPop   = select_by_attr(stat_units, '{}=0'.format(popFld),
                             os.path.join(WORK, 'no_pop.shp'))
    
    # For each statistic unit with population
    withLyr = feat_lyr(withPop)
    cursor  = arcpy.UpdateCursor(withLyr)
    
    FID = 0
    for feature in cursor:
        # Create a new file
        unity = select_by_attr(
            withLyr, 'FID = {}'.format(str(FID)),
            os.path.join(WORK, 'unit_{}.shp'.format(str(FID)))
        )
        
        # Convert to raster
        rst_unity = shp_to_raster(
            unity, "FID",
            os.path.join(WORK, 'unit_{}.tif'.format(str(FID))),
            GRID_REF_CELLSIZE
        )
        
        # Convert to point
        pnt_unity = rst_to_pnt(
            rst_unity, 
            os.path.join(WORK, 'pnt_un_{}.shp'.format(str(FID)))
        )
        
        # Execute closest facilitie
        CLOSEST_TABLE = os.path.join(
            WORK, 'cls_fac_{}.dbf'.format(str(FID))
        )
        closest_facility(
            network, rdv_name, destinations, pnt_unity,
            CLOSEST_TABLE, 
            oneway_restriction=ONEWAY
        )
        
        # Get Mean
        MEAN_TIME = field_statistics(CLOSEST_TABLE, 'Total_Minu', 'MEAN')[0]
        
        # Record Mean
        feature.setValue("TIME", MEAN_TIME)
        cursor.updateRow(feature)
        
        FID += 1
    
    merge([withPop, noPop], output)
    
    return output


def population_within_point_buffer(netDataset, rdvName, pointShp, populationShp,
                                   popField, bufferDist, epsg, output,
                                   workspace=None, bufferIsTimeMinutes=None,
                                   useOneway=None):
    """
    Assign to points the population within a certain distance (metric or time)
    
    * Creates a Service Area Polygon for each point in pointShp;
    * Intersect the Service Area Polygons with the populationShp;
    * Count the number of persons within each Service Area Polygon
    (this number will be weighted by the area % of the statistic unit
    intersected with the Service Area Polygon).
    """
    
    import arcpy; import os
    from geopandas                     import GeoDataFrame
    from gasp.cpu.arcg.lyr             import feat_lyr
    from gasp.cpu.arcg.anls.ovlay      import intersect
    from gasp.cpu.arcg.mng.gen         import copy_features
    from gasp.cpu.arcg.mng.fld         import add_geom_attr
    from gasp.cpu.arcg.mng.fld         import add_field
    from gasp.cpu.arcg.mng.fld         import calc_fld
    from gasp.mng.genze                import dissolve
    from gasp.cpu.arcg.netanlst.svarea import service_area_use_meters
    from gasp.cpu.arcg.netanlst.svarea import service_area_polygon
    from gasp.fm.shp                   import shp_to_df
    from gasp.to.shp                   import df_to_shp
    
    workspace = os.path.dirname(pointShp) if not workspace else workspace
    
    if not os.path.exists(workspace):
        from gasp.oss.ops import create_folder
        workspace = create_folder(workspace, overwrite=False)
    
    # Copy population layer
    populationShp = copy_features(populationShp, os.path.join(
        workspace, 'cop_{}'.format(os.path.basename(populationShp))
    ))
    
    # Create layer
    pntLyr = feat_lyr(pointShp)
    popLyr = feat_lyr(populationShp)
    
    # Create Service Area
    if not bufferIsTimeMinutes:
        servArea = service_area_use_meters(
            netDataset, rdvName, bufferDist, pointShp,
            os.path.join(workspace, 'servare_{}'.format(
                os.path.basename(pointShp))),
            OVERLAP=False, ONEWAY=useOneway
        )
    
    else:
        servArea = service_area_polygon(
            netDataset, rdvName, bufferDist, pointShp,
            os.path.join(workspace, "servare_{}".format(
                os.path.basename(pointShp))),
            ONEWAY_RESTRICTION=useOneway, OVERLAP=None
        )
    
    servAreaLyr = feat_lyr(servArea)
    
    # Add Column with Polygons area to Feature Class population
    add_geom_attr(popLyr, "total", geom_attr="AREA")
    
    # Intersect buffer and Population Feature Class
    intSrc = intersect([servAreaLyr, popLyr], os.path.join(
        workspace, "int_servarea_pop.shp"
    ))
    
    intLyr = feat_lyr(intSrc)
    
    # Get area of intersected statistical unities with population
    add_geom_attr(intLyr, "partarea", geom_attr="AREA")
    
    # Get population weighted by area intersected
    calc_fld(
        intLyr, "population",
        "((([partarea] * 100) / [total]) * [{}]) / 100".format(popField),
        {"TYPE" : "DOUBLE", "LENGTH" : "10", "PRECISION" : "3"}
    )
    
    # Dissolve service area by Facility ID
    diss = dissolve(
        intLyr, os.path.join(workspace, 'diss_servpop.shp'),
        "FacilityID", statistics="population SUM"
    )
    
    # Get original Point FID from FacilityID
    calc_fld(
        diss, "pnt_fid", "[FacilityID] - 1",
        {"TYPE" : "INTEGER", "LENGTH" : "5", "PRECISION" : None}
    )
    
    dfPnt  = shp_to_df(pointShp)
    dfDiss = shp_to_df(diss)
    
    dfDiss.rename(columns={"SUM_popula": "n_pessoas"}, inplace=True)
    
    resultDf = dfPnt.merge(
        dfDiss, how='inner', left_index=True, right_on="pnt_fid"
    )
    
    resultDf.drop('geometry_y', axis=1, inplace=True)
    
    resultDf = GeoDataFrame(
        resultDf, crs={'init' : 'epsg:{}'.format(epsg)},
        geometry='geometry_x'
    )
    
    df_to_shp(resultDf, output)
    
    return output


"""
Pandas and Google Maps Based Solutions
"""
def gdl_mean_time_wByPop(unities, unities_groups, population_field,
                     destinations, output, workspace=None,
                     unities_epsg=4326,
                     destinations_epsg=4326):
    """
    Tempo medio ponderado pela populacao residente a infra-estrutura mais 
    proxima
    
    # TODO: Migrate to Pandas
    """
    
    import os
    from osgeo                   import ogr
    from gasp.cpu.gdl            import drv_name
    from gasp.fm.shp             import points_to_list
    from gasp.cpu.gdl.mng.feat   import feat_to_pnt
    from gasp.cpu.gdl.mng.prj    import project_geom
    from gasp.cpu.gdl.mng.fld    import add_fields
    from gasp.cpu.gdl.mng.genze  import ogr_dissolve
    from gasp.cpu.glg.directions import get_time_pnt_destinations
    
    workspace = workspace if workspace else \
        os.path.dirname(output)
    
    # Unities to centroid
    pnt_unities = feat_to_pnt(
        unities,
        os.path.join(
            workspace, 'pnt_' + os.path.basename(unities))
    )
    
    # List destinations
    lst_destinies = points_to_list(
        destinations, listVal="dict",
        inEpsg=destinations_epsg, outEpsg=4326
    )
    
    # Calculate indicator
    polyUnit = ogr.GetDriverByName(
        drv_name(unities)).Open(unities, 1)
    
    polyLyr = polyUnit.GetLayer()
    
    polyLyr = add_fields(polyLyr, {'meantime': ogr.OFTReal})
    
    pntUnit = ogr.GetDriverByName(
        drv_name(pnt_unities)).Open(pnt_unities, 0)
    
    pntLyr = pntUnit.GetLayer()
    
    polyFeat = polyLyr.GetNextFeature()
    distUnities = {}
    groups = {}
    for pntFeat in pntLyr:
        geom = pntFeat.GetGeometryRef()
        
        if unities_epsg == 4326:
            originGeom = geom
        else:
            originGeom = project_geom(geom, unities_epsg, 4326)
        
        _id, duration, distance = get_time_pnt_destinations(
            originGeom, lst_destinies
        )
        
        __min = duration['value'] / 60.0
        pop = polyFeat.GetField(population_field)
        group = polyFeat.GetField(unities_groups)
        
        distUnities[polyFeat.GetFID()] = (__min, __min * pop)
        
        if group not in groups:
            groups[group] = __min * pop
        else:
            groups[group] += __min * pop
        
        polyFeat = polyLyr.GetNextFeature()
    
    del polyLyr
    polyUnit.Destroy()
    
    polyUnit = ogr.GetDriverByName(
        drv_name(unities)).Open(unities, 1)
        
    polyLyr = polyUnit.GetLayer()
    
    for feat in polyLyr:
        unitId = feat.GetFID()
        groupId = feat.GetField(unities_groups)
        
        indicator = (distUnities[unitId][1] / groups[groupId]) * distUnities[unitId][0]
        
        feat.SetField('meantime', indicator)
        
        polyLyr.SetFeature(feat)
    
    del polyLyr, pntLyr
    polyUnit.Destroy()
    pntUnit.Destroy()
    
    ogr_dissolve(
        unities, unities_groups, output,
        field_statistics={'meantime': 'SUM'}
    )