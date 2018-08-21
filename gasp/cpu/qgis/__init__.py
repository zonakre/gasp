"""
QGIS methods
"""

def start_qgis_session_ubuntu():
    from qgis.core import *
    import sys
    
    app = QgsApplication([], False, None)
    app.setPrefixPath("/usr/bin", True)
    app.initQgis()
    
    sys.path.append("/usr/share/qgis/python/plugins")
    
    from processing.core.Processing import Processing
    
    Processing.initialize()


def vlayer(shp):
    import os
    from qgis.core import QgsVectorLayer
    
    return QgsVectorLayer(
        shp, os.path.splitext(os.path.basename(shp))[0], "ogr"
    )


def rlayer(rst):
    import os
    from qgis.core import QgsRasterLayer
    
    return QgsRasterLayer(rst, os.path.splitext(os.path.basename(rst))[0])

