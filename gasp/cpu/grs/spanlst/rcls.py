"""
Raster tools - GRASS GIS

GRASS GIS Tools translated to Python
"""

def interval_rules(dic, out_rules):
    """
    Write rules file for reclassify - in this method, intervals will be 
    converted in new values
    
    dic = {
        new_value1: {'base': x, 'top': y},
        new_value2: {'base': x, 'top': y},
        ...,
        new_valuen: {'base': x, 'top': y}
    }
    """
    
    import os
    
    if os.path.splitext(out_rules)[1] != '.txt':
        out_rules = os.path.splitext(out_rules)[0] + '.txt'
    
    with open(out_rules, 'w') as txt:
        for new_value in dic:
            txt.write(
                '{b} thru {t}  = {new}\n'.format(
                    b=str(dic[new_value]['base']),
                    t=str(dic[new_value]['top']),
                    new=str(new_value)
                )
            )
        txt.close()
    
    return out_rules

def category_rules(dic, out_rules):
    """
    Write rules file for reclassify - in this method, categorical values will be
    converted into new designations/values
    
    dic = {
        old_value : new_value,
        old_value : new_value,
        ...
    }
    """
    
    if os.path.splitext(out_rules)[1] != '.txt':
        out_rules = os.path.splitext(out_rules)[0] + '.txt'
    
    with open(out_rules, 'w') as txt:
        for k in dic:
            txt.write(
                '{o}  = {n}\n'.format(o=str(dic[k]), n=str(k))
            )
        
        txt.close()
    
    return out_rules


def reclassify(rst, out, regras):
    from grass.pygrass.modules import Module
    r = Module(
        'r.reclass', input=rst, output=out, rules=regras, overwrite=True,
        run_=False, quiet=True)
    r()


def set_null(rst, value, ascmd=None):
    """
    Null in Raster to Some value
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            'r.null', map=rst, setnull=value, run_=False, quiet=True
        )
        
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd("r.null map={} setnull={} --quiet".format(
            rst, value
        ))


def null_to_value(rst, value, as_cmd=None):
    """
    Give a numeric value to the NULL cells
    """
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        m = Module(
            'r.null', map=rst, null=value, run_=False, quiet=True
        )
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd("r.null map={} null={} --quiet".format(
            rst, value
        ))


def grass_erase_raster(rst_to_be_erased, erase_rst, interestVal, output, w):
    """
    Change to 0 the cells of the rst_to_be_erased that are in the same position
    of the ones in the erase_rst that have the interestVal.
    
    The inputs and output are GRASS Rasters
    """
    
    import os
    from osgeo        import gdal
    from gasp.cpu.grs import grass_converter
    from gasp.fm.rst  import rst_to_array
    from gasp.to.rst  import array_to_raster
    # TODO: find replace_value_where
    #from gasp    import array_replace_value_where
    
    to_be_erased = os.path.join(w, 'to_be_erased.tif')
    erase = os.path.join(w, 'erase_rst.tif')
    grass_converter(rst_to_be_erased, to_be_erased)
    grass_converter(erase_rst, erase)
    v_1 = rst_to_array(to_be_erased)
    v_2 = rst_to_array(erase)
    replaced = array_replace_value_where(
        v_1, v_2==value_to_erase, 0
    )
    pro_erased = os.path.join(w, output + '.tif')
    array_to_raster(
        replaced, pro_erased, to_be_erased, None,
        gdal.GDT_Int32, noData=None, gisApi='gdal'
    )
    grass_converter(pro_erased, output)
    return output

