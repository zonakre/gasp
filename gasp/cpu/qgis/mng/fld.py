"""
QGIS Fields management
"""

def cria_campo(shape, campo):
    from gasp.qgis import vlayer
    lyr = vlayer(shape, "indf2")
    vpr = lyr.dataProvider()
    vpr.addAttributes([QgsField(campo, QVariant.Int)])

