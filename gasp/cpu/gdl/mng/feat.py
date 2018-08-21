"""
Features management
"""

from osgeo import ogr


def polyline_to_points(inShp, outShp, attr=None, epsg=None):
    """
    Polyline vertex to Points
    
    TODO: See if works with Polygons
    """
    
    import os
    from osgeo                import ogr
    from gasp.cpu.gdl         import drv_name
    from gasp.cpu.gdl.mng.fld import ogr_copy_fields
    
    # Open Input
    polyData = ogr.GetDriverByName(drv_name(inShp)).Open(inShp)
    
    polyLyr = polyData.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from gasp.cpu.gdl.mng.prj import get_shp_sref
        srs = get_shp_sref(polyLyr)
    
    else:
        from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    # Create Output
    pntData = ogr.GetDriverByName(
        drv_name(outShp)).CreateDataSource(outShp)
    
    pntLyr = pntData.CreateLayer(
        os.path.splitext(os.path.basename(outShp))[0],
        srs, geom_type=ogr.wkbPoint
    )
    
    # Copy fields from input to output
    if attr:
        if attr == 'ALL':
            attr = None
        else:
            attr = [attr] if type(attr) != list else attr
        
        ogr_copy_fields(polyLyr, pntLyr, __filter=attr)
    
    # Polyline Vertex to Point Feature Class
    pntLyrDefn = pntLyr.GetLayerDefn()
    for feat in polyLyr:
        geom = feat.GetGeometryRef()
        
        # Get point count
        nrPnt = geom.GetPointCount()
        
        # Add point to a new feature
        for p in range(nrPnt):
            x, y, z = geom.GetPoint(p)
            
            new_point = ogr.Geometry(ogr.wkbPoint)
            new_point.AddPoint(x, y)
            
            new_feature = ogr.Feature(pntLyrDefn)
            new_feature.SetGeometry(new_point)
            
            if attr:
                for at in attr:
                    new_feature.SetField(at, feat.GetField(at))
            
            pntLyr.CreateFeature(new_feature)
            
            new_feature.Destroy()
    
    del pntLyr
    del polyLyr
    pntData.Destroy()
    polyData.Destroy()
    
    return outShp


def polylines_from_points(points, polylines, POLYLINE_COLUMN,
                          ORDER_FIELD=None, epsg=None):
    """
    Create a Polyline Table from a Point Table
    
    A given Point Table:
    FID | POLYLINE_ID | ORDER_FIELD
     0  |    P1       |      1
     1  |    P1       |      2
     2  |    P1       |      3
     3  |    P1       |      4
     4  |    P2       |      1
     5  |    P2       |      2
     6  |    P2       |      3
     7  |    P2       |      4
     
    Will be converted into a new Polyline Table:
    FID | POLYLINE_ID
     0  |    P1
     1  |    P2
     
    In the Point Table, the POLYLINE_ID field identifies the Polyline of that point,
    the ORDER FIELD specifies the position (first point, second point, etc.)
    of the point in the polyline.
    
    If no ORDER field is specified, the points will be assigned to polylines
    by reading order.
    """
    
    import os
    from osgeo                import ogr
    from gasp.cpu.gdl         import drv_name
    from gasp.cpu.gdl.mng.prj import ogr_def_proj
    from gasp.cpu.gdl.mng.fld import ogr_list_fields_defn
    from gasp.cpu.gdl.mng.fld import add_fields
    
    # TODO: check if geometry is correct
    
    # List all points
    pntSrc = ogr.GetDriverByName(
        drv_name(points)).Open(points)
    pntLyr = pntSrc.GetLayer()
    
    lPnt = {}
    cnt = 0
    for feat in pntLyr:
        # Get Point Geom
        geom = feat.GetGeometryRef()
        # Polyline identification
        polyline = feat.GetField(POLYLINE_COLUMN)
        # Get position in the polyline
        order = feat.GetField(ORDER_FIELD) if ORDER_FIELD else cnt
        
        # Store data
        if polyline not in lPnt.keys():
            lPnt[polyline] = {order: (geom.GetX(), geom.GetY())}
        
        else:
            lPnt[polyline][order] = (geom.GetX(), geom.GetY())
        
        cnt += 1
    
    # Write output
    lineSrc = ogr.GetDriverByName(
        drv_name(polylines)).CreateDataSource(polylines)
    
    if not epsg:
        from gasp.cpu.gdl.mng.prj import get_shp_sref
        srs = get_shp_sref(points)
    
    else:
        from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    lineLyr = lineSrc.CreateLayer(
        os.path.splitext(os.path.basename(polylines))[0],
        srs, geom_type=ogr.wkbLineString
    )
    
    # Create polyline id field
    fields_types = ogr_list_fields_defn(pntLyr)
    add_fields(
        lineLyr, {POLYLINE_COLUMN : fields_types[POLYLINE_COLUMN].keys()[0]}
    )
    
    polLnhDefns = lineLyr.GetLayerDefn()
    # Write lines
    for polyline in lPnt:
        new_feature = ogr.Feature(polLnhDefns)
        
        lnh = ogr.Geometry(ogr.wkbLineString)
        
        pnt_order = lPnt[polyline].keys()
        pnt_order.sort()
        
        for p in pnt_order:
            lnh.AddPoint(lPnt[polyline][p][0], lPnt[polyline][p][1])
        
        new_feature.SetField(POLYLINE_COLUMN, polyline)
        new_feature.SetGeometry(lnh)
        
        lineLyr.CreateFeature(new_feature)
        
        new_feature = None
    
    pntSrc.Destroy()
    lineSrc.Destroy()
    
    return polylines


def split_by_range(inShp, nr_feat, outFolder):
    """
    Split shp in several
    """
    
    import os
    from gasp.prop.feat         import feat_count
    from gasp.cpu.gdl.mng.fld   import lst_fld
    from gasp.cpu.gdl.anls.exct import sel_by_attr
    
    rowsN = feat_count(inShp, gisApi='ogr')
    
    nrShp = int(rowsN / float(nr_feat)) + 1
    
    fields = lst_fld(inShp)
    
    offset = 0
    c = 0
    table_name = os.path.splitext(os.path.basename(inShp))[0]
    for i in range(nrShp):
        sel_by_attr(
            inShp, 
            "SELECT * FROM {} ORDER BY {} LIMIT {} OFFSET {}".format(
                table_name, ', '.join(fields), str(nr_feat), str(offset)
            ),
            os.path.join(outFolder, table_name + '_{}.shp'.format(c))
        )
        
        offset += nr_feat
        c += 1


def feat_to_pnt(inShp, outPnt, epsg=None):
    """
    Get Centroid from each line in a PolyLine Feature Class
    """
    
    import os
    from osgeo                import ogr
    from gasp.cpu.gdl         import drv_name
    from gasp.cpu.gdl.mng.fld import ogr_copy_fields
    from gasp.cpu.gdl.mng.fld import lst_fld
    
    # TODO: check if geometry is correct
    
    # Open data
    polyData = ogr.GetDriverByName(
        drv_name(outPnt)).Open(inShp)
    
    polyLyr  = polyData.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from gasp.cpu.gdl.mng.prj import get_shp_sref
        srs = get_shp_sref(polyLyr)
    
    else:
        from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    # Create output
    pntData = ogr.GetDriverByName(
        drv_name(outPnt)).CreateDataSource(outPnt)
    
    pntLyr = pntData.CreateLayer(
        os.path.splitext(os.path.basename(outPnt))[0],
        srs, geom_type=ogr.wkbPoint
    )
    
    # Copy fields from input to output
    fields = lst_fld(polyLyr)
    ogr_copy_fields(polyLyr, pntLyr)
    
    pntLyrDefn = pntLyr.GetLayerDefn()
    for feat in polyLyr:
        geom = feat.GetGeometryRef()
        
        pnt = geom.Centroid()
        
        new_feat = ogr.Feature(pntLyrDefn)
        new_feat.SetGeometry(pnt)
        
        for fld in fields:
            new_feat.SetField(fld, feat.GetField(fld))
        
        pntLyr.CreateFeature(new_feat)
        
        new_feat.Destroy()
    
    del pntLyr
    del polyLyr
    pntData.Destroy()
    polyData.Destroy()
    
    return outPnt


def feat_to_newshp(inShp, outFolder, epsg=None):
    """
    Export all features in inShp to a new File
    """
    
    import os
    
    from gasp.cpu.gdl         import drv_name
    from gasp.prop.feat       import get_geom_type
    from gasp.cpu.gdl.mng.fld import lst_fld
    from gasp.cpu.gdl.mng.fld import ogr_copy_fields
    from gasp.oss             import get_fileformat, get_filename
    
    inDt = ogr.GetDriverByName(
        drv_name(inShp)).Open(inShp)
    
    lyr = inDt.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from gasp.cpu.gdl.mng.prj import get_shp_sref
        srs = get_shp_sref(lyr)
    
    else:
        from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    # Get fields name
    fields = lst_fld(lyr)
    
    # Get Geometry type
    geomCls = get_geom_type(inShp, gisApi='ogr', name=None, py_cls=True)
    
    # Read features and create a new file for each feature
    for feat in lyr:
        # Create output
        newShp = os.path.join(outFolder, "{}_{}{}".format(
            get_filename(inShp), str(feat.GetFID()),
            get_fileformat(inShp)
        ))
        
        newData = ogr.GetDriverByName(
            drv_name(newShp)).CreateDataSource(newShp)
        
        newLyr = newData.CreateLayer(
            get_filename(newShp), srs, geom_type=geomCls
        )
        
        # Copy fields from input to output
        ogr_copy_fields(lyr, newLyr)
        
        newLyrDefn = newLyr.GetLayerDefn()
        
        # Create new feature
        newFeat = ogr.Feature(newLyrDefn)
        
        # Copy geometry
        geom = feat.GetGeometryRef()
        newFeat.SetGeometry(geom)
        
        # Set fields attributes
        for fld in fields:
            newFeat.SetField(fld, feat.GetField(fld))
        
        # Save feature
        newLyr.CreateFeature(newFeat)
        
        newFeat.Destroy()
        
        del newLyr
        newData.Destroy()

