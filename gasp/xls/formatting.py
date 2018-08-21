""" Formatting tools """

def check_if_cell_is_bold(xls_obj, cell_obj):
    """
    Return if a cell is bold or not
    """
    
    fmt = xls_obj.xf_list[cell_obj.xf_index]
    
    isBold = fmt._font_flag
    
    return True if isBold else None

