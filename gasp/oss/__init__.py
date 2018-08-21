"""
Methods to interact with the Operating System
"""

import os

def os_name():
    import platform
    return str(platform.system())

def get_filename(__file, forceLower=None):
    """
    Return filename without file format
    """
    
    filename = os.path.splitext(os.path.basename(__file))[0]
    
    if forceLower:
        filename = filename.lower()
    
    return filename

def get_fileformat(__file):
    """
    Return file format
    """
    
    return os.path.splitext(__file)[1]


def get_filesize(path, unit='MB'):
    """
    Return file size in some menory unit
    """
    
    memory = os.path.getsize(path)
    
    if unit == 'MB':
        memory = (memory / 1024.0) /1024
    
    elif unit == 'KB':
        memory = memory / 1024.0
    
    else:
        memory = memory
    
    return memory

def list_files(w, file_format=None, filename=None):
    """
    List the abs path of all files with a specific extension on a folder
    """
    
    # Prepare file format list
    if file_format:
        from gasp import goToList
        
        formats = goToList(file_format)
        
        for f in range(len(formats)):
            if formats[f][0] != '.':
                formats[f] = '.' + formats[f]
    
    # List files
    r = []
    for (d, _d_, f) in os.walk(w):
        r.extend(f)
        break
    
    # Filter files by format or not
    if not file_format:
        t = [os.path.join(w, i) for i in r]
    
    else:
        t = [
            os.path.join(w, i) for i in r
            if os.path.splitext(os.path.basename(i))[1] in formats
        ]
    
    # Filter by filename
    if not filename:
        return t
    
    else:
        filename = [filename] if type(filename) == str or \
            type(filename) == unicode else filename
        
        _t = []
        for i in t:
            if os.path.splitext(os.path.basename(i))[0] in filename:
                _t.append(i)
        
        return _t


def list_folders(w, name=None):
    """
    List folders path or name in one folder
    """
    
    foldersname = []
    for (dirname, dirsname, filename) in os.walk(w):
        foldersname.extend(dirsname)
        break
    
    if name:
        return foldersname
    
    else:
        return [os.path.join(w, fld) for fld in foldersname]


def list_folders_files(w, name=None):
    """
    List folders and files path or name
    """
    
    fld_file = []
    for (dirname, dirsname, filename) in os.walk(w):
        fld_file.extend(dirsname)
        fld_file.extend(filename)
        break
    
    if name:
        return fld_file
    
    else:
        return [os.path.join(w, f) for f in fld_file]


def list_folders_subfiles(path, files_format=None,
                          only_filename=None):
    """
    List folders in path and the files inside each folder
    """
    
    folders_in_path = list_folders(path)
    
    out = {}
    for folder in folders_in_path:
        out[folder] = list_files(
            folder, file_format=files_format
        )
        
        if only_filename:
            for i in range(len(out[folder])):
                out[folder][i] = os.path.basename(out[folder][i])
    
    return out

