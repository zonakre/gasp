def rgb2ihs(i_red, i_green, i_blue):
    from grass.pygrass.modules import Module
    transf = Module("i.rgb.his", red=i_red, green=i_green, blue=i_blue, hue="i_hue", intensity="i_intensity", saturation="i_saturation", overwrite=True, run_=False)
    transf()
def ihs2rgb(i_hue, i_saturacao, i_intensidade):
    from grass.pygrass.modules import Module
    trans = Module("i.his.rgb", hue=i_hue, intensity=i_intensidade, saturation=i_saturacao, red="t_red", green="t_green", blue="t_blue", overwrite=True, run_=False)
    trans()
   
def ihs(vermelho, verde, azul, pan, out_red, out_green, out_blue):
    # Carrega as imagens no belo do GRASS
    r_in_gdal(vermelho, "vermelho")
    r_in_gdal(verde, "verde")
    r_in_gdal(azul, "azul")
    r_in_gdal(pan, "pancromatica")
    rgb2ihs("vermelho", "verde", "azul")
    ihs2rgb("i_hue", "i_saturation", "pancromatica")
    r_out_gdal("t_red", out_red)
    r_out_gdal("t_green", out_green)
    r_out_gdal("t_blue", out_blue)

def ihs_pansharpen(vermelho, verde, azul, pancroma, saida, workspace):
    r_in_gdal(vermelho, "vermelho")
    r_in_gdal(verde, "verde")
    r_in_gdal(azul, "azul")
    r_in_gdal(pancroma, "pancromatica")
    from grass.pygrass.modules import Module
    output = Module("i.pansharpen", red="vermelho", green="verde", blue="azul", pan="pancromatica", output=saida, method="ihs")
    r_out_gdal(saida + "_red", workspace + "\\pansharped_red.tif")
    r_out_gdal(saida + "_green", workspace + "\\pansharped_green.tif")
    r_out_gdal(saida + "_blue", workspace + "\\pansharped_blue.tif")

