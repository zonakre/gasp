"""
Manage data with GRASS GIS
"""


def merge(in_lst, out):
    """
    Merge data from several layers into a new single layer
    """
    
    from grass.pygrass.modules import Module
    
    try:
        merge = Module('v.patch', input=in_lst, output=out,
                       flags='e', overwrite=True, run_=False, quiet=True)
        merge()
    except:
        merge = Module('v.patch', input=in_lst, output=out,
                       overwrite=True, run_=False, quiet=True)
        merge()
    
    return out

