"""
Tools for Django Models management
"""


def get_special_tables():
    return {
        'auth_user'        : 'django.contrib.auth.models.User',
        'auth_group'       : 'django.contrib.auth.models.Group',
        'auth_user_groups' : ''
    }


def get_ignore_tables():
    return [
        'django_Permission',
        'django_Group',
        'django_LogEntry'
    ]


def list_fieldsName(model_obj):
    """
    List fields in Model
    """
    
    fields = model_obj._meta.get_fields()
    
    fld_name = [fld.name for fld in fields]
    
    return fld_name


def get_fieldsTypes(model_obj):
    """
    get type of the lifes in on django model
    """
    
    fields = model_obj._meta.get_fields()
    
    flds = {}
    for field in fields:
        t = field.get_internal_type()
        
        if t == 'AutoField' or t == 'IntegerField' or \
            t == 'BigAutoField' or t == 'BigIntegerField':
            flds[field.name] = int
        
        elif t == 'CharField':
            flds[field.name] = str
        
        elif t == 'BooleanField' or t == 'ForeignKey' or \
            t == 'PolygonField' or t == 'DateField':
            continue
        else:
            continue
    
    return flds


def isForeign_key_in_model(modelName=None, appName=None, exportAllFields=None,
                           specialModel=None):
    """
    There is any foreign key in one model
    """
    
    from django.contrib.gis.db import models
    from gasp import __import
    
    # List fields in model
    if modelName and appName and specialModel:
        raise ValueError(
            'Please define modelName/AppName or only specialModel'
        )
    
    if modelName and appName:
        modelObj = __import('{}.models.{}'.format(appName, modelName))
    
    elif specialModel:
        modelObj = __import(get_special_tables()[specialModel])
    
    else:
        raise ValueError((
            'Nothing to do... '
            'Please define modelName/AppName or only specialModel'
        ))
    
    fields = list_fieldsName(modelObj)
    
    # Check if the field is a foreign key
    fk_fields = []
    for field in fields:
        fieldObj = modelObj._meta.get_field(field)
        if isinstance(fieldObj, models.ForeignKey):
            fk_fields.append(field)
    
    return fk_fields if not exportAllFields else \
           (fk_fields, fields)


def list_tables_without_foreignk(tables, proj_path=None):
    """
    List tables without foreign keys
    """
    
    import os
    
    if proj_path:
        from gasp.djg import open_Django_Proj
        
        application = open_Django_Proj(proj_path)
    
    result = []
    for table in tables:
        # Get model object
        
        if table in get_special_tables():
            # Special table
            fk_fields = isForeign_key_in_model(specialModel=table)
        else:
            tname = os.path.splitext(os.path.basename(table))[0] \
                if os.path.isfile(table) else table
            
            appName = tname.split('_')[0]
            modName = '_'.join(tname.split('_')[1:])
            
            fk_fields = isForeign_key_in_model(modName, appName)
        
        if fk_fields:
            continue
        else:
            result.append(table)
    
    return result


def update_model(model, data):
    """
    Update Model Data
    """
    
    from gasp import __import
    
    djangoCls = __import(model)
    __model = djangoCls()
    
    for row in data:
        for k in row:
            setattr(__model, k, row[k])
        __model.save()


"""
*******************************************************************************
******************************* EXPERIENCES ***********************************
*******************************************************************************
"""
def create_model(name, fields=None, app_label='', module='',
                 options=None, admin_opts=None):
    """
    Create a Django model dynamicaly

    Source: https://code.djangoproject.com/wiki/DynamicModels

    Parameters:
    name - The name of the model to be created
    fields - A dictionary of fields the model will have
    (managers and methods would go in this dictionary as well)
    app_label - A custom application label for the model
    module - An arbitrary module name to use as the model's source
    options - A dictionary of options, as if they were provided to the
    inner Meta class
    admin_opts - A dictionary of admin options, as if they were provided 
    to the Admin class

    TODO: It is needed to find a way to send this model to the database
    """

    from django.contrib.gis.db import models

    class Meta:
        # Using type('Meta', ...) gives a dictproxy error during model creation
        pass

    if app_label:
        # app_label must be set using the Meta inner class
        setattr(Meta, 'app_label', app_label)

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, (models.Model,), attrs)

    # Create an Admin class if admin options were provided
    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model
"""
*******************************************************************************
"""
