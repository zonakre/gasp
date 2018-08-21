"""
Visibility methods
"""

def gdal_viewshed(observation_sites, dem_rst, interest_points_rst, out_rst):
    """
    Viewshed using GDAL Library
    
    Procedure:
    1) 1 Local de observacao - 1 local interesse
    2) Obter segmento entre os 2 pontos
    3) Calcular a altitude para cada ponto do segmento usando a equação da recta
    4) Extrair a altitude do DTM para as celulas do segmento
    5) Calcular 3 - 4
    6) Se 3-4 > 0 - e visivel para todos
    se houver 1 <= 0 nao e visivel
    """
    
    