"""
Random
"""

from grass.pygrass.modules import Module

def create_random_points(vector, nr_pontos, saida):
    """
    Generate Random Points Feature Class
    """
    
    aleatorio = Module(
        "v.random", output=saida, npoints=nr_pontos,
        restrict=vector, overwrite=True, run_=False
    )
    aleatorio()
    
    return saida


def sample_to_points(points, col_name, rst):
    """
    v.what.rast - Uploads raster values at positions of vector
    points to the table.
    """
    
    m = Module(
        "v.what.rast", map=points, raster=rst,
        column=col_name,
        overwrite=True, run_=False, quiet=True
    )
    
    m()

