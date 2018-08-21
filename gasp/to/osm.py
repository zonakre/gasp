"""
To OpenStreetMap Files
"""


def osmosis_extract(boundary, osmdata, wepsg, w, output):
    """
    Extract OSM Data from a xml file with osmosis
    
    The extraction is done using the extent of a boundary
    """
    
    import os
    from decimal       import Decimal
    from gasp          import exec_cmd
    from gasp.prop.ext import get_extent
    from gasp.mng.prj  import project
    from gasp.to.shp   import shp_to_shp
    
    # Convert to ESRI Shapefile
    if os.path.splitext(boundary)[1] != '.shp':
        lmt = os.path.join(w, 'lmt_osmosis.shp')
        shp_to_shp(boundary, lmt, ogrApi='ogr')
    else:
        lmt = boundary
    
    # Convert boundary to WGS84 -EPSG 4326
    if int(wepsg) != 4326:
        wgs_lmt = project(
            lmt, os.path.join(w, 'lmt_wgs.shp'),
            4326, inEPSG=int(wepsg), gisApi='ogr'
        )
    else:
        wgs_lmt = lmt
    
    # Get boundary extent
    left, right, bottom, top = get_extent(wgs_lmt, gisApi='ogr')
    
    # Osmosis shell comand
    osmExt = os.path.splitext(osmdata)[1]
    osm_f  = 'enableDateParsing=no' if osmExt == '.xml' else ''
    
    cmd = (
        'osmosis --read-{_f} {p} file={_in} --bounding-box top={t} left={l}'
        ' bottom={b} right={r} --write-pbf file={_out}'
    ).format(
        _f = osmExt[1:], p = osm_f, _in = osmdata,
        t = str(top), l = str(left), b = str(bottom), r = str(right),
        _out = output
    )
    
    # Execute command
    outcmd = exec_cmd(cmd)
    
    return output


def select_highways(inOsm, outOsm):
    """
    Extract some tag from OSM file
    """
    
    import os
    from gasp import exec_cmd
    
    outExt = os.path.splitext(outOsm)[1]
    
    cmd = (
        'osmosis --read-xml enableDateParsing=no file={} --tf accept-ways '
        'highway=* --used-node --write-{} {}' 
    ).format(
        inOsm,
        "pbf" if outExt == ".pbf" else "xml", outOsm)
    
    outcmd = exec_cmd(cmd)
    
    return outOsm

