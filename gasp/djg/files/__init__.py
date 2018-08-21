"""
Deal with files
"""


def save_file(save_fld, _file):
    """
    Store a uploaded file in a given folder
    """ 
    
    import os
    
    with open(os.path.join(save_fld, _file.name), 'wb+') as destination:
        for chunk in _file.chunks():
            destination.write(chunk)

