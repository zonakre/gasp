"""
Working with fields tables
"""

import arcpy


def add_field(tbl, name, fld_type, length, precision=""):
    arcpy.AddField_management(
        tbl, name, fld_type, length, precision, "", "",
        "NULLABLE", "NON_REQUIRED", ""
    )


def del_field(tbl, drop_fields, table_format=None):
    """
    This tool deletes one or more fields from a table, feature
    class, feature layer, or raster dataset.
    
    Use table_format if tbl is a dir
    """
    
    import os
    
    from gasp import goToList
    
    try:
        if os.path.isdir(tbl):
            from gasp.oss import list_files
        
            tables = list_files(tbl, file_format=table_format)
        else:
            tables = [tbl]
    except:
        tables = [tbl]
    
    drop_fields = goToList(drop_fields)
    
    if not drop_fields:
        raise ValueError('drop_fields should be a string or a list of strings')
    
    for tbl in tables:
        arcpy.DeleteField_management(tbl, drop_fields)


def calc_fld(table, fld, expression, isNewField=None):
    """
    Field Calculator
    
    isNewField = {
        "TYPE" : "DOUBLE", "LENGTH" : "10", "PRECISION" : "3"
    }
    """
    
    if isNewField:
        add_field(
            table, fld, isNewField["TYPE"],
            isNewField["LENGTH"], isNewField["PRECISION"]
        )
    
    arcpy.CalculateField_management(
        table, fld, expression, "VB", ""
    )


def list_fields(tbl):
    """
    Return a list with the name of every field in a Feature Class
    """
    
    return [str(f.name) for f in arcpy.ListFields(tbl)]


def get_field_type_str(field_type):
    return "TEXT" if field_type == 'String' \
        else "SHORT" if field_type == 'Integer' else \
        "TEXT"


def type_fields(tbl, field=None):
    """
    Return a dict with the field name as value and the field type as
    value.
    
    If a field is given (string or list), return only the types for
    the columns in the field object.
    
    The field types could be:
    * All - All field types are returned. This is the default.
    * BLOB - Only field types of BLOB are returned.
    * Date - Only field types of Date are returned.
    * Double - Only field types of Double are returned.
    * Geometry - Only field types of Geometry are returned.
    * GlobalID - Only field types of GlobalID are returned.
    * GUID - Only field types of GUID are returned.
    * Integer - Only field types of Integer are returned.
    * OID - Only field types of OID are returned.
    * Raster - Only field types of Raster are returned.
    * Single - Only field types of Single are returned.
    * SmallInteger - Only field types of SmallInteger are returned.
    * String - Only field types of String are returned.
    """
    
    fields_type = {
        str(f.name) : str(f.type) for f in arcpy.ListFields(tbl)
    }
    
    if not field:
        return fields_type
    
    else:
        if type(field) == list:
            for fld in fields_type:
                if fld not in field:
                    del fields_type[fld]
            return fields_type
        
        elif type(field) == str or type(field) == unicode:
            return fields_type[field]


def get_fields_properties(tbl, fields=None):
    """
    Get fields Properties
    
    return a object like:
    d = {
        'NAME' : {'LENGTH': X, 'TYPE': 'type'}
    }
    """
    
    fields = [fields] if type(fields) == str or type(fields) == unicode \
        else fields if type(fields) == list else None
    
    if not fields:
        d = {
            str(f.name) : {
                'LENGTH' : f.length,
                'TYPE'   : f.type
            } for f in arcpy.ListFields(tbl)
        }
    
    else:
        d = {
            str(f.name) : {
                'LENGTH' : f.length,
                'TYPE'   : f.type
            } for f in arcpy.ListFields(tbl) if f in fields
        }
    
    return d
    

def copy_fields(srcLyr, destLyr):
    
    inFields = get_fields_properties(srcLyr)
    
    for field in inFields:
        if field == 'FID' or field == 'Shape':
            continue
        
        FIELD_TYPE = 'TEXT' if inFields[field]['TYPE'] == 'String' else \
            'INTEGER' if inFields[field]['TYPE'] == 'Integer' or \
            inFields[field]['TYPE'] == 'SmallInteger' else \
            'DOUBLE' if inFields[field]['TYPE'] == 'Double' else 'TEXT'
        
        add_field(
            destLyr, field,
            FIELD_TYPE,
            inFields[field]['LENGTH']
        )


"""
Table statistics and values
"""

def field_statistics(shp, fld, STATS):
    """
    SUM   - Adds the total value for the specified field.
    MEAN  - Calculates the average for the specified field.
    MIN   - Finds the smallest value for all records of the specified field. 
    MAX   - Finds the largest value for all records of the specified field.
    RANGE - Finds the range of values (MAX minus MIN) for the specified field. 
    STD   - Finds the standard deviation on values in the specified field.
    COUNT - Finds the number of values included in statistical calculations.
    This counts each value except null values. To determine the number of 
    null values in a field, use the COUNT statistic on the field in question, 
    and a COUNT statistic on a different field which does not contain nulls 
    (for example, the OID if present), then subtract the two values. 
    FIRST - Finds the first record in the Input Table and uses its specified
    field value.
    LAST  - Finds the last record in the Input Table and uses its specified
    field value.
    
    Return an array with the statistics
    Same order of STATS
    """
    
    STATS = [STATS] if type(STATS) != list else STATS
    
    c = arcpy.SearchCursor(shp)
    VAL = [float(l.getValue(fld)) for l in c]
    
    for i in range(len(STATS)):
        if STATS[i] == 'SUM':
            STATS[i] = sum(VAL)
        
        if STATS[i] == 'MIN':
            STATS[i] = min(VAL)
        
        if STATS[i] == 'MAX':
            STATS[i] = max(VAL)
        
        if STATS[i] == 'MEAN':
            STATS[i] = sum(VAL) / len(VAL)
    
    return STATS if len(STATS) > 1 else STATS[0]


def add_geom_attr(lyr, field_name, geom_attr="AREA"):
    """
    Add Geometry Attribute to table
    
    TODO: Now works only with Polygon and geom_attr=Area
    """
    
    arcpy.AddGeometryAttributes_management(lyr, geom_attr)
    
    add_field(lyr, field_name, "DOUBLE", "10", "3")
    calc_fld(lyr, field_name, "[POLY_AREA]")
    
    del_field(lyr, ["POLY_AREA"])


def distint_values_column(shp, field):
    """
    List all values in a column of a vectorial file
    """
    
    values = []
    cs = arcpy.SearchCursor(shp)
    for line in cs:
        if line.getValue(field) not in values:
            values.append(line.getValue(field))
    
    return values


def get_equal_int(shp, field, nr_cls, roundNr=1):
    """
    Return the equal intervals for a field of a feature class
    """
    
    import os
    from gasp.cpu.arcg.stats import summary
    
    arcpy.env.overwriteOutput = True
    
    # Get maximum and minimum
    stat_tbl = summary(
        shp, 
        os.path.splitext(shp)[0] + '_stat.dbf',
        [[field, 'MAX'], [field, 'MIN']]
    )
    
    cursor = arcpy.SearchCursor(stat_tbl)
    l = cursor.next()
    while l:
        __max = float(l.getValue('MAX_{}'.format(field[:6])))
        __min = l.getValue('MIN_{}'.format(field[:6]))
        l = cursor.next()
    
    int_break = (__max - __min) / float(nr_cls)
    
    breaks = [round(__min, roundNr)]
    for i in range(1, nr_cls + 1):
        breaks.append(round(breaks[i-1] + int_break, roundNr))
    
    return breaks

