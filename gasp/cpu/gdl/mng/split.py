"""
Splitting with OGR
"""


def splitShp_by_range(shp, nrFeat, outFolder):
    """
    Split one feature class by range
    """
    
    import os
    from gasp.oss               import get_filename, get_fileformat
    from gasp.cpu.gdl.prop.feat import feat_count
    from gasp.cpu.gdl.mng.fld   import lst_fld
    from gasp.cpu.gdl.anls.exct import sel_by_attr
    
    rowsN = feat_count(shp)
    
    nrShp = int(rowsN / float(nrFeat)) + 1 if nrFeat != rowsN else 1
    
    fields = lst_fld(shp)
    
    offset = 0
    exportedShp = []
    for i in range(nrShp):
        outShp = sel_by_attr(
            shp,
            "SELECT {cols}, geometry FROM {t} ORDER BY {cols} LIMIT {l} OFFSET {o}".format(
                t=os.path.splitext(os.path.basename(shp))[0],
                l=str(nrFeat), o=str(offset),
                cols=", ".join(fields)
            ),
            os.path.join(outFolder, "{}_{}{}".format(
                get_filename(shp, forceLower=True), str(i),
                get_fileformat(shp)
            ))
        )
        
        exportedShp.append(outShp)
        offset += nrFeat
    
    return exportedShp

