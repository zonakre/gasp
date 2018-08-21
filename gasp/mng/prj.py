# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Data Management Tools > Manage Spatial Reference Systems
"""

def project(inShp, outShp, outEPSG, inEPSG=None, gisApi='ogr'):
    """
    Project Geodata using GIS
    
    API's Available:
    * arcpy
    """
    
    if gisApi == 'arcpy':
        """
        Execute Data Management > Data Transformations > Projection
        """
        
        import arcpy
        from gasp.cpu.arcg.lyr import feat_lyr
        from gasp.fm.api.srorg import get_wkt_esri
        
        layer   = feat_lyr(inShp)
        srs_obj = get_wkt_esri(outEPSG)
        
        arcpy.Project_management(layer, outShp, srs_obj)
    
    elif gisApi == 'ogr':
        """
        Using ogr Python API
        """
        
        if not inEPSG:
            raise ValueError(
                'To use ogr API, you should specify the EPSG Code of the'
                ' input data using inEPSG parameter'
            )
        
        import os
        from osgeo                import ogr
        from gasp.prop.feat       import get_geom_type
        from gasp.prop.ff         import drv_name
        from gasp.cpu.gdl.mng.fld import ogr_copy_fields
        from gasp.cpu.gdl.mng.prj import get_trans_param, get_sref_from_epsg
        from gasp.oss             import get_filename
        
        def copyShp(out, outDefn, lyr_in, trans):
            for f in lyr_in:
                g = f.GetGeometryRef()
                g.Transform(trans)
                new = ogr.Feature(outDefn)
                new.SetGeometry(g)
                for i in range(0, outDefn.GetFieldCount()):
                    new.SetField(outDefn.GetFieldDefn(i).GetNameRef(), f.GetField(i))
                out.CreateFeature(new)
                new.Destroy()
                f.Destroy()
        
        # ####### #
        # Project #
        # ####### #
        transP = get_trans_param(inEPSG, outEPSG)
        
        inData = ogr.GetDriverByName(
            drv_name(inShp)).Open(inShp, 0)
        
        inLyr = inData.GetLayer()
        out = ogr.GetDriverByName(
            drv_name(outShp)).CreateDataSource(outShp)
        
        outlyr = out.CreateLayer(
            get_filename(outShp), get_sref_from_epsg(outEPSG),
            geom_type=get_geom_type(
                inShp, name=None, py_cls=True, gisApi='ogr'
            )
        )
        
        # Copy fields to the output
        ogr_copy_fields(inLyr, outlyr)
        # Copy/transform features from the input to the output
        outlyrDefn = outlyr.GetLayerDefn()
        copyShp(outlyr, outlyrDefn, inLyr, transP)
        
        inData.Destroy()
        out.Destroy()
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp

