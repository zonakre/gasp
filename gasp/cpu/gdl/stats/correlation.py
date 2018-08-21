"""
Execute statistic analysis using GDAL Library
"""


def pearson_correlation(x, y):
    """
    Pearson correlation between two raster images
    
    The images have to have the same reading order and the same size
    
    Is wise exclude the nodata values
    """
    
    import numpy
    from gasp.fm.rst import rst_to_array
    
    vx = rst_to_array(x, flatten=True, with_nodata=False)
    vy = rst_to_array(y, flatten=True, with_nodata=False)
    
    
    cof = numpy.corrcoef(vx, vy)[0, 1]
    
    return cof

def pearson_obsolete(imagem1, imagem2):
    from osgeo import gdal
    import numpy as n
    img_1 = gdal.Open(imagem1)
    img_1_array = img_1.ReadAsArray()
    list_img1 = []
    nodata = 0
    for i in img_1_array:
        for e in i:
            if e < -1:
                nodata +=1
            else: 
                list_img1.append(float(e))
    print "Nodata imagem 1 - " + str(nodata)
    img_2 = gdal.Open(imagem2)
    img_2_array = img_2.ReadAsArray()
    list_img2 = []
    nodata = 0
    for i in img_2_array: 
        for e in i:
            if e < -1:
                nodata +=1
            else:
                list_img2.append(float(e))
    print "Nodata imagem 2 - " + str(nodata)
    count = len(list_img1)
    print "imagem 1: " + str(count)
    count = len(list_img2)
    print "imagem 2: " + str(count)
    # Cálculo das médias
    aux1 = 0
    aux2 = 0
    for i in range(len(list_img1)):
        valor_amostra1 = list_img1[i]
        valor_amostra2 = list_img2[i]
        somaAmostra1 = valor_amostra1 + aux1
        aux1 = somaAmostra1
        somaAmostra2 = valor_amostra2 + aux2
        aux2 = somaAmostra2
    media_amostra1 = somaAmostra1/float(len(list_img1))
    print "numero total observacoes - amostra 1 " + str(len(list_img1))
    print "somatorio das observacoes - amostra 1 " + str(somaAmostra1)
    media_amostra2 = somaAmostra2/float(len(list_img2))
    print "numero total observacoes - amostra 2 " + str(len(list_img2))
    print "somatorio das observacoes - amostra 2 " + str(somaAmostra2)
    del aux1, aux2
    # Cálcula o coeficiente de Pearson
    aux = 0
    aux2 = 0
    aux3 = 0
    for i in range(len(list_img1)):
        valor_X = list_img1[i]
        valor_Y = list_img2[i]
        soma = (valor_X - media_amostra1) * (valor_Y - media_amostra2)
        somatorio = soma + aux
        aux = somatorio
        den_X = (valor_X - media_amostra1)**2
        den_Xomatorio = den_X + aux2
        aux2 = den_Xomatorio
        den_Y = (valor_Y - media_amostra2)**2
        den_Yomatorio = den_Y + aux3
        aux3 = den_Yomatorio
    raiz_X = (den_Xomatorio)**0.5
    raiz_Y = (den_Yomatorio)**0.5
    denominador = raiz_X * raiz_Y
    correlacao = somatorio / denominador
    print "Correlacao = " + str(correlacao)


def speraman_correlation(x, y):
    """
    Speraman correlation between two raster images
    
    The images have to have the same reading order and the same size
    Is wise exclude the nodata values
    """
    
    from scipy       import stats
    from decimal     import Decimal
    from gasp.to.rst import rst_to_array
    
    vx = rst_to_array(x, flatten=True, with_nodata=False)
    vy = rst_to_array(y, flatten=True, with_nodata=False)
    
    coef = stats.spearmanr(vx, vy, axis=0)
    
    return Decimal(coeficiente[0])

