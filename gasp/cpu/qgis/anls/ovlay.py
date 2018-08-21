"""
QGIS Overlay Tools
"""

import processing

def intersection(pontos, poligonos, saida):
    """
    QGIS Intersection
    """
    processing.runalg("qgis:intersection", pontos, poligonos, saida)
    
    return saida


def erase(inShp, eraseFeat, output):
    """
    QGIS Difference - equivalent to erase
    """
    
    processing.runalg(
        "qgis:difference", inShp, eraseFeat, output
    )
    
    return output

