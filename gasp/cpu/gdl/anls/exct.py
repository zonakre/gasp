"""
Querying and analysing geographic information with OGR
"""
    
def ogr_select_by_location(shp, boundary_filter, filtered_output):
    """
    Filter a shp using the location of a boundary_filter shp
    
    For now the boundary must have only one feature
    
    Writes the filter on a new shp
    """
    
    import os
    from osgeo                import ogr
    from gasp.prop.ff         import drv_name
    from gasp.prop.feat       import get_geom_type
    from gasp.cpu.gdl.mng.gen import copy_features
    from gasp.cpu.gdl.mng.fld import ogr_copy_fields
    
    # Open main data
    dtSrc = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
    lyr = dtSrc.GetLayer()
    
    # Get filter geom
    filter_shp = ogr.GetDriverByName(
        drv_name(boundary_filter)).Open(boundary_filter, 0)
    filter_lyr = filter_shp.GetLayer()
    
    c = 0
    for f in filter_lyr:
        if c:
            break
        geom = f.GetGeometryRef()
        c += 1
    
    filter_shp.Destroy()
    
    # Apply filter
    lyr.SetSpatialFilter(geom)
    
    # Copy filter objects to a new shape
    out = ogr.GetDriverByName(
        drv_name(filtered_output)).CreateDataSource(filtered_output)
    
    outLyr  = out.CreateLayer(
        os.path.splitext(os.path.basename(filtered_output))[0],
        geom_type=get_geom_type(shp, gisApi='ogr', name=None, py_cls=True)
    )
    
    # Copy fields
    ogr_copy_fields(lyr, outLyr)
    
    copy_features(lyr, outLyr, outLyr.GetLayerDefn(), only_geom=False)


def get_attr_values_by_location(inShp, attr, geomFilter=None, shpFilter=None):
    """
    Get attributes of the features of inShp that intersects with geomFilter
    or shpFilter
    """
    
    from osgeo        import ogr
    from gasp.prop.ff import drv_name
    
    if not geomFilter and not shpFilter:
        raise ValueError(
            'A geom object or a path to a sho file should be given'
        )
    
    if shpFilter:
        # For now the shpFilter must have only one feature
        filter_shp = ogr.GetDriverByName(
            drv_name(shpFilter)).Open(shpFilter, 0)
        
        filter_lyr = filter_shp.GetLayer()
        c= 0
        for f in filter_lyr:
            if c:
                break
            
            geom = f.GetGeometryRef()
            c += 1
        
        filter_shp.Destroy()
    
    else:
        geom = geomFilter
    
    # Open Main data
    dtSrc = ogr.GetDriverByName(drv_name(inShp)).Open(inShp, 0)
    lyr = dtSrc.GetLayer()
    
    lyr.SetSpatialFilter(geom)
    
    # Get attribute values
    ATTRIBUTE_VAL = [feat.GetField(attr) for feat in lyr]
    
    dtSrc.Destroy()
    
    return ATTRIBUTE_VAL


def sel_by_attr(inShp, sql, outShp):
    """
    Select vectorial file and export to new file
    """
    
    from gasp         import exec_cmd
    from gasp.prop.ff import drv_name
    
    out_driver = drv_name(outShp)
    
    cmd = 'ogr2ogr -f "{drv}" {o} {i} -dialect sqlite -sql "{s};"'.format(
        o=outShp, i=inShp, s=sql, drv=out_driver
    )
    
    # Execute command
    outcmd = exec_cmd(cmd)
    
    return outShp


def split_whr_attrIsTrue(osm_fc, outputfolder, fields=None, sel_fields=None,
                         basename=None):
    """
    For each field in osm table or in fields, creates a new feature class 
    where the field attribute is not empty
    """

    import os
    from gasp.cpu.gdl.mng.fld import lst_fld

    # List table fields
    tbl_fields = fields if fields else lst_fld(osm_fc)

    if type(tbl_fields) == str or type(tbl_fields) == unicode:
        tbl_fields = [tbl_fields]

    if sel_fields:
        sel_fields.append('geometry')
        aux = 1

    else:
        aux = 0

    # Export each field in data
    outFilename = '{}.shp' if not basename else basename + '_{}.shp'
    for fld in tbl_fields:
        a = 0
        if not aux:
            sel_fields = ['geometry', fld]
        else:
            if fld not in sel_fields:
                sel_fields.append(fld)
                a += 1

        sel_by_attr(
            osm_fc,
            "SELECT {flds} FROM {t} WHERE {f}<>''".format(
                f=fld, t=os.path.splitext(os.path.basename(osm_fc))[0],
                flds=', '.join(sel_fields)
                ),
            os.path.join(
                outputfolder,
                outFilename.format(fld if fld.islower() else fld.lower())
            )
        )

        if a:
            sel_fields.remove(fld)

