"""
Features management
"""

def split(entrada, workspace_saida):
    import processing
    
    processing.runalg(
        "qgis:splitvectorlayer", entrada, "value",
        workspace_saida
    )


def copy_features(entrada, destino, geom):
    from qgis.core import QgsVectorFileWriter
    from osgeo import ogr
    
    lyr = cria_layer(entrada, "indf", False)
    provider = lyr.dataProvider()
    
    if geom == 1: 
        writer = QgsVectorFileWriter(
            destino, provider.encoding(),
            provider.fields(),
            ogr.wkbPolygon,
            provider.crs()
        )
    
    elif geom == 2:
        writer = QgsVectorFileWriter(
            destino, provider.encoding(),
            provider.fields(),
            ogr.wkbPoint, provider.crs()
        )
    
    return destino

