"""
Proximity
"""

def Buffer(inShp, geom_type, dist, outShp, cmdAS=None):
    
    if not cmdAS:
        from grass.pygrass.modules import Module
        
        bf = Module(
            "v.buffer", input=inShp, type=geom_type,
            distance=dist if type(dist) != str else None,
            column=dist if type(dist) == str else None,
            flags='t', output=outShp,
            overwrite=True, run_=False, quiet=True
        )
        
        bf()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.buffer input={} type={} layer=1 {}={} "
            "output={} -t --overwrite --quiet"
        ).format(
            inShp, geom_type,
            "column" if type(dist) == str else "distance",
            str(dist), outShp
        ))
    
    return outShp


def near(fromShp, toShp, nearCatCol='tocat', nearDistCol="todistance",
         maxDist=-1, as_cmd=None):
    """
    v.distance - Finds the nearest element in vector map 'to'
    for elements in vector map 'from'.
    """
    
    from gasp.cpu.grs.mng.tbl import add_field
    
    add_field(fromShp, nearCatCol , 'INTEGER', ascmd=as_cmd)
    add_field(fromShp, nearDistCol, 'DOUBLE PRECISION', ascmd=as_cmd)
    
    if not as_cmd:
        import grass.script as grass
        
        grass.run_command(
            "v.distance", _from=fromShp, to=toShp,
            upload='cat,dist',
            column='{},{}'.format(nearCatCol, nearDistCol),
            dmax=maxDist
        )
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.distance from={} to={} upload=cat,dist "
            "column={},{} dmax={}"
        ).format(fromShp, toShp, nearCatCol, nearDistCol, maxDist))

