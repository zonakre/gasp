"""
Hydrologic procedures
"""

def generate_waterlines(mdt, waterbodies, accumulation_value=500,
                        workspace=None):
    """
    Generate Water Bodies lines
    """
    
    import os
    from gasp.oss                    import get_fileformat
    from gasp.cpu.arcg.lyr           import rst_lyr
    from gasp.prop.ff                import vector_formats, raster_formats
    from gasp.spanlst.algebra        import rstcalc
    from gasp.cpu.arcg.spanlst.hydro import fill
    from gasp.cpu.arcg.spanlst.hydro import flow_accumulation
    from gasp.cpu.arcg.spanlst.hydro import flow_direction
    from gasp.cpu.arcg.spanlst.hydro import stream_to_feature
    
    workspace = workspace if workspace else \
        os.path.dirname(waterbodies)
    
    raster_format = os.path.splitext(os.path.basename(waterbodies))[1]
    
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    
    fill_rst = fill(mdt, 'flow_raster{}'.format(raster_format),
                    template=mdt)
    
    dire_rst = flow_direction(
        fill_rst, 'direction_raster{}'.format(raster_format),
        template=mdt
    )
    
    flow_acc = flow_accumulation(
        dire_rst, 'flow_raster{}'.format(raster_format),
        template=mdt
    )
    
    # Split water bodies from the other accumulation data
    lyr_flow = rst_lyr(flow_acc)
    
    outFormat = os.path.splitext(os.path.basename(waterbodies))[1]
    rstFormat = raster_formats()
    vecFormat = vector_formats()
    
    waterRst = waterbodies if outFormat in rstFormat else \
        os.path.join(
            workspace,
            os.path.splitext(os.path.basename(waterbodies))[0] + raster_format
        ) if outFormat in vecFormat else None
    
    if not waterRst:
        raise ValueError('Your output is not a raster and is not a vector')
    
    waterRst = rstcalc(
        '{r} > {a}'.format(
            r=os.path.splitext(os.path.basename(flow_acc))[0],
            a=str(accumulation_value)
        ),
        waterRst, template=mdt, api='arcpy'
    )
    
    if outFormat in vecFormat:
        stream_to_feature(waterRst, dire_rst, waterbodies)
        
        return waterbodies
    
    else:
        return waterRst



def GDAL_Hidric_Balance(meta_file=os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'HidricBalance_example.json')
    ):
    """
    Proper description
    """
    
    import os
    
    from gasp.fm.rst   import rst_to_array
    from gasp.to.rst   import array_to_raster
    from gasp.prop.rst import get_cellsize
    
    def DecodeJson(json_file):
        import json
        t = open(json_file, 'r')
        d = json.load(t)
        t.close()
        return d
    
    def SomaRstOnLst(l):
        for i in range(1, len(l)):
            l[i] = l[i] + l[i-1]
        return l[-1]
    
    def indexCaloricoAnual(tempMensal):
        lst_ICM = []
        c = 0
        for rst in tempMensal:
            rst_array = RasterToArray(rst)
            rst_icm = (rst_array / 5.0)**1.514
            lst_ICM.append(rst_icm)
        ica = SomaRstOnLst(lst_ICM)
        return ica
    
    def EvapotranspiracaoPotencial(tMensal, ICAnual, insolacao):
        dias_mes = [31,28,31,30,31,30,31,31,30,31,30,31]
        a = 0.492 + (0.0179 * ICAnual) - (0.0000771 * ICAnual**2) + (0.000000675 * ICAnual**3)
        lst_k = []
        ETP_value = []
        for mes in range(len(dias_mes)):
            k = (float(insolacao[mes]) * float(dias_mes[mes])) / 360.0
            lst_k.append(k)
        for raster in range(len(tMensal)):
            rst_array = RasterToArray(tMensal[raster])
            etp = 16.0 * ((10.0 * rst_array/ICAnual)**a)
            ETP = etp * lst_k[raster]
            ETP_value.append(ETP)
        return ETP_value
    
    def DefClimatico(precipitacao, EvapoT_Potencial):
        Exd_Hid = []
        dClimaC = []
        for raster in range(len(precipitacao)):
            rst_array = RasterToArray(precipitacao[raster])
            excedente_hidrico = rst_array - EvapoT_Potencial[raster]
            Exd_Hid.append(excedente_hidrico)
        for rst in range(len(Exd_Hid)):
            cop = np.zeros((Exd_Hid[rst].shape[0], Exd_Hid[rst].shape[1]))
            np.copyto(cop, Exd_Hid[rst], 'no')
            if rst == 0:
                np.place(cop, cop>0, 0)
                dClimaC.append(cop)
            else:
                np.place(cop, cop>0, 0)
                dClimaC.append(cop + dClimaC[rst-1])
        return [Exd_Hid, dClimaC]
    
    def reservaUtil(textura, excedenteHid, defice):
        lst_ru = []
        for rst in range(len(excedenteHid)):
            ru = textura * np.exp(defice[rst]/textura)
            np.copyto(ru, textura, 'no', defice[rst]==0)
            if rst == 0:
                lst_ru.append(ru)
            else:
                ex_hid_mes_anterior = np.zeros((ru.shape[0], ru.shape[1]))
                np.place(ex_hid_mes_anterior, excedenteHid[rst-1]<0, 1)
                ex_hid_este_mes = np.zeros((ru.shape[0], ru.shape[1]))
                np.place(ex_hid_este_mes, excedenteHid[rst]>0, 1)
                recarga = ex_hid_mes_anterior + ex_hid_este_mes
                no_caso_recarga = lst_ru[rst-1] + excedenteHid[rst]
                if 2 in np.unique(recarga):
                    np.copyto(ru, no_caso_recarga, 'no', recarga==2)
                else:
                    ex_hid_mes_anterior = np.zeros((ru.shape[0], ru.shape[1]))
                    np.place(ex_hid_mes_anterior, excedenteHid[rst-1]>0, 1)
                    ex_hid_este_mes = np.zeros((ru.shape[0], ru.shape[1]))
                    np.place(ex_hid_este_mes, excedenteHid[rst]>excedenteHid[rst-1], 1)
                    recarga = ex_hid_mes_anterior + ex_hid_este_mes
                    no_caso_recarga = lst_ru[rst-1] + excedenteHid[rst]
                    np.copyto(ru, no_caso_recarga, 'no', recarga==2)
                lst_ru.append(ru)
        return lst_ru
    
    def VariacaoReservaUtil(lst_ru):
        lst_vru = []
        for rst in range(len(lst_ru)):
            if rst == 0:
                vru = lst_ru[-1] - lst_ru[rst]
            else:
                vru = lst_ru[rst-1] - lst_ru[rst]
            lst_vru.append(vru)
        return lst_vru
    
    def ETR(precipitacao, vru, etp):
        lst_etr = []
        for rst in range(len(precipitacao)):
            p_array = RasterToArray(precipitacao[rst])
            etr = p_array + vru[rst]
            np.copyto(etr, etp[rst], 'no', p_array>etp[rst])
            lst_etr.append(etr)
        return lst_etr
    
    def DeficeHidrico(etp, etr):
        return [etp[rst] - etr[rst] for rst in range(len(etp))]
    
    rst_textura = rst_to_array(raster_textura)
    # Lista Raster com valores de precipitacao
    precipitacao=ListRaster(rst_precipitacao, "img")
    ica = indexCaloricoAnual(temperatura)
    n_dias = fileTexto(file_insolacao)
    EvapotranspiracaoP = EvapotranspiracaoPotencial(temperatura, ica, n_dias)
    Defice_climatico = DefClimatico(precipitacao, EvapotranspiracaoP)
    excedente_hidrico = Defice_climatico[0]
    defice_climatico_cumulativo = Defice_climatico[1]
    reserva_util = reservaUtil(rst_textura, excedente_hidrico, defice_climatico_cumulativo)
    vru = VariacaoReservaUtil(reserva_util)
    etr = ETR(precipitacao, vru, EvapotranspiracaoP)
    def_hidrico = DeficeHidrico(EvapotranspiracaoP, etr)
    # Soma defice hidrico
    rst_hidrico = SomaRstOnLst(def_hidrico)
    array_to_raster(
        rst_hidrico, rst_saida, temperatura[0],
        epsg, get_cellsize(temperatura[0], gisApi='gdal'), gdal.GDT_Float64,
        gisApi='gdal'
    )

