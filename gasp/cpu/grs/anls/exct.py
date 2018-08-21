"""
GIS API's subpackage:

GRASS GIS Python tools for vectorial data
"""

def extract(vector, _out_, whr, geomType="area", lyrN=1, ascmd=None):
    """
    v.extract
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
    
        m = Module(
            "v.extract", input=vector, type=geomType, layer=lyrN,
            where=whr, output=_out_, overwrite=True,
            run_=False, quiet=True
        )
    
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.extract input={} type={} layer={} where={} "
            "output={} --overwrite --quiet"
        ).format(vector, geomType, str(lyrN), whr, _out_))
    
    return _out_

