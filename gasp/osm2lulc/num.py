"""
OSM2LULC using Numpy
"""


def osm2lulc(osmdata, nomenclature, refRaster, lulcRst,
             epsg=3857, overwrite=None, dataStore=None):
    """
    Convert OSM data into Land Use/Land Cover Information
    
    A matrix based approach
    """
    
    # ************************************************************************ #
    # Python Modules from Reference Packages #
    # ************************************************************************ #
    import os; import numpy; import datetime
    from threading import Thread
    from osgeo     import gdal
    # ************************************************************************ #
    # Dependencies #
    # ************************************************************************ #
    from gasp.fm.rst         import rst_to_array
    from gasp.prop.rst       import get_cellsize
    from gasp.oss.ops        import create_folder, copy_file
    from gasp.osm2lulc.utils import osm_to_sqdb, osm_project, add_lulc_to_osmfeat
    from gasp.osm2lulc.mod1  import num_selection
    from gasp.osm2lulc.mod2  import num_roads
    from gasp.osm2lulc.m3_4  import num_selbyarea
    from gasp.osm2lulc.mod5  import num_base_buffer
    from gasp.osm2lulc.mod6  import num_assign_builds
    from gasp.to.rst         import array_to_raster
    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    if not os.path.exists(os.path.dirname(lulcRst)):
        raise ValueError('{} does not exist!'.format(os.path.dirname(lulcRst)))
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    from gasp.osm2lulc.var import osmTableData, PRIORITIES
    
    workspace = os.path.join(os.path.dirname(
        lulcRst), 'num_osmto') if not dataStore else dataStore
    
    # Check if workspace exists:
    if os.path.exists(workspace):
        if overwrite:
            create_folder(workspace, overwrite=True)
        else:
            raise ValueError('Path {} already exists'.format(workspace))
    else:
        create_folder(workspace, overwrite=None)
    
    CELLSIZE = get_cellsize(refRaster, xy=False, gisApi='gdal')
    time_b = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Convert OSM file to SQLITE DB #
    # ************************************************************************ #
    osm_db = osm_to_sqdb(osmdata, os.path.join(workspace, 'osm.sqlite'))
    time_c = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Add Lulc Classes to OSM_FEATURES by rule #
    # ************************************************************************ #
    add_lulc_to_osmfeat(osm_db, osmTableData, nomenclature)
    time_d = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Transform SRS of OSM Data #
    # ************************************************************************ #
    osmTableData = osm_project(osm_db, epsg)
    time_e = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # MapResults #
    # ************************************************************************ #
    mergeOut  = {}
    timeCheck = {}
    RULES = [1, 2, 3, 4, 5, 7]
    
    def run_rule(ruleID):
        time_start = datetime.datetime.now().replace(microsecond=0)
        _osmdb = copy_file(
            osm_db, os.path.splitext(osm_db)[0] + '_r{}.sqlite'.format(ruleID)
        )
        # ******************************************************************** #
        # 1 - Selection Rule #
        # ******************************************************************** #
        if ruleID == 1:
            res, tm = num_selection(
                _osmdb, osmTableData['polygons'], workspace,
                CELLSIZE, epsg, refRaster
            )
        
        # ******************************************************************** #
        # 2 - Get Information About Roads Location #
        # ******************************************************************** #
        elif ruleID == 2:
            res, tm = num_roads(
                _osmdb, nomenclature, osmTableData['lines'],
                osmTableData['polygons'], workspace, CELLSIZE, epsg,
                refRaster
            )
        
        # ******************************************************************** #
        # 3 - Area Upper than #
        # ******************************************************************** #
        elif ruleID == 3:
            res, tm = num_selbyarea(
                _osmdb, osmTableData['polygons'], workspace,
                CELLSIZE, epsg, refRaster, UPPER=True
            )
        
        # ******************************************************************** #
        # 4 - Area Lower than #
        # ******************************************************************** #
        elif ruleID == 4:
            res, tm = num_selbyarea(
                _osmdb, osmTableData['polygons'], workspace,
                CELLSIZE, epsg, refRaster, UPPER=False
            )
        
        # ******************************************************************** #
        # 5 - Get data from lines table (railway | waterway) #
        # ******************************************************************** #
        elif ruleID == 5:
            res, tm = num_base_buffer(
                _osmdb, osmTableData['lines'], workspace,
                CELLSIZE, epsg, refRaster
            )
        # ******************************************************************** #
        # 7 - Assign untagged Buildings to tags #
        # ******************************************************************** #
        elif ruleID == 7:
            if nomenclature != "GLOBE_LAND_30":
                res, tm = num_assign_builds(
                    _osmdb, osmTableData['points'], osmTableData['polygons'],
                    workspace, CELLSIZE, epsg, refRaster
                )
            
            else:
                return
        
        time_end = datetime.datetime.now().replace(microsecond=0)
        mergeOut[ruleID] = res
        timeCheck[ruleID] = {'total': time_end - time_start, 'detailed': tm}
    
    thrds = []
    for r in RULES:
        thrds.append(Thread(
            name="to_{}".format(str(r)), target=run_rule,
            args=(r,)
        ))
        
    
    for t in thrds: t.start()
    for t in thrds: t.join()
    
    # Merge all results into one Raster
    compileResults = {}
    for rule in mergeOut:
        for cls in mergeOut[rule]:
            if cls not in compileResults:
                if type(mergeOut[rule][cls]) == list:
                    compileResults[cls] = mergeOut[rule][cls]
                else:
                    compileResults[cls] = [mergeOut[rule][cls]]
            
            else:
                if type(mergeOut[rule][cls]) == list:
                    compileResults[cls] += mergeOut[rule][cls]
                else:
                    compileResults[cls].append(mergeOut[rule][cls])
    
    time_m = datetime.datetime.now().replace(microsecond=0)
    # All Rasters to Array
    arrayRst = {}
    for cls in compileResults:
        for raster in compileResults[cls]:
            if not raster:
                continue
            
            array = rst_to_array(raster)
            
            if cls not in arrayRst:
                arrayRst[cls] = [array.astype(numpy.int16)]
            
            else:
                arrayRst[cls].append(array.astype(numpy.int16))
    time_n = datetime.datetime.now().replace(microsecond=0)
    
    # Sum Rasters of each class
    for cls in arrayRst:
        if len(arrayRst[cls]) == 1:
            sumArray = arrayRst[cls][0]
        
        else:
            sumArray = arrayRst[cls][0]
            
            for i in range(1, len(arrayRst[cls])):
                sumArray = sumArray + arrayRst[cls][i]
        
        arrayRst[cls] = sumArray
    
    time_o = datetime.datetime.now().replace(microsecond=0)
    
    # Apply priority rule
    __priorities = PRIORITIES[nomenclature]
    
    for lulcCls in __priorities:
        if lulcCls not in arrayRst:
            continue
        else:
            numpy.place(arrayRst[lulcCls], arrayRst[lulcCls] > 0,
                lulcCls
            )
    
    for i in range(len(__priorities)):
        if __priorities[i] not in arrayRst:
            continue
        
        else:
            for e in range(i+1, len(__priorities)):
                if __priorities[e] not in arrayRst:
                    continue
                
                else:
                    numpy.place(arrayRst[__priorities[e]],
                        arrayRst[__priorities[i]] == __priorities[i], 0
                    )
    
    time_p = datetime.datetime.now().replace(microsecond=0)
    
    # Merge all rasters
    startCls = 'None'
    for i in range(len(__priorities)):
        if __priorities[i] in arrayRst:
            resultSum = arrayRst[__priorities[i]]
            startCls = i
            break
    
    if startCls == 'None':
        return 'NoResults'
    
    for i in range(startCls + 1, len(__priorities)):
        if __priorities[i] not in arrayRst:
            continue
        
        resultSum = resultSum + arrayRst[__priorities[i]]
    
    # Save Result
    numpy.place(resultSum, resultSum==0, -1)
    array_to_raster(
        resultSum, lulcRst, refRaster, epsg, gdal.GDT_Int16, noData=-1,
        gisApi='gdal'
    )
    
    time_q = datetime.datetime.now().replace(microsecond=0)
    
    return lulcRst, {
        0  : ('set_settings', time_b - time_a),
        1  : ('osm_to_sqdb', time_c - time_b),
        2  : ('cls_in_sqdb', time_d - time_c),
        3  : ('proj_data', time_e - time_d),
        4  : ('rule_1', timeCheck[1]['total'], timeCheck[1]['detailed']),
        5  : ('rule_2', timeCheck[2]['total'], timeCheck[2]['detailed']),
        6  : ('rule_3', timeCheck[3]['total'], timeCheck[3]['detailed']),
        7  : ('rule_4', timeCheck[4]['total'], timeCheck[4]['detailed']),
        8  : ('rule_5', timeCheck[5]['total'], timeCheck[5]['detailed']),
        9  : None if 7 not in timeCheck else (
            'rule_7', timeCheck[7]['total'], timeCheck[7]['detailed']),
        10 : ('rst_to_array', time_n - time_m),
        11 : ('sum_cls', time_o - time_n),
        12 : ('priority_rule', time_p - time_o),
        13 : ('merge_rst', time_q - time_p)
    }
