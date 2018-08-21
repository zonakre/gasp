"""
Clip rasters with ArcGIS
"""


def clip_raster(rst, feat_clip, out, template=None, snap=None, clipGeom=True):
    """
    Clip a single raster dataset
    """
    
    import arcpy
    
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    if snap:
        tempSnap = arcpy.env.snapRaster
        arcpy.env.snapRaster = snap
    
    clipGeom = "ClippingGeometry" if clipGeom else "NONE"
    arcpy.Clip_management(
        rst, "", out, feat_clip, "-3,402823e+038",
        clipGeom, "NO_MAINTAIN_EXTENT"
    )
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    if snap:
        arcpy.env.snapRaster = tempSnap
    
    return out


def clip_each_feature(rst, shp,
                      feature_id,
                      work, out_basename):
    """
    Clip a raster dataset for each feature in a feature class
    """

    import arcpy
    import os

    from gasp.cpu.arcg.lyr       import feat_lyr
    from gasp.cpu.arcg.lyr       import rst_lyr
    from gasp.cpu.arcg.anls.exct import select_by_attr
    from gasp.oss.ops            import create_folder

    # ########### #
    # Environment #
    # ########### #
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = work

    # ###### #
    # Do it! #
    # ###### #
    # Open feature class
    lyr_shp = feat_lyr(shp)
    lyr_rst = rst_lyr(rst)

    # Create folder for some temporary files
    wTmp = create_folder(os.path.join(work, 'tmp'))

    # Get id's field type
    fields = arcpy.ListFields(lyr_shp)
    for f in fields:
        if str(f.name) == str(feature_id):
            fld_type = f.type
            break
    
    expression = '{fld}=\'{_id}\'' if str(fld_type) == 'String' else \
        '{fld}={_id}'
    
    del fields, f

    # Run the clip tool for each feature in the shp input
    c = arcpy.SearchCursor(lyr_shp)
    l = c.next()
    while l:
        fid = str(l.getValue(feature_id))
        selection = select_by_attr(
            lyr_shp,
            expression.format(fld=feature_id, _id=fid),
            os.path.join(wTmp, 'each_{}.shp'.format(fid))
        )

        clip_rst = clip_raster(
            lyr_rst, selection, '{b}_{_id}.tif'.format(b=out_basename, _id=fid) 
        )

        l = c.next()


def clip_several_each_feature(rst_folder, shp, feature_id, work, template=None,
                              rst_file_format='.tif'):
    """
    Clip a folder of rasters by each feature in a feature class

    The rasters clipped for a feature will be in an individual folder
    """

    import arcpy
    import os

    from gasp.cpu.arcg.lyr       import feat_lyr
    from gasp.cpu.arcg.lyr       import rst_lyr
    from gasp.cpu.arcg.anls.exct import select_by_attr
    from gasp.cpu.arcg.mng.fld   import type_fields
    from gasp.oss.ops            import create_folder
    from gasp.oss                import list_files

    # ########### #
    # Environment #
    # ########### #
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = work

    # ###### #
    # Do it! #
    # ###### #
    # Open feature class
    lyr_shp = feat_lyr(shp)

    # Create folder for some temporary files
    wTmp = create_folder(os.path.join(work, 'tmp'))

    # Split feature class in parts
    c = arcpy.SearchCursor(lyr_shp)
    l = c.next()
    features = {}

    # Get id's field type
    fld_type = type_fields(lyr_shp, field=feature_id)

    expression = '{fld}=\'{_id}\'' if str(fld_type) == 'String' else \
        '{fld}={_id}'

    del fields, f

    while l:
        fid = str(l.getValue(feature_id))

        selection = select_by_attr(
            lyr_shp,
            expression.format(fld=feature_id, _id=fid),
            os.path.join(wTmp, 'each_{}.shp'.format(fid))
        )
        
        f_lyr = feat_lyr(selection)
        features[fid] = f_lyr

        l=c.next()

    rasters = list_files(rst_folder, file_format='.tif')

    for raster in rasters:
        r_lyr = rst_lyr(raster)
        for feat in features:
            clip_rst = clip_raster(
                r_lyr, features[feat],
                os.path.join(
                    work, os.path.splitext(os.path.basename(feat))[0],
                    os.path.basename(raster)
                ),
                template
            )


def clip_raster_each_feat_class(raster, clipFolder, outputFolder,
                                template=None, snap=None,
                                clipGeometry=None, clipFormat='.shp',
                                outputFormat='.tif'):
    """
    Clip a raster for each feature class in a folder
    """
    
    import os
    
    from gasp.oss import list_files, get_filename
    
    clipShp = list_files(clipFolder, file_format=clipFormat)
    
    outputFormat = outputFormat if outputFormat[0] == '.' else \
        '.' + outputFormat
    
    for shp in clipShp:
        clip_raster(
            raster, shp,
            os.path.join(
                outputFolder,
                get_filename(shp) + outputFormat
            ), 
            clipGeom=clipGeometry,
            template=template, snap=snap
        )

