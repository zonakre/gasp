"""
Field Management Utils
"""

def rename_column(inShp, columns, output, api="ogr2ogr"):
    """
    Rename Columns in Shp
    
    TODO: For now implies output. In the future, it option will be removed
    """
    
    if api == "ogr2ogr":
        import os
        from gasp import goToList
        from gasp.cpu.gdl.mng.fld import lst_fld
        from gasp.oss import get_filename
        #from gasp.oss.ops import rename_files_with_same_name, del_file
        from gasp.cpu.gdl.anls.exct import sel_by_attr
        
        # List Columns
        cols = lst_fld(inShp)
        for c in cols:
            if c in columns:
                continue
            else:
                columns[c] = c
        
        columns["geometry"] = "geometry"
        
        """
        # Rename original shp
        newFiles = rename_files_with_same_name(
            os.path.dirname(inShp), get_filename(inShp),
            get_filename(inShp) + "_xxx"
        )
        """
        
        # Rename columns by selecting data from input
        outShp = sel_by_attr(inShp, "SELECT {} FROM {}".format(
            ", ".join(["{} AS {}".format(c, columns[c]) for c in columns]),
            get_filename(inShp)
        ) , output)
        
        # Delete tempfile
        #del_file(newFiles)
    
    else:
        raise ValueError("{} is not available".format(api))
    
    return outShp

