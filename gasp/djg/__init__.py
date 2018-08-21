"""
API's subpackage:

Tools for assist Django
"""


def open_Django_Proj(path_to_proj):
    """
    To run methods related with django objects, we
    need to make our python recognize the Django Project
    """
    
    import os, sys
    
    # This is so Django knows where to find stuff.
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "{}.settings".format(os.path.basename(path_to_proj))
    )
    
    sys.path.append(path_to_proj)
    
    # This is so my local_settings.py gets loaded.
    os.chdir(path_to_proj)
    
    # This is so models get loaded.
    from django.core.wsgi import get_wsgi_application
    
    return get_wsgi_application()


def list_djg_apps(path_to_django_proj):
    """
    List Django App's avaiable in a Django Project
    """
    
    import os
    
    from gasp.oss import list_folders_subfiles
    
    # Get project name
    projectName = os.path.basename(path_to_django_proj)
    
    # List folders and files in the folders
    projFolders = list_folders_subfiles(
        path_to_django_proj, files_format='.py',
        only_filename=True
    )
    
    apps = []
    # Check if the folder is a app
    for folder in projFolders:
        if os.path.basename(folder) == projectName:
            continue
        
        if '__init__.py' in projFolders[folder] or \
           'apps.py' in projFolders[folder]:
            apps.append(os.path.basename(folder))
    
    return apps

