def criar_shp_aPartirDeOutra(entrada, destino, momento):
    from qgis.core import QgsVectorFileWriter
    from osgeo import ogr
    
    from gasp.qgis import vlayer
    
    lyr = cria_layer(entrada, "indf", False)
    provider = lyr.dataProvider()
    
    if momento == 1: 
        writer = QgsVectorFileWriter(
            destino, provider.encoding(), provider.fields(),
            ogr.wkbPolygon,provider.crs()
        )
    
    elif momento == 2:
        writer = QgsVectorFileWriter(
            destino, provider.encoding(), provider.fields(),
            ogr.wkbPoint,provider.crs()
        )
    
    return destino


def merge_lyr(lstShp, out):
    """
    Merge Layers
    """
    
    import processing
    
    processing.runalg("saga:mergelayers", lstShp, True, True, out)
    
    return out

