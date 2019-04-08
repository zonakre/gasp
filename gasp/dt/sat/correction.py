"""
Imagery corrections
"""


def lnd8_dn_to_ref(folder, img_format, meta_json, outWorkspace, srs):
    """
    Landsat8 digital numbers to surface reflectance
    """
    
    import math
    import json
    import numpy
    import os
    
    from gasp.oss      import list_files
    from gasp.fm.rst   import rst_to_array
    from gasp.prop.rst import get_cellsize, rst_stats
    from gasp.to.rst   import array_to_raster
    
    
    def Get_RTA(Ml, Qcalc, Al):
        """
        Obtem Radiancia no Topo da Atmosfera
        
        Ml - relacao da radiancia multibanda
        Qcalc - imagem de satelite original
        Al - radiancia add band
        """
        
        Llambda = Ml * Qcalc + Al
        
        return Llambda
    
    def GetIrraSolar(d, Lmax, Pmax):
        """
        d - distancia da terra ao sol (com base no dia do ano em
        que a imagem foi recolhida)
        ESUN - irradiancia solar media exoatmosferica
        Lmax - radiancia maxima
        Pmax - reflectancia maxima
        """
        return (math.pi * d**2) * (Lmax/Pmax)
    
    def GetRefAparente(d, esun, rta, Z):
        """
        Reflectancia aparente
        Z - angulo zenital do sol
        """
        pp = math.pi * rta * d**2 / esun * math.cos(Z)
        return pp
    
    def GetRefSuperfice(DNmin, Ml, Al, IrrSolar, Z, d, RefAparente):
        """Reflectancia a superficie"""
        Lp = (Ml * DNmin + Al - 0.01 * IrrSolar) * (math.cos (Z) / math.pi * d**2)
        p = math.pi * (RefAparente - Lp) * d**2 / IrrSolar * math.cos(Z)
        return p
    
    lst_bands = list_files(folder, file_format=img_format)
    json_file = open(meta_json, 'r')
    json_data = json.load(json_file)
    cellsize = get_cellsize(lst_bands[0], gisApi='gdal')
    
    # Estimate Surface Reflectance for each band
    for bnd in lst_bands:
        # Convert images to numpy array
        img = rst_to_array(bnd)
        # Calculations of each pixel; store results on a new numpy array
        rta_array = Get_RTA(
            json_data[u"RADIANCE_MULT_BAND"][unicode(os.path.basename(bnd))],
            img,
            json_data[u"RADIANCE_ADD_BAND"][unicode(os.path.basename(bnd))]
        )
        solar_irradiation = GetIrraSolar(
            json_data[u"EARTH_SUN_DISTANCE"],
            json_data[u"RADIANCE_MAXIMUM_BAND"][unicode(os.path.basename(bnd))],
            json_data[u"REFLECTANCE_MAXIMUM_BAND"][unicode(os.path.basename(bnd))]   
        )
        ref_aparente_array = GetRefAparente(
            json_data[u"EARTH_SUN_DISTANCE"],
            solar_irradiation,
            rta_array,
            90 - json_data[u"SUN_ELEVATION"]
        )
        new_map = GetRefSuperfice(
            rst_stats(bnd, api='gdal')['MIN'],
            json_data[u"RADIANCE_MULT_BAND"][unicode(os.path.basename(bnd))],
            json_data[u"RADIANCE_ADD_BAND"][unicode(os.path.basename(bnd))],
            solar_irradiation,
            90 - json_data[u"SUN_ELEVATION"],
            json_data[u"EARTH_SUN_DISTANCE"],
            ref_aparente_array
        )
        array_to_raster(
            new_map,
            os.path.join(outWorkspace, os.path.basename(bnd)),
            bnd,
            srs,
            cellsize, 
            gdal.GDT_Float32, gisApi='gdal'
        )

