"""
Pseudo Views for download
"""


def down_zip(fileDir, fileName, fileFormat):
    """
    Prepare Download response for a zipped file
    """
    
    import os
    from django.http import HttpResponse
    
    zipFile = os.path.join(
        fileDir,
        '{}.{}'.format(fileName, fileFormat)
    )
    with open(zipFile, 'rb') as f:
        r = HttpResponse(f.read())
        
        r['content_type'] = 'application/zip'
        r['Content-Disposition'] = 'attachment;filename={}.{}'.format(
            fileName, fileFormat
        )
        
        return r


def down_xml(fileXml):
    """
    Prepare Download response for a xml file
    """
    
    import os
    from django.http import HttpResponse
    
    with open(fileXml, 'rb') as f:
        r = HttpResponse(f.read())
        
        r['content_type'] = 'text/xml'
        
        r['Content-Disposition'] = 'attachment;filename={}'.format(
            os.path.basename(fileXml)
        )
        
        return r


def down_tiff(tifFile):
    """
    Download tif image
    """
    import os
    
    from django.http import HttpResponse
    
    with open(tifFile, mode='rb') as img:
        r = HttpResponse(img.read())
        
        r['content_type'] = 'image/tiff'
        r['Content-Disposition'] = 'attachment;filename={}'.format(
            os.path.basename(tifFile)
        )
        return r


def db_table_to_kml(table, QUERY, outKml):
    """
    Query a database table and convert it to a KML File
    """
    
    import json
    import os
    from django.http         import HttpResponse
    from gasp.djg.mdl.serial import serialize_by_query_to_jsonfile
    from gasp.to.shp         import shp_to_shp
    
    # Write data in JSON
    JSON_FILE = os.path.join(
        os.path.dirname(outKml),
        os.path.splitext(os.path.basename(outKml))[0] + '.json'
    )
    
    serialize_by_query_to_jsonfile(table, QUERY, 'geojson', JSON_FILE)
    
    # Convert JSON into KML
    shp_to_shp(JSON_FILE, outKml, gisApi='ogr')
    
    # Create a valid DOWNLOAD RESPONSE
    with open(outKml, 'rb') as f:
        response = HttpResponse(f.read())
        
        response['content_type'] = 'text/xml'
        response['Content-Disposition'] = 'attachment;filename={}'.format(
            os.path.basename(outKml)
        )
        
        return response

