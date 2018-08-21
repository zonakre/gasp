"""
Tools for process geographic data on PostGIS
"""

from gasp.cpu.psql import connection


def near(link, first_tbl, second_tbl, dist, output, near_field='near'):
    """
    Near tool for PostGIS
    
    Parameters meaning:
    
    * link = dict with meta to connect to PostgreSQL
    
    * first_tbl = dict with meta of the table that will be store the minimum
    distance between the features of this table and the nearest feature of the
    second table. E.g. {table_name: {'pk': value, 'geom': value, 'fields': 
    list_value_with_other_interest_fields}}
    
    * second_tbl = dict with meta of the second table. Dict with the same 
    structure
    
    * dist = if a distance is greater than this variable, it will be stored on
    the output table having a dist value of -1.0
    
    * output = name of the output table
    
    * near_field = name of the field that will receive the nearest distance
    values
    
    Returns:
    result table name, pk, geom and near field
    """
    
    # Table names
    first_table = first_tbl.keys()[0]
    second_table = second_tbl.keys()[0]
    
    # Fields to select from the two tables
    try:
        first_fields = first_tbl[first_table]['fields']
    except:
        first_fields = []
    try:
        second_fields = second_tbl[second_table]['fields']
    except:
        second_fields = []
    
    # The SQL query depends on the number of fields on the previous lists
    if len(first_fields) == 0 and len(second_fields) == 0:
        sql_fields = "s.{pk_f}, s.{g_f}, h.{pk_s} AS sid".format(
            pk_f = first_tbl[first_table]['pk'],
            g_f  = first_tbl[first_table]['geom'],
            pk_s = second_tbl[second_table]['pk'],
            g_s  = second_tbl[second_table]['geom'],
        )
    elif len(first_fields) != 0 and len(second_fields) == 0:
        sql_fields = "s.{pk_f}, s.{g_f}, {flds}, h.{pk_s} AS sid".format(
            pk_f = first_tbl[first_table]['pk'],
            g_f  = first_tbl[first_table]['geom'],
            pk_s = second_tbl[second_table]['pk'],
            g_s  = second_tbl[second_table]['geom'],
            flds = ", ".join(['s.{f}'.format(f=x) for x in first_fields])
        )
    elif len(first_fields) == 0 and len(second_fields) != 0:
        sql_fields = "s.{pk_f}, s.{g_f}, {flds}, h.{pk_s} AS sid".format(
            pk_f = first_tbl[first_table]['pk'],
            g_f  = first_tbl[first_table]['geom'],
            pk_s = second_tbl[second_table]['pk'],
            g_s  = second_tbl[second_table]['geom'],
            flds = ", ".join(['h.{f}'.format(f=x) for x in second_fields])            
        )
    elif len(first_fields) != 0 and len(second_fields) != 0:
        sql_fields = "s.{pk_f}, s.{g_f}, {fflds}, {sflds}, h.{pk_s} AS sid".format(
            pk_f  = first_tbl[first_table]['pk'],
            g_f   = first_tbl[first_table]['geom'],
            pk_s  = second_tbl[second_table]['pk'],
            g_s   = second_tbl[second_table]['geom'],
            fflds = ", ".join(['s.{f}'.format(f=x) for x in first_fields]),
            sflds = ", ".join(['h.{f}'.format(f=x) for x in second_fields])            
        )
    
    # Connect to PostgreSQL
    c = connection(link)
    
    cursor = c.cursor()
    
    cursor.execute((
        "CREATE TABLE {out} AS "
        "SELECT DISTINCT ON (s.{pk_f}) "
        "{fld_sel}, "
        "ST_Distance("
            "s.{g_f}, h.{g_s}"
        ") AS {near} FROM {frst} s LEFT JOIN {scnd} h ON "
        "ST_DWithin(s.{g_f}, h.{g_s}, {d}) ORDER BY s.{pk_f}, "
        "ST_Distance(s.{g_f}, s.{g_s});"
    ).format(
        out=output,
        pk_f=first_tbl[first_table]['pk'],
        pk_s=second_tbl[second_table]['pk'],
        g_f=first_tbl[first_table]['geom'],
        g_s=second_tbl[second_table]['geom'],
        frst=first_table,
        scnd=second_table,
        d=dist, near=near_field,
        fld_sel=sql_fields
    ))
    
    cursor.execute(
        "ALTER TABLE {tbl} ADD CONSTRAINT {tbl}_pk PRIMARY KEY ({fld});".format(
            tbl=output, fld=first_tbl[first_table]['pk']
        )
    )
    cursor.execute(
        "UPDATE {tbl} SET near=-1.0 WHERE near IS NULL;".format(
            tbl=output
        )
    )
    
    c.commit()
    cursor.close()
    c.close()
    
    return [output, first_tbl[first_table]['pk'],
            first_tbl[first_table]['geom'], near_field]

