"""
Array to a Feature Class - OGR Compilant
"""

from osgeo import ogr

def array_to_shp(array_like, outFile, x='x', y='y', epsg=None):
    """
    Convert a array with geometric data into a file with geometry (GML, ESRI
    Shapefile or others).
    
    Example of an array_like object:
    data = [
        {col_1: value, col_2: value, x: value, y: value},
        {col_1: value, col_2: value, x: value, y: value},
    ]
    
    This array must contain a 'x' and 'y' keys (or 
    equivalent).
    
    TODO: Now works only for points
    """
    
    import os
    from gasp                 import unicode_to_str
    from gasp.cpu.gdl         import drv_name, create_point
    from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
    from gasp.cpu.gdl.mng.fld import map_pyType_fldCode
    from gasp.oss             import get_filename
    
    ogr.UseExceptions()
    
    # Create output file
    shp = ogr.GetDriverByName(drv_name(outFile)).CreateDataSource(outFile)
    
    lyr = shp.CreateLayer(
        get_filename(outFile),
        None if not epsg else get_sref_from_epsg(epsg),
        geom_type=ogr.wkbPoint,
    )
    
    # Create fields of output file
    fields = []
    keys_fields = {}
    for k in array_like[0]:
        if k != x and k != y:
            fld_name = k[:9]
            if type(fld_name) == unicode:
                fld_name = unicode_to_str(fld_name)
            
            if fld_name not in fields:
                fields.append(fld_name)
            
            else:
                # Get All similar fields in the fields list
                tmp_fld = []
                for i in fields:
                    if i[:8] == fld_name[:8]:
                        tmp_fld.append(i[:8])
                
                c = len(tmp_fld)
                
                fld_name = fld_name[:8] + '_{n}'.format(n=str(c))
                
                fields.append(fld_name)
            
            # TODO: Automatic mapping of filters types needs further testing
            #fld_type = map_pyType_fldCode(array_like[0][k])
            lyr.CreateField(
                ogr.FieldDefn(fld_name, ogr.OFTString)
            )
            
            keys_fields[k] = fld_name
    
    defn = lyr.GetLayerDefn()
    
    for i in range(len(array_like)):
        feat = ogr.Feature(defn)
        feat.SetGeometry(
            create_point(array_like[i][x], array_like[i][y]))
        
        for k in array_like[i]:
            if k != x and k != y:
                value = array_like[i][k]
                if type(value) == unicode:
                    value = unicode_to_str(value)
                    if len(value) >= 254:
                        value = value[:253]
                
                feat.SetField(
                    keys_fields[k], value
                )
        
        lyr.CreateFeature(feat)
        
        feat = None
    
    shp.Destroy()


def osm_to_featurecls(xmlOsm, output, fileFormat='.shp', useXmlName=None):
    """
    OSM to ESRI Shapefile
    """

    import os
    from gasp.cpu.gdl.anls.exct import sel_by_attr
    
    # Convert xml to sqliteDB
    sqDB = ogr_btw_driver(xmlOsm, os.path.join(output, 'fresh_osm.sqlite'))

    # sqliteDB to Feature Class
    TABLES = ['points', 'lines', 'multilinestrings', 'multipolygons']
    
    for T in TABLES:
        sel_by_attr(
            sqDB, "SELECT * FROM {}".format(T),
            os.path.join(output, "{}{}{}".format(
                "" if not useXmlName else os.path.splitext(os.path.basename(xmlOsm))[0],
                T, fileFormat if fileFormat[0] == '.' else "." + fileFormat
            ))
        )

    return output


def getosm_to_featurecls(inBoundary, outVector, boundaryEpsg=4326,
                         vectorFormat='.shp'):
    """
    Get OSM Data from the Internet and convert the file to regular vector file
    """

    import os
    
    from gasp.fm.api.osm import download_by_boundary

    # Download data from the web
    osmData = download_by_boundary(
        inBoundary, os.path.join(outVector, 'fresh_osm.xml'), boundaryEpsg
    )

    # Convert data to regular vector file
    return osm_to_featurecls(
        osmData, outVector, fileFormat=vectorFormat
    )

