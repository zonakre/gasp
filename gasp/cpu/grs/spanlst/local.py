"""
GRASS GIS local Tools
"""

def combine(inA, inB, o, ascmd=None):
    """
    Combine Rasters
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
    
        c = Module(
            "r.cross", input=[inA, inB], output=o, flags='z', overwrite=True,
            run_=False, quiet=True
        )
    
        c()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "r.cross input={},{} output={} "
            "-z --overwrite --quiet"
        ).format(inA, inB, o))
    
    return o

