"""
Proximity tools
"""

import processing

def dist_buffer(inShp, dist, output):
    """
    Buffer using Qgis Tools
    """
    
    processing(
        "qgis:fixeddistancebuffer",
        inShp, 10, 5, True, output
    )
    
    return output

