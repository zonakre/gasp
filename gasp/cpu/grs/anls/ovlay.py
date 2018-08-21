"""
Overlay operations with GRASS GIS
"""


def union(aShp, bShp, o, ascmd=None):
    """
    Union using GRASS GIS
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
    
        un = Module(
            "v.overlay", ainput=aShp, atype="area",
            binput=bShp, btype="area", operator="or",
            output=o, overwrite=True, run_=False, quiet=True
        )
    
        un()
    
    else:
        from gasp import exec_cmd
        
        outcmd = exec_cmd((
            "v.overlay ainput={} atype=area binput={} btype=area "
            "operator=or output={} --overwrite --quiet"
        ).format(aShp, bShp, o))
    
    return o


def erase(inShp, erase_feat, out, asCMD=None):
    """
    Difference operations between vectors
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        erase = Module(
            "v.overlay", ainput=inShp, atype="area",
            binput=erase_feat, btype="area", operator="not",
            output=out, overwrite=True, run_=False, quiet=True
        )
    
        erase()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.overlay ainput={} atype=area binput={} "
            "btype=area operator=not output={} "
            "--overwrite --quiet"
        ).format(inShp, erase_feat, out))
    
    return out


def vclip(inShp, clipShp, outShp, asCMD=None):
    """
    Extracts features of input map which overlay features of clip map.
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        vclip = Module(
            "v.clip", input=inShp, clip=clipShp,
            output=outShp, overwrite=True, run_=False
        )
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd(
            "v.clip input={} clip={} output={} --overwrite".format(
                inShp, clipShp, outShp
            )
        )
    
    return outShp


def intersection(aentrada, bentrada, saida):
    from grass.pygrass.modules import Module
    
    clip = Module(
        "v.overlay", ainput=aentrada, atype="area",
        binput=bentrada, btype="area", operator="and",
        output=saida,  overwrite=True, run_=False
    )
    
    clip()
    
    return saida


def intersection2(pontos, poligonos, outPut):
    """
    
    TODO: Needs generalization
    v.select or v.overlay?
    """
    
    from grass.pygrass.modules import Module
    
    intersect = Module(
        "v.select", ainput=pontos, atype='point',
        binput=poligonos, btype='area', output=outPut,
        operator='intersects', overwrite=True, run_=False)
    intersect()
    
    return outPut


"""
Edit Vectorial Feature Classes
"""

"""
V.edit possibilities
"""
def vedit_break(inShp, pntBreakShp,
                geomType='point,line,boundary,centroid'):
    """
    Use tool break
    """
    
    import os
    from grass.pygrass.modules import Module
    
    # Iterate over pntBreakShp to get all coords
    if os.path.isfile(pntBreakShp):
        from gasp.fm.shp import points_to_list
        lstPnt = points_to_list(pntBreakShp)
    else:
        from grass.pygrass.vector import VectorTopo
        
        pnt = VectorTopo(pntBreakShp)
        pnt.open(mode='r')
        lstPnt = ["{},{}".format(str(p.x), str(p.y)) for p in pnt]
    
    # Run v.edit
    m = Module(
        "v.edit", map=inShp, type=geomType, tool="break",
        coords=lstPnt,
        overwrite=True, run_=False, quiet=True
    )
    
    m()


def v_break_at_points(workspace, loc, lineShp, pntShp, conParam, srs, out_correct,
            out_tocorrect):
    """
    Split lines at points
    
    Use PostGIS to sanitize the result
    
    TODO: Confirm utility
    """
    
    import os
    from gasp.cpu.grs         import run_grass
    from gasp.cpu.psql.mng    import create_db
    from gasp.to.psql         import shp_to_psql_tbl
    from gasp.to.shp          import psql_to_shp
    from gasp.cpu.psql.mng.qw import ntbl_by_query
    from gasp.oss             import get_filename
    
    tmpFiles = os.path.join(workspace, loc)
    
    gbase = run_grass(workspace, location=loc, srs=srs)
    
    import grass.script       as grass
    import grass.script.setup as gsetup
    
    gsetup.init(gbase, workspace, loc, 'PERMANENT')
    
    from gasp.to.shp.grs import shp_to_grs, grs_to_shp
    
    grsLine = shp_to_grs(
        lineShp, get_filename(lineShp, forceLower=True)
    )
    
    vedit_break(grsLine, pntShp, geomType='line')
    
    LINES = grass_converter(
        grsLine, os.path.join(tmpFiles, grsLine + '_v1.shp'), 'line')
    
    # Sanitize output of v.edit.break using PostGIS
    create_db(conParam, conParam["DB"], overwrite=True)
    conParam["DATABASE"] = conParam["DB"]
    
    LINES_TABLE = shp_to_psql_tbl(
        conParam, LINES, srs,
        pgTable=get_filename(LINES, forceLower=True), api="shp2pgsql"
    )
    
    # Delete old/original lines and stay only with the breaked one
    Q = (
        "SELECT {t}.*, foo.cat_count FROM {t} INNER JOIN ("
            "SELECT cat, COUNT(cat) AS cat_count, "
            "MAX(ST_Length(geom)) AS max_len "
            "FROM {t} GROUP BY cat"
        ") AS foo ON {t}.cat = foo.cat "
        "WHERE foo.cat_count = 1 OR foo.cat_count = 2 OR ("
            "foo.cat_count = 3 AND ST_Length({t}.geom) <= foo.max_len)"
    ).format(t=LINES_TABLE)
    
    CORR_LINES = ntbl_by_query(
        conParam, "{}_corrected".format(LINES_TABLE), Q)
    
    # TODO: Delete Rows that have exactly the same geometry
    
    # Highlight problems that the user must solve case by case
    Q = (
        "SELECT {t}.*, foo.cat_count FROM {t} INNER JOIN ("
            "SELECT cat, COUNT(cat) AS cat_count FROM {t} GROUP BY cat"
        ") AS foo ON {t}.cat = foo.cat "
        "WHERE foo.cat_count > 3"
    ).format(t=LINES_TABLE)
    
    ERROR_LINES = ntbl_by_query(
        conParam, "{}_not_corr".format(LINES_TABLE), Q)
    
    psql_to_shp(
        conParam,  CORR_LINES, out_correct,
        api="pgsql2shp", geom_col="geom"
    )
    
    psql_to_shp(
        conParam, ERROR_LINES, out_tocorrect,
        api="pgsql2shp", geom_col="geom"
    )

