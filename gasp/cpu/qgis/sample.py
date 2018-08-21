def values_to_points(pnt, rst, out):
    import processing
    
    processing.runalg(
        "saga:addgridvaluestopoints",
        pnt, rst, 0, out
    )
    
    return out


def random_inside_poly(inPoly, nPoints, out):
    """
    Create random points inside polygons
    """
    
    processing.runalg(
        "qgis:randompointsinsidepolygonsfixed",
        inPoly,
        0, nPoints, 10,
        out
    )
    
    return out

