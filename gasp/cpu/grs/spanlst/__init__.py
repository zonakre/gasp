"""
GIS API's subpackage:

GRASS GIS Python tools for raster data
"""


"""
Get Raster Properties
"""

def raster_report(rst, rel, _units=None, ascmd=None):
    """
    Units options:
    * Options: mi, me, k, a, h, c, p
    ** mi: area in square miles
    ** me: area in square meters
    ** k: area in square kilometers
    ** a: area in acres
    ** h: area in hectares
    ** c: number of cells
    ** p: percent cover
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
    
        report = Module(
            "r.report", map=rst, flags="h", output=rel,
            units=_units, run_=False, quiet=True
        )
    
        report()
    
    else:
        from gasp import exec_cmd, goToList
        
        rcmd = exec_cmd("r.report map={} output={}{} -h".format(
            rst, rel,
            " units={}".format(",".join(goToList(_units))) if _units else ""
        ))
    
    return rel


def sanitize_report(report):
    """
    Retrieve data from Report of a Raster
    """
    
    import codecs
    
    with codecs.open(report, 'r') as txt:
        rows = [lnh for lnh in txt]
        __rows = []
        l = [" ", "category", "."]
        
        c = 1
        for r in rows:
            if c <= 4:
                c += 1
                continue
            
            _r =  r.strip("\n")
            _r = _r.strip("|")
            
            for i in l:
                _r = _r.replace(i, "")
            
            _r = _r.replace(";", "|")
            
            __rows.append(_r.split("|"))
        
        __rows[0] = ['0', '1', '1'] + __rows[0][3:]
        
        return __rows[:-4]


def san_report_combine(report):
    from gasp.fm.txt          import txt_to_df
    from gasp.cpu.pnd.mng.fld import splitcol_to_newcols
    
    repdata = txt_to_df(report, _delimiter="z")
    
    repdata.rename(columns={repdata.columns.values[0] : 'data'}, inplace=True)
    repdata.drop([
        0, 1, 2, 3, repdata.shape[0]-1, repdata.shape[0]-2,
        repdata.shape[0]-3, repdata.shape[0]-4
    ], axis=0, inplace=True)
    
    repdata["data"] = repdata.data.str.replace(
        ' ', '').str.replace('.', '').str.replace(
            'category', '').str.replace(
                "Category", '').str.replace(';', '|')
    
    repdata["data"] = repdata.data.str[1:-1]
    
    repdata = splitcol_to_newcols(repdata, "data", "|", {
        0 : "new_value", 1 : "first_raster_val",
        2 : "second_raster_val", 3 : "n_cells"
    })
    
    return repdata


def get_rst_report_data(rst, UNITS=None):
    """
    Execute r.report and get reported data
    """
    
    import os
    from gasp         import random_str
    from gasp.oss.ops import del_file
    
    REPORT_PATH = raster_report(rst, os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "{}.txt".format(random_str(6))
    ), _units=UNITS)
    
    report_data = sanitize_report(REPORT_PATH)
    
    del_file(REPORT_PATH)
    
    return report_data


def get_cellsize(rst):
    import grass.script as grass
    
    dic = grass.raster.raster_info(rst)
    
    return dic['nsres']


"""
GRASS GIS Raster Calculator
"""
def mapcalc(equation, out, asCMD=None):
    """
    Raster Calculator
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
    
        rc = Module(
            'r.mapcalc',
            '{} = {}'.format(out, equation),
            overwrite=True, run_=False, quiet=True
        )
    
        rc()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "r.mapcalc \"{} = {}\" --overwrite --quiet"
        ).format(out, equation))
    
    return out


"""
Raster spatial analyst
"""
def rcost(cst, origin, out):
    """
    Return a acumulated cost surface
    """
    
    from grass.pygrass.modules import Module
    
    acum_cst = Module(
        'r.cost', input=cst, output=out, start_points=origin,
        overwrite=True, run_=False, quiet=True
    )
    
    acum_cst()
    
    return out


"""
Merge and Combine raster dataset
"""
def mosaic_raster(inRasterS, o, asCmd=None):
    """
    The GRASS program r.patch allows the user to build a new raster map the size
    and resolution of the current region by assigning known data values from
    input raster maps to the cells in this region. This is done by filling in
    "no data" cells, those that do not yet contain data, contain NULL data, or,
    optionally contain 0 data, with the data from the first input map.
    Once this is done the remaining holes are filled in by the next input map,
    and so on. This program is useful for making a composite raster map layer
    from two or more adjacent map layers, for filling in "holes" in a raster map
    layer's data (e.g., in digital elevation data), or for updating an older map
    layer with more recent data. The current geographic region definition and
    mask settings are respected.
    The first name listed in the string input=name,name,name, ... is the name of
    the first map whose data values will be used to fill in "no data" cells in
    the current region. The second through last input name maps will be used,
    in order, to supply data values for for the remaining "no data" cells.
    """
    
    if not asCmd:
        from grass.pygrass.modules import Module
    
        m = Module(
            "r.patch", input=inRasterS, output=o,
            overwrite=True, run_=False, quiet=True
        )
    
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd("r.patch input={} output={} --overwrite --quiet".format(
            ",".join(inRasterS), o
        ))
    
    return o


def rseries(lst, out, meth):
    
    from grass.pygrass.modules import Module
    
    serie = Module(
        'r.series', input=lst, output=out, method=meth,
        overwrite=True, quiet=True, run_=False
    )
    
    serie()
    
    return out


"""
Grouping and Zonal geometries
"""
def region_group(in_rst, out_rst, diagonal=True):
    """
    Equivalent to ArcGIS Region Group Tool
    
    r.clump finds all areas of contiguous cell category values in the input
    raster map. NULL values in the input are ignored. It assigns a unique
    category value to each such area ("clump") in the resulting output raster
    map.
    
    Category distinctions in the input raster map are preserved. This means
    that if distinct category values are adjacent, they will NOT be clumped
    together. The user can run r.reclass prior to r.clump to recategorize cells
    and reassign cell category values.
    """
    
    from grass.pygrass.modules import Module
    
    if diagonal:
        m = Module(
            'r.clump', input=in_rst, output=out_rst, flags='d',
            overwrite=True, quiet=True, run_=False
        )
    else:
        m = Module(
            'r.clump', input=in_rst, output=out_rst,
            overwrite=True, quiet=True, run_=False
        )
    
    m()
    
    return out_rst


def zonal_geometry(in_rst, out_rst, work):
    """
    Equivalent to ArcGIS Zonal Geometry Tool
    
    r.object.geometry calculates form statistics of raster objects in the input
    map and writes it to the output text file (or standard output if no output
    filename or '-' is given), with fields separated by the chosen separator.
    Objects are defined as clumps of adjacent cells with the same category
    value (e.g. output of r.clump or i.segment).
    """
    
    import os
    import codecs
    from grass.pygrass.modules     import Module
    from gasp.cpu.grs.spanlst.rcls import reclassify
    
    txt_file = os.path.join(work, 'report.txt')
    r_geometry = Module(
        'r.object.geometry', input=in_rst, output=txt_file, flags='m',
        separator=',', overwrite=True, quiet=True, run_=False
    )
    r_geometry()
    
    recls_rules = os.path.join(work, 'reclass.txt')
    opened_rules = open(txt_file, 'r')
    with codecs.open(recls_rules, 'w', encoding='utf-8') as f:
        c = 0
        for line in opened_rules.readlines():
            if not c:
                c+=1
            else:
                cols = line.split(',')
                f.write(
                    '{raster_value}  = {new_value} \n'.format(
                        raster_value=cols[0], new_value=str(int(float(cols[1])))
                    )
                )
        f.close()
        opened_rules.close()
    
    reclassify(in_rst, out_rst, recls_rules)
    
    return out_rst


"""
Tools for sampling
"""
def create_random_points_on_raster(inputRaster, nr_points, outVect):
    """
    Creates a raster map layer and vector point map containing
    randomly located points.
    """
    
    from grass.pygrass.modules import Module
    
    m = Module(
        "r.random", input=inputRaster, npoints=nr_points, vector=outVect,
        overwrite=True, run_=False, quiet=True
    )
    
    m()
    
    return outVect

