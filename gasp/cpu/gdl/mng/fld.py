"""
Fields relate
"""

from osgeo        import ogr
from gasp.prop.ff import drv_name

def map_fldCode_fldName(code=None, name=None):
    """
    Return the Field Type Name or the Field Type Code for a given
    code or name
    """
    
    mapObj = {
        2  : 'Real',
        4  : 'String',
        12 : 'Integer64'
    }
    
    if code and not name:
        if code in mapObj:
            return mapObj[code]
        else:
            raise ValueError('Code not referenced')
    
    elif not code and name:
        if name in mapObj.values():
            for __code in mapObj:
                if str(name) == mapObj[__code]:
                    return __code
        
        else:
            raise ValueError('Name not referenced')
    
    elif not code and not name:
        return mapObj


def map_pyType_fldCode(pyObj):
    """
    Return the code of the field type necessary to store that type of 
    python objects
    """
    
    if type(pyObj) == float:
        return 2
    elif type(pyObj) == int:
        return 12
    elif type(pyObj) == long:
        return 12
    elif type(pyObj) == str:
        return 4
    elif type(pyObj) == unicode:
        return 4
    else:
        raise ValueError((
            "Type of the given pyObj hasn't correspondence to a field code"
        ))


def pandas_map_ogrType(type_):
    __types = {
        'int32'   : ogr.OFTInteger,
        'int64'   : ogr.OFTInteger,
        'float32' : ogr.OFTReal,
        'float64' : ogr.OFTReal,
        'object'  : ogr.OFTString
    }
    
    return __types[type_]


def lst_fld(shp):
    """
    Return a list with every field name in a vectorial layer
    """
    
    if type(shp) == ogr.Layer:
        lyr = shp
        c=0
    
    else:
        data = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0)
    
        lyr = data.GetLayer()
        c= 1
    
    defn = lyr.GetLayerDefn()
    
    fields = []
    for i in range(0, defn.GetFieldCount()):
        fdefn = defn.GetFieldDefn(i)
        fields.append(fdefn.name)
    
    if c:
        del lyr
        data.Destroy()
    
    return fields


def ogr_list_fields_defn(shp):
    """
    Return a dict with the field name as key and the field definition as value
    
    Field defn is the same of saying name + type
    """
    
    if type(shp) == ogr.Layer:
        lyr = shp
        c   = 0
    
    else:
        data = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0) 
        lyr = data.GetLayer()
        c   = 1
    
    defn = lyr.GetLayerDefn()
    
    fields = {}
    for i in range(0, defn.GetFieldCount()):
        fdefn = defn.GetFieldDefn(i)
        fieldType = fdefn.GetFieldTypeName(fdefn.GetType())
        
        fields[fdefn.name] = {fdefn.GetType(): fieldType}
    
    if c:
        del lyr
        data.Destroy()
    
    return fields


def ogrFieldsDefn_from_pandasdf(df):
    """
    Return OGR Field Defn for every column in Pandas DataFrame
    """
    
    typeCols = dict(df.dtypes)
    
    return {col : pandas_map_ogrType(
        str(typeCols[col])) for col in typeCols}


def ogr_copy_fields(inLyr, outLyr, __filter=None):
    
    if __filter:
        __filter = [__filter] if type(__filter) != list else __filter
    
    inDefn = inLyr.GetLayerDefn()
    
    for i in range(0, inDefn.GetFieldCount()):
        fDefn = inDefn.GetFieldDefn(i)
        
        if __filter:
            if fDefn.name in __filter:
                outLyr.CreateField(fDefn)
            
            else:
                continue
        
        else:
            outLyr.CreateField(fDefn)
    
    del inDefn, fDefn


def add_fields(table, fields):
    """
    Receive a feature class and a dict with the field name and type
    and add the fields in the feature class
    
    TODO: Check if fields is a dict
    """
    
    import os
    
    if type(table) == ogr.Layer:
        lyr = table
        c = 0
    
    else:
        if os.path.exists(table) and os.path.isfile(table):
            # Open table in edition mode
            __table = ogr.GetDriverByName(
                drv_name(table)).Open(table, 1)
            
            # Get Layer
            lyr = __table.GetLayer()
            c=1 
        
        else:
            raise ValueError('File path does not exist')
    
    for fld in fields:
        lyr.CreateField(ogr.FieldDefn(fld, fields[fld]))
    
    if c:
        del lyr
        __table.Destroy()
    else:
        return lyr


def add_fields_to_tables(inFolder, fields, tbl_format='.shp'):
    """
    Add fields to several tables in a folder
    """
    
    from gasp.oss import list_files
    
    tables = list_files(inFolder, file_format=tbl_format)
    
    for table in tables:
        add_fields(table, fields)


def add_fields_sqldialect(table, fields):
    """
    Add fields to table using SQL dialect
    """
    
    import os
    from gasp import exec_cmd
    
    tbl_name = os.path.splitext(os.path.basename(table))[0]
    
    if type(fields) != dict:
        raise ValueError('Fields argument should be a dict')
    
    ogrinfo = 'ogrinfo {i} -sql "{s}"'
    
    for fld in fields:
        sql = 'ALTER TABLE {tableName} ADD COLUMN {col} {_type};'.format(
            tableName = tbl_name, col=fld, _type=fields[fld]
        )
        
        outcmd = exec_cmd(ogrinfo.format(
            i=table, s=sql
        ))


def summarize_table_fields(table, outFld, fld_name_fld_name=None,
                          __upper=False):
    """
    Summarize all fields in a table
    """
    
    from gasp         import exec_cmd
    from gasp.oss.ops import create_folder
    
    # List table fields:
    fields = lst_fld(table)
    
    # For each field, query data to summarize the values in the field
    cmd = 'ogr2ogr {o} {i} -dialect sqlite -sql "{s};"'
    
    if not os.path.exists(outFld):
        tmp = create_folder(outFld)
    
    for field in fields:
        outTbl = os.path.join(outFld, '{}.dbf'.format(field))
        
        outcmd = exec_cmd(cmd.format(
            i=table, o=outTbl,
            s='SELECT {f_}{f} FROM {t} GROUP BY {f}'.format(
                f=field,
                t=os.path.splitext(os.path.basename(table))[0],
                f_='' if not fld_name_fld_name else '{}, '.format(
                    fld_name_fld_name
                )
            )
        ))

def update_table(table, new_values, ref_values=None):
    """
    Update a feature class table with new values
    
    Where with OR condition
    new_values and ref_values are dict with fields as keys and values as 
    keys values.
    """
    
    from gasp import exec_cmd
    
    if ref_values:
        update_query = 'UPDATE {tbl} SET {pair_new} WHERE {pair_ref};'.format(
            tbl=os.path.splitext(os.path.basename(table))[0],
            pair_new=','.join(["{fld}={v}".format(
                fld=x, v=new_values[x]) for x in new_values]),
            pair_ref=' OR '.join(["{fld}='{v}'".format(
                fld=x, v=ref_values[x]) for x in ref_values])
        )
    
    else:
        update_query = 'UPDATE {tbl} SET {pair};'.format(
            tbl=os.path.splitext(os.path.basename(table))[0],
            pair=','.join(["{fld}={v}".format(
                fld=x, v=new_values[x]) for x in new_values])
        )
    
    ogrinfo = 'ogrinfo {i} -dialect sqlite -sql "{s}"'.format(
        i=table, s=update_query
    )
    
    # Run command
    outcmd = exec_cmd(ogrinfo)

def add_filename_to_field(tables, new_field, table_format='.dbf'):
    """
    Update a table with the filename in a new field
    """
    
    from gasp.oss import list_files
    
    if os.path.isdir(tables):
        __tables = list_files(tables, file_format=table_format)
    
    else:
        __tables = [tables]
    
    for table in __tables:
        add_fields(table, {new_field: 'varchar(50)'})
        
        name_tbl = os.path.splitext(os.path.basename(table))[0]
        name_tbl = name_tbl.lower() if name_tbl.isupper() else name_tbl
        update_table(
            table,
            {new_field: name_tbl}
        )


def add_geomattr_to_sqldbTbl(sqdb, table, geom_attr, newTblName, newColName):
    """
    Use ogr2ogr to add geometry attributes to table
    """
    
    from gasp import exec_cmd
    
    cmd = (
        "ogr2ogr -update -append -f \"SQLite\" {db} -nln \"{nt}\" "
        "-dialect sqlite -sql \"SELECT *, {geomProp}(geometry) "
        "AS {newCol} FROM {tbl}\" {db}"
    ).format(
        db=sqdb, nt=newTblName, geomProp=geom_attr,
        newCol=newColName, tbl=table
    )
    
    rcmd = exec_cmd(cmd)
    
    return newTblName

