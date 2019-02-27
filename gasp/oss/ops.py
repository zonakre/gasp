"""
Operations with py os

* Create, rename, manage, delete folders and files
"""

import os
import shutil
from gasp.web import get_file


def create_folder(folder, randName=None, overwrite=True):
    """
    Create a new folder
    Replace the given folder if that one exists
    """
    
    if randName:
        import random
        chars = '0123456789qwertyuiopasdfghjklzxcvbnm'
        
        name = ''
        for i in range(10):
            name+=random.choice(chars)
        
        folder = os.path.join(folder, name)
    
    if os.path.exists(folder):
        if overwrite:
            shutil.rmtree(folder)
        else:
            raise ValueError(
                "{} already exists".format(folder)
            )
    
    os.mkdir(folder)
    
    return folder


def del_folder(folder):
    """
    Delete folder if exists
    """
    
    if os.path.exists(folder) and os.path.isdir(folder):
        shutil.rmtree(folder)


def del_file(_file):
    """
    Delete files if exists
    """
    
    from gasp import goToList
    
    for ff in goToList(_file):
        if os.path.isfile(ff) and os.path.exists(ff):
            os.remove(ff)


def del_file_folder_tree(fld, file_format):
    """
    Delete all files with a certain format in a folder and sub-folders
    """
    
    if file_format[0] != '.':
        file_format = '.' + file_format
    
    for (dirname, sub_dir, filename) in os.walk(fld):
        for f in filename:
            if os.path.splitext(f)[1] == file_format:
                os.remove(os.path.join(dirname, f))


def del_files_by_name(folder, names):
    from .info import list_files
    lst_files = list_files(folder, filename=basenames)
    
    for f in lst_files:
        del_file(f)


def del_files_by_partname(folder, partname):
    """
    If one file in 'folder' has 'partname' in his name, it will be
    deleted
    """
    
    from .info import list_files
    
    files = list_files(folder)
    
    for _file in files:
        if partname in os.path.basename(_file):
            del_file(_file)


def rename_files_with_same_name(folder, oldName, newName):
    """
    Rename files in one folder with the same name
    """
    
    from gasp.oss import list_files, get_fileformat
    
    _Files = list_files(folder, filename=oldName)
    
    Renamed = []
    for f in _Files:
        newFile = os.path.join(folder, newName + get_fileformat(f))
        os.rename(f, newFile)
        
        Renamed.append(newFile)
    
    return Renamed


def onFolder_rename(fld, toBeReplaced, replacement, only_files=True,
                    only_folders=None):
    """
    List all files in a folder; see if the filename includes what is defined
    in the object 'toBeReplaced' and replace this part with what is in the
    object 'replacement'
    """
    
    from gasp.oss import list_files

    if not only_files and not only_folders:
        files = list_folders_files(fld)

    elif not only_files and only_folders:
        files = list_folders(fld)

    elif only_files and not only_folders:
        files = list_files(fld)

    for __file in files:
        if os.path.isfile(__file):
            filename = os.path.splitext(os.path.basename(__file))[0]
        else:
            filename = os.path.basename(__file)

        if toBeReplaced in filename:
            renamed = filename.replace(toBeReplaced, replacement)

            if os.path.isfile(__file):
                renamed = renamed + os.path.splitext(os.path.basename(__file))[1]

            os.rename(
                __file, os.path.join(os.path.dirname(__file), renamed)
            )


def onFolder_rename2(folder, newBegin, stripStr, fileFormats=None):
    """
    Erase some characters of file name and add something to the
    begining of the file
    """
    
    from gasp.oss import list_files
    from gasp.oss import get_filename
    from gasp.oss import get_fileformat
    
    files = list_files(folder, file_format=fileFormats)
    
    for _file in files:
        name = get_filename(_file, forceLower=True)
        
        new_name = name.replace(stripStr, '')
        new_name = "{}{}{}".format(newBegin, new_name, get_fileformat(_file))
        
        os.rename(_file, os.path.join(os.path.dirname(_file), new_name))


def copy_file(src, dest):
    """
    Copy a file
    """
    
    from shutil import copyfile
    
    copyfile(src, dest)
    
    return dest

