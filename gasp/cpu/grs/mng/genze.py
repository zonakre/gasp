"""
Generalization
"""


def dissolve(shp, out, field=None, asCMD=None):
    """
    Generalize Geometries
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
    
        diss = Module(
            "v.dissolve", input=shp, column=field, output=out,
            overwrite=True, run_=False, quiet=True
        )
    
        diss()
    
    else:
        from gasp import exec_cmd
        
        outCmd = exec_cmd((
            "v.dissolve input={}{} output={} "
            "--overwrite --quiet"
        ).format(shp, " column={}".format(field) if field else "", out))
    
    return out

