"""
XLS To Something Data Structure
"""

import pandas

def xls_to_df(table_file, sheet=None, useFirstColAsIndex=None):
    """
    XLS to Pandas Dataframe
    """
    
    sheet = 0 if sheet == None else sheet
    
    indexCol = 0 if useFirstColAsIndex else None
    
    d = pandas.read_excel(
        table_file, sheet, index_col=indexCol,
        encoding='utf-8', dtype='object'
    )
    
    return d


def xls_to_dict(table_file, sheet=None, dictValueAsList=None):
    """
    XLS File to a Python Dict
    
          | col_1 | col_2 | ... | col_n
    row_1 | XXXXX | XXXXX | ... | XXXXX
    row_2 | XXXXX | XXXXX | ... | XXXXX
      ... | XXXXX | XXXXX | ... | XXXXX
    row_n | XXXXX | XXXXX | ... | XXXXX
    
    dict = {
        row_1 : {
            col_1 : XXXXX,
            col_2 : XXXXX,
            ...
            col_n : XXXXX
        },
        row_2 : {
            col_1 : XXXXX,
            col_2 : XXXXX,
            ...
            col_n : XXXXX
        },
        ...,
        row_n : {
            col_1 : XXXXX,
            col_2 : XXXXX,
            ...
            col_n : XXXXX
        }
    }
    
    OR
     col_1| col_2 | col_3 | ... | col_n
    V_0:0 | V_0:1 | V_0:2 | ... | V_0:N
    V_1:0 | V_1:1 | V_1:2 | ... | V_1:N
    V_2:0 | V_2:1 | V_2:2 | ... | V_2:N
     ...  |  ...  |  ...  | ... |  ...
    V_N:0 | V_N:1 | V_N:2 | ... | V_N:N
    
    dict = {
        V_0:0 : [V_0:1, V_0:2, ..., V_0:N],
        V_1:0 : [V_1:1, V_1:2, ..., V_1:N],
        V_2:0 : [V_2:1, V_2:2, ..., V_2:N],
        ...
        V_N:0 : [V_N:1, V_N:2, ..., V_N:N]
    }
    """
    
    from gasp.to.obj import df_to_dict
    
    table = xls_to_df(table_file, sheet=sheet, useFirstColAsIndex=True)
    
    return df_to_dict(table,
        colsIsIndex=None, valueIsList=dictValueAsList
    )


def xlstimedelta_to_pddf(inXls, timecol, sheet_name=None, sheet_index=None,
                         columnsToMantain=None):
    """
    Convert a table with a column with timedelta values to a valid 
    Pandas DataFrame
    """
    
    import datetime
    import xlrd
    from xlrd           import xldate_as_tuple
    from gasp           import goToList
    from gasp.xls.sheet import get_sheet_obj
    from gasp.xls.fld   import columns_by_order
    from gasp.xls.fld   import get_columns_position
    
    __xls = xlrd.open_workbook(inXls)
    sheet = get_sheet_obj(__xls, name=sheet_name, index=sheet_index)
    
    # Get Cols name
    COLS_NAME = columns_by_order(sheet) if not columnsToMantain else \
        goToList(columnsToMantain)
    
    if type(timecol) != int:
        if timecol not in COLS_NAME:
            COLS_NAME.append(timecol)
    
    # Get Cols position
    COLS_POS = get_columns_position(sheet, COLS_NAME)
    POS_COLS = COLS_POS.values()
    
    if type(timecol) == int:
        COL_TIME_POSITION = timecol
    else:
        COL_TIME_POSITION = COLS_POS[timecol]
    
    data = []
    for row in range(1, sheet.nrows):
        l_col = []
        for col in range(sheet.ncols):
            if col not in POS_COLS:
                continue
            
            if col == COL_TIME_POSITION:
                tt = xldate_as_tuple(
                    sheet.cell(row, col).value, __xls.datemode)
                
                l_col.append(datetime.timedelta(
                    weeks=tt[1], days=tt[2], hours=tt[3],
                    minutes=tt[4], seconds=tt[5]
                ))
            
            else:
                l_col.append(sheet.cell(row, col).value)
        
        data.append(l_col)
    
    df = pandas.DataFrame(data, columns=COLS_NAME)
    
    return df


def xls_to_dict_ktuple(xls, sheet_name=None, sheet_index=None):
    """
    XLS File to a Python Dict
    
                      | col_1 | col_2 | ... | col_n
    row_1.0 | row_1.1 | XXXXX | XXXXX | ... | XXXXX
    row_2.0 | row_2.1 | XXXXX | XXXXX | ... | XXXXX
      ...   |  ...    | XXXXX | XXXXX | ... | XXXXX
    row_n.0 | row_n.1 | XXXXX | XXXXX | ... | XXXXX
    
    dict = {
        (row_1.0, row_1.1) : {
            col_1 : XXXX,
            col_2 : XXXX,
            ...
            col_n : XXXX
        },
        (row_2.0, row_2.0) : {
            col_1 : XXXX,
            col_2 : XXXX,
            ...
            col_n : XXXX
        },
        ...,
        (row_n.0, row_n.1) : {
            col_1 : XXXX,
            col_2 : XXXX,
            ...
            col_n : XXXX
        }
    }
    """
    
    import xlrd
    from gasp.xls.sheet import get_sheet_obj
    
    __xls = xlrd = open_workbook(xls)
    
    sheet = get_sheet_obj(__xls, sheet_name, sheet_index)
    
    cname = {
        (sheet.cell(i,0).value, sheet.cell(i, 1).value) : {
            sheet.cell(0, e).value : sheet.cell(i, e).value for e in range(
                2, sheet.ncols)
        } for i in range(1, sheet.nrows)
    }
    
    __xls.release_resources()
    
    return cname


def xls_to_array(xls, sheet):
    """
    XLS File to a Python Dict
    
    col_1 | col_2 | col_3 | ... | col_N
    V_0:0 | V_0:1 | V_0:2 | ... | V_0:N
    V_1:0 | V_1:1 | V_1:2 | ... | V_1:N
    V_2:0 | V_2:1 | V_2:2 | ... | V_2:N
     ...  |  ...  |  ...  | ... |  ...
    V_N:0 | V_N:1 | V_N:2 | ... | V_N:N
    
    list = [
        {col_1 : V_0:0, col_2 : V_0:1, col_3 : V_0:2, ..., col_N : V_0:N},
        {col_1 : V_1:0, col_2 : V_1:1, col_3 : V_1:2, ..., col_N : V_1:N},
        {col_1 : V_2:0, col_2 : V_2:1, col_3 : V_2:2, ..., col_N : V_2:N},
        ...,
        {col_1 : V_N:0, col_2 : V_N:1, col_3 : V_N:2, ..., col_N : V_N:N},
    ]
    """
    
    from gasp.to.obj import df_to_list
    
    table = xls_to_df(
        xls, sheet=sheet, useFirstColAsIndex=None
    )
    
    return df_to_list(table)


def ods_to_df(odsFile, sheet):
    """
    ODS file to Pandas Dataframe
    """
    
    import json
    import pandas
    from pyexcel_ods import get_data
    
    data = get_data(odsFile)[sheet]
    
    return pandas.DataFrame(data[1:], columns=data[0])


def get_unit_attributes(sheet_obj, entities_pos, fields):
    """
    Return a dict as:
    d = {
        entitie_1: {field1: value, field2: value, ...},
        entitie_2: {field1: value, field2: value, ...},
        ...
        entitie_n: {field1: value, field2: value, ...},
    }
    """
    
    unit_attributes = {}
    for line in range(1, sheet_obj.nrows):
        entitie_id = sheet_obj.cell(line, entities_pos).value
        if entitie_id not in unit_attributes.keys():
            attributes = {}
            for field in fields:
                attributes[field] = sheet_obj.cell(line, fields[field]).value
            unit_attributes[entitie_id] = attributes
    
    if u'' in unit_attributes.keys():
        del unit_attributes[u'']
    
    if '' in unit_attributes.keys():
        del unit_attributes['']    
    
    return unit_attributes


"""
Deal with SpreadSheets with time values
"""

def duration_by_entity_and_pairs(inXls, sheet_name=None, sheet_index=None):
    """
    Table:
    
    ENTITY | ORIGIN | DESTINATION | DURATION
       12E  |  801   |     817     | 00:02:30
       12E  |  817   |    13824    | 00:02:15
       12E  | 13824  |    13822    | 00:01:18
       12E  | 13822  |    13809    | 00:03:06
       15E  |  917   |    5515     | 00:04:56
       15E  | 5515   |    3822     | 00:02:51
       15E  | 3822   |    3802     | 00:02:30
       15E  | 3802   |    7102     | 00:01:12
    
    To:
    dict = {
        12E : {
            (801, 817)     : 00:02:30,
            (817, 13824)   : 00:02:15,
            (13824, 13822) : 00:01:18,
            (13822, 13809) : 00:03:06
        },
        15E : {
            (917, 5515)  : 00:04:56,
            (5515, 3822) : 00:02:51,
            (3822, 3802) : 00:02:30,
            (3802, 7102) : 00:01:12
        }
    }
    """
    
    import xlrd
    import datetime
    from xlrd import xldate_as_tuple
    
    __xls = xlrd.open_workbook(inXls)
    sheet = get_sheet_obj(__xls, name=sheet_name, index=sheet_index)
    
    d = {}
    for row in range(1, sheet.nrows):
        ENTITY     = sheet.cell(row, 0).value
        PAIR_A     = sheet.cell(row, 1).value
        PAIR_B     = sheet.cell(row, 2).value
        TIME_TUPLE = xldate_as_tuple(sheet.cell(row, 3).value, __xls.datemode)
        
        VAL_AS_TIMEDELTA = datetime.timedelta(
            weeks=TIME_TUPLE[1], days=TIME_TUPLE[2], hours=TIME_TUPLE[3],
            minutes=TIME_TUPLE[4], seconds=TIME_TUPLE[5]
        )
        
        if ENTITY not in d:
            d[ENTITY] = {(PAIR_A, PAIR_B) : VAL_AS_TIMEDELTA}
        else:
            d[ENTITY][(PAIR_A, PAIR_B)] = VAL_AS_TIMEDELTA
    
    return d

