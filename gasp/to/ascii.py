"""
To Ascii using GRASS GIS Tools
"""

def vector_to_ascii(grsVec, asciiTxt,
                    inGeom='point,line,boundary,centroid,area,face,kernel'):
    """
    Vector Map to ASCII File
    """ 
    
    m = Module(
        "v.out.ascii", input=grsVec, type=inGeom,
        output=asciiTxt, columns='*',
        overwrite=True, run_=False, quiet=True
    )
    
    m()