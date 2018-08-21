"""
Methods to extract OSM data from the internet
"""


def download_by_boundary(input_boundary, output_osm, epsg, area_threshold=None):
    """
    Download data from OSM using a bounding box
    """
    
    import os
    from decimal        import Decimal
    from gasp.prop.feat import feat_count
    from gasp.prop.ext  import get_extent
    from gasp.web       import get_file
    
    # Check number of features
    number_feat = feat_count(input_boundary)
    if number_feat != 1:
        raise ValueError((
            'Your boundary has more than one feature. '
            'Only feature classes with one feature are allowed.'
        ))
    
    # Check boundary area
    if area_threshold:
        from gasp.cpu.gdl import area_to_dic
        d_area = area_to_dic(input_boundary)
        if d_area[0] > area_threshold:
            raise ValueError(
                '{} has more than than {} square meters'.format(
                    os.path.basename(input_boundary),
                    str(area_threshold)
                )
            )
    
    # Get boundary extent
    left, right, bottom, top = get_extent(input_boundary, gisApi='ogr')
    
    if epsg != 4326:
        from gasp.cpu.gdl         import create_point
        from gasp.cpu.gdl.mng.prj import project_geom
        
        bottom_left = project_geom(
            create_point(left, bottom), epsg, 4326
        )
        
        top_right   = project_geom(
            create_point(right, top), epsg, 4326
        )
        
        left , bottom = bottom_left.GetX(), bottom_left.GetY()
        right, top    = top_right.GetX()  , top_right.GetY()
    
    bbox_str = ','.join([str(left), str(bottom), str(right), str(top)])
    
    url = "http://overpass-api.de/api/map?bbox={box}".format(box=bbox_str)
    
    osm_file = get_file(url, output_osm)
    
    return output_osm


def download_by_polygeom(inGeom, outOsm, epsg):
    """
    Download data from OSM using extent of a Polygon Object
    """
    
    from gasp.web import get_file
    
    # Transform polygon if necessary
    if epsg != 4326:
        from gasp.cpu.gdl.mng.prj import project_geom
        
        inGeom = project_geom(inGeom, epsg, 4326)
    
    # Get polygon extent
    left, right, bottom, top = inGeom.GetEnvelope()
    
    bbox_str = "{},{},{},{}".format(
        str(left), str(bottom), str(right), str(top))
    
    url = "https://overpass-api.de/api/map?bbox={}".format(bbox_str)
    
    osm_file = get_file(url, outOsm)
    
    return outOsm


def download_by_psqlext(psqlCon, table, geomCol, outfile):
    """
    Download OSM file using extent in PGTABLE
    """
    
    from gasp.cpu.psql.i import get_tbl_extent
    from gasp.web        import get_file
    
    ext = get_tbl_extent(psqlCon, table, geomCol)
    
    bbox_str = ",".join([str(x) for x in ext])
    
    url = "https://overpass-api.de/api/map?bbox={}".format(
        bbox_str
    )
    
    output = get_file(url, outfile)
    
    return output

