"""
GRASS Methods to convert to Vectorial data
"""

def shp_to_grs(inLyr, outLyr, filterByReg=None, asCMD=None):
    """
    Add Shape to GRASS GIS
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        f = 'o' if not filterByReg else 'ro'
        
        m = Module(
            "v.in.ogr", input=inLyr, output=outLyr, flags='o',
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.in.ogr input={} output={} -o{} --overwrite --quiet"
        ).format(inLyr, outLyr, " -r" if filterByReg else ""))
    
    return outLyr


def psql_to_grs(conParam, table, outLyr, where=None, notTable=None,
                filterByReg=None):
    """
    Add Shape to GRASS GIS from PGSQL
    """
    
    from gasp import exec_cmd
    
    rcmd = exec_cmd((
        "v.in.ogr input=\"PG:host={} dbname={} user={} password={} "
        "port={}\" output={} layer={}{}{}{} -o --overwrite --quiet" 
    ).format(conParam["HOST"], conParam["DATABASE"], conParam["USER"],
        conParam["PASSWORD"], conParam["PORT"], outLyr, table,
        "" if not where else " where=\"{}\"".format(where),
        " -t" if notTable else "",
        " -r" if filterByReg else ""
    ))
    
    return outLyr


def grs_to_shp(inLyr, outLyr, geomType, lyrN=1, asCMD=True, asMultiPart=None):
    """
    GRASS Vector to Shape File
    """
    
    from gasp.prop.ff import VectorialDrivers
    from gasp.oss     import get_fileformat
    
    vecDriv = VectorialDrivers()
    outEXT  = get_fileformat(outLyr)
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        __flg = None if not asMultiPart else 'm'
        
        m = Module(
            "v.out.ogr", input=inLyr, type=geomType, output=outLyr,
            format=vecDriv[outEXT], flags=__flg, layer=lyrN,
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.out.ogr input={} type={} output={} format={} "
            "layer={}{} --overwrite --quiet"  
        ).format(
            inLyr, geomType, outLyr, 
            vecDriv[outEXT], lyrN, " -m" if asMultiPart else ""
        ))
    
    return outLyr


def sqlite_to_shp(db, table, out, where=None, notTable=None,
                  filterByReg=None):
    """
    Execute a query on SQLITE DB and add data to GRASS GIS
    """
    
    from gasp import exec_cmd
    
    outCmd = exec_cmd(
        "v.in.ogr -o input={} layer={} output={}{}{}{}".format(
            db, table, out,
            "" if not where else " where=\"{}\"".format(where),
            " -t" if notTable else "",
            " -r" if filterByReg else ""
        )
    )
    
    return out

