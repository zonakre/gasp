"""
Write data into PostgreSQL database
"""

def df_to_pgsql(conParam, df, pgtable, append=None):
    """
    Pandas Dataframe to PGSQL table
    """
    
    from gasp.cpu.psql import alchemy_engine
    
    pgengine = alchemy_engine(conParam)
    
    df.to_sql(
        pgtable, pgengine,
        if_exists='replace' if not append else 'append',
        index=False
    )
    
    return pgtable


def geodf_to_pgsql(conParam, df, pgtable, epsg, geomType,
                   colGeom="geometry"):
    """
    Pandas GeoDataframe to PGSQL table
    """
    
    from geoalchemy2    import Geometry, WKTElement
    from gasp.cpu.psql import alchemy_engine
    
    pgengine = alchemy_engine(conParam)
    
    df["geom"] = df[colGeom].apply(
        lambda x: WKTElement(x.wkt, srid=epsg)
    )
    
    if colGeom != 'geom':
        df.drop(colGeom, axis=1, inplace=True)
    
    df.to_sql(
        pgtable, pgengine, if_exists='replace', index=False,
        dtype={'geom' : Geometry(geomType, srid=epsg)}
    )
    
    return pgtable


def apnd_geodf_in_pgtbl(conpg, df, tbl, epsg, geomType,
                        colGeom="geometry"):
    """
    Append Pandas GeoDataframe into PGSQL Table
    """
    
    from geoalchemy2   import Geometry, WKTElement
    from gasp.cpu.psql import alchemy_engine
    
    pgengine = alchemy_engine(conpg)
    
    df["geom"] = df[colGeom].apply(
        lambda x: WKTElement(x.wkt, srid=epsg)
    )
    
    if colGeom != 'geom':
        df.drop(colGeom, axis=1, inplace=True)
    
    df.to_sql(
        tbl, pgengine, if_exists='append', index=False,
        dtype={'geom' : Geometry(geomType, srid=epsg)}
    )
    
    return tbl


def insert_query(dic_pgsql, query, execute_many_data=None):
    """
    Insert data into a PGSQL Table
    """
    
    from gasp.cpu.psql   import connection
    from psycopg2.extras import execute_values
    
    con = connection(dic_pgsql)
    
    cursor = con.cursor()
    if execute_many_data:
        execute_values(cursor, query, execute_many_data)
    
    else:
        cursor.execute(query)
    
    con.commit()
    cursor.close()
    con.close()


def txt_to_pgsql(csv, pg_table, delimiter, encoding_='utf-8', dic_con={
        'HOST': 'localhost', 'PASSWORD': 'admin',
        'USER': 'postgres', 'DATABASE': 'shogun_db', 'PORT': '5432'
    }):
    """
    Method to insert tables writen in a text file into pgsql table
    """

    import codecs

    def sanitize_value(v):
        return None if v=='None' or v=='' else v

    with codecs.open(csv, 'r', encoding=encoding_) as f:
        c = 0
        data = []

        for l in f:
            cols = l.replace('\r', '').strip('\n').split(delimiter)
            if not c:
                cols_name = ['%s' % cl for cl in cols]
                c += 1
            else:
                data.append([sanitize_value(v) for v in cols])

    sql_query = '''INSERT INTO {tbl} ({col}) VALUES %s'''.format(
        tbl=pg_table, col=', '.join(cols_name)
    )

    con = insert_query(
        dic_con, sql_query, execute_many_data=data)


def txts_to_pgsql(folder, delimiter, __encoding='utf-8', conPSQL={
        'HOST' : 'localhost', 'PASSWORD' : 'admin',
        'USER' : 'postgres' , 'DATABASE' : 'matuc_db', 'PORT': '5432'
    }):
    """
    Executes txt_to_pgsql for every file in a given folder
    
    The file name should be the table name
    """
    
    import os
    from gasp.oss import list_files
    
    __files = list_files(folder, file_format=['.txt', '.csv', '.tsv'])
    
    for __file in __files:
        txt_to_pgsql(
            __file,
            pg_table,
            delimiter, encoding_=__encoding,
            dic_con=conPSQL
        )

def txts_to_pgsql_newdb(folder, delimiter, newdb, conPSQL={
        'HOST' : 'localhost', 'PASSWORD' : 'admin',
        'USER' : 'postgres' , 'PORT': '5432'
    }, rewrite=True):
    """
    Create a new db and put there all text files in a folder
    
    The file name should be the table name
    """
    
    import os
    from gasp.oss              import list_files
    from gasp.fm.txt           import txt_to_df
    from gasp.cpu.psql.mng     import create_db
    from gasp.cpu.psql.mng.fld import pgtypes_from_pandasdf
    from gasp.cpu.psql.mng     import create_tbl
    
    # Create database
    create_db(conPSQL, newdb, overwrite=rewrite)
    conPSQL["DATABASE"] = newdb
    
    # List text files
    txts = list_files(folder, file_format=['.txt', '.csv', '.tsv'])
    
    # List tables data
    table_data = {
        os.path.splitext(os.path.basename(txt))[0] : txt_to_df(
            txt, delimiter) for txt in txts
    }
    
    # Create Tables
    dicColsT = {}
    for table in table_data:
        cols = list(table_data[table].columns)
        
        colsT = pgtypes_from_pandasdf(table_data[table])
        dicColsT[table] = colsT
        create_tbl(conPSQL, table, colsT, orderFields=cols)
    
    # Insert data into tables
    for table in table_data:
        print table
        cols = list(table_data[table].columns)
        print cols
        
        tableDf = table_data[table]
        for i in range(len(cols)):
            if not i:
                if dicColsT[table][cols[i]] == "text":
                    tableDf["row"] = u"('" + tableDf[cols[i]].astype(unicode) + \
                        u"'"
                else:  
                    tableDf["row"] = u"(" + tableDf[cols[i]].astype(unicode)
            
            else:
                if dicColsT[table][cols[i]] == "text":
                    tableDf["row"] = tableDf["row"] + u", '" + \
                        tableDf[cols[i]].astype(unicode) + u"'"
                else:
                    tableDf["row"] = tableDf["row"] + u", " + \
                        tableDf[cols[i]].astype(unicode)
        
        str_a = tableDf["row"].str.cat(sep=u"), ") + u")"
        sql = u"INSERT INTO {} ({}) VALUES {}".format(
            unicode(table, 'utf-8'), u", ".join(cols), str_a
        )
        
        insert_query(conPSQL, sql)


def txts_to_pgsql_newdb_raw(folder, delimiter, newdb, enc='utf-8', conPSQL={
        'HOST' : 'localhost', 'PASSWORD' : 'admin',
        'USER' : 'postgres' , 'PORT': '5432'
    }, rewrite=True):
    """
    Create a new db and put there all text files in a folder
    
    The file name should be the table name
    """
    
    import os;                 import codecs
    from gasp.oss              import list_files
    from gasp.fm.txt           import txt_to_df
    from gasp.cpu.psql.mng     import create_db, create_tbl
    from gasp.cpu.psql.mng.fld import pgtypes_from_pandasdf
    
    # Create database
    create_db(conPSQL, newdb, overwrite=rewrite)
    conPSQL["DATABASE"] = newdb
    
    # List text files
    txts = list_files(folder, file_format=['.txt', '.csv', '.tsv'])
    
    # List tables data
    table_data = {}
    for txt in txts:
        print txt
        table_data[os.path.splitext(os.path.basename(
            txt))[0]] = txt_to_df(txt, delimiter)
    
    # Create Tables
    dicColsT = {}
    for table in table_data:
        cols = list(table_data[table].columns)
        
        colsT = pgtypes_from_pandasdf(table_data[table])
        dicColsT[table] = colsT
        create_tbl(conPSQL, table, colsT, orderFields=cols)
    
    for txt in txts:
        txt_to_pgsql(
            txt, os.path.splitext(os.path.basename(txt))[0],
            delimiter, encoding_=enc, dic_con=conPSQL
        )

def txts_to_newdb(psqlParam, folder, newdb, delimiter,
                  rewrite=None):
    """
    Create a new database and add TXT Files in Folder as
    tables.
    
    The filename will be the table name
    """
    
    import os
    from gasp.oss          import list_files, get_filename
    from gasp.fm.txt       import txt_to_df
    from gasp.cpu.psql.mng import create_db
    from gasp.to.psql      import df_to_pgsql
    
    # Create database
    create_db(psqlParam, newdb, overwrite=rewrite)
    psqlParam["DATABASE"] = newdb
    
    # List text files
    txts = list_files(folder, file_format=[
        '.txt', '.csv', '.tsv'])
    
    for txt in txts:
        txtDf = txt_to_df(txt, delimiter)
        
        newtbl = df_to_pgsql(psqlParam, txtDf,
            get_filename(txt, forceLower=True))
    
    return newdb


def dbf_to_pgsql(dbf, pg_table, lnk={'HOST':'localhost', 'USER': 'postgres',
                                     'PASSWORD': 'admin', 'PORT': '5432',
                                     'DATABASE': 'shogun_db'}):
    """
    Put all data in a dbf table in a PostgreSQL table
    
    TODO: Check if input file is a dbf file
          Create pgsql table if not exists
    """
    
    from osgeo                import ogr
    from gasp.cpu.gdl.mng.fld import lst_fld
    from gasp.to.psql         import insert_query
    
    def sanitize_value(v):
        if v == 'None':
            return None
        
        if type(v) == int or type(v) == float:
            return v
        else:
            return unicode(v, 'ISO8859-1')
    
    # Open input
    table = ogr.GetDriverByName('ESRI Shapefile').Open(dbf, 0)
    
    cols = lst_fld(dbf)
    
    viewTable = table.GetLayer()
    
    data = []
    for line in viewTable:
        data.append([
            sanitize_value(line.GetField(cols[i])) for i in range(len(cols))
        ])
    
    sql_query = '''INSERT INTO {tbl} ({col}) VALUES %s'''.format(
        tbl=pg_table, col=', '.join(cols)
    )
    
    con = insert_query(lnk, sql_query, execute_many_data=data)


def shp_to_psql_tbl(con_param, shpData, srsEpsgCode, pgTable=None, api="pandas"):
    """
    Send Shapefile to PostgreSQL
    
    if api is equal to "pandas" - GeoPandas API will be used;
    if api is equal to "shp2pgsql" - shp2pgsql tool will be used.
    """
    
    import os
    from gasp.oss import get_filename
    
    if api == "pandas":
        from gasp.fm.shp    import shp_to_df
        from gasp.prop.feat import get_geom_type
    
    elif api == "shp2pgsql":
        from gasp          import exec_cmd
        from gasp.cpu.psql import run_sql_file
        from gasp.oss.ops  import del_file
    
    else:
        raise ValueError(
            'api value is not valid. options are: pandas and shp2pgsql'
        )
    
    # Check if shp is folder
    if os.path.isdir(shpData):
        from gasp.oss import list_files
        
        shapes = list_files(shpData, file_format='.shp')
    
    else:
        from gasp import goToList
        
        shapes = goToList(shpData)
    
    tables = []
    for _i in range(len(shapes)):
        # Get Table name
        tname = get_filename(shapes[_i], forceLower=True) if not pgTable else \
            pgTable[_i] if type(pgTable) == list else pgTable
        
        # Import data
        if api == "pandas":
            # SHP to DataFrame
            df = shp_to_df(shapes[_i])
            
            df.rename(columns={
                x : x.lower() for x in df.columns.values
            }, inplace=True)
            
            if "geometry" in df.columns.values:
                geomCol = "geometry"
            
            elif "geom" in df.columns.values:
                geomCol = "geom"
            
            else:
                print df.columns.values
                raise ValuError("No Geometry found in shp")
            
            # GeoDataFrame to PSQL
            geodf_to_pgsql(
                con_param, df, tname, srsEpsgCode,
                get_geom_type(shapes[_i], name=True, py_cls=False, gisApi='ogr'),
                colGeom=geomCol
            )
        
        else:
            sql_script = os.path.join(
                os.path.dirname(shapes[_i]), tname + '.sql'
            )
            
            cmd = (
                'shp2pgsql -I -s {epsg} -W UTF-8 '
                '{shp} public.{name} > {out}'
            ).format(
                epsg=srsEpsgCode, shp=shapes[_i], name=tname, out=sql_script
            )
            
            outcmd = exec_cmd(cmd)
            
            run_sql_file(con_param, con_param["DATABASE"], sql_script)
            
            del_file(sql_script)
        
        tables.append(tname)
    
    return tables[0] if len(tables) == 1 else tables


def shps_to_onepgsql(folder_shp, epsg, conParam, out_table):
    """
    Send all shps to PGSQL and merge the data into a single table
    """
    
    from gasp.cpu.psql.mng      import tbls_to_tbl
    from gasp.cpu.psql.mng._del import del_tables
    
    pgTables = shp_to_psql_tbl(
        conParam, folder_shp, epsg, api="shp2pgsql"
    )
    
    tbls_to_tbl(conParam, pgTables, out_table)
    
    return out_table


def rst_to_psql(rst, srs, lnk={
        'HOST': 'localhost', 'PORT': '5432',
        'PASSWORD': 'admin', 'USER': 'postgres',
        'DATABASE': 'shogun_db'}, sql_script=None):
    """
    Run raster2pgsql to import a raster dataset into PostGIS Database
    """
    
    import os
    from gasp          import exec_cmd
    from gasp.cpu.psql import run_sql_file
    
    rst_name = os.path.splitext(os.path.basename(rst))[0]
    
    if not sql_script:
        sql_script = os.path.join(os.path.dirname(rst), rst_name + '.sql')
    
    cmd = (
        'raster2pgsql -s {epsg} -I -C -M {rfile} -F -t 100x100 '
        'public.{name} > {sqls}'
    ).format(
        epsg=str(srs), rfile=rst, name=rst_name, sqls=sql_script
    )
    
    run_sql_file(lnk, lnk["DATABASE"], sql_script)
    
    return rst_name


def osm_to_pgsql(osmdata, db, db_host, db_user):
    """
    Import OSM Data in a xml file (pbf or osm) to a PostgreSQL database
    using osm2pgsql
    """
    
    import os
    from gasp import exec_cmd
    
    # Comand to execute osm2pgsql
    cmd = (
        'osm2pgsql -c -l -s -d {bd} -C 2000 -U {user} -H {host} '
        '-k -G {osm}'
    ).format(
        bd = db, user = db_user, host = db_host, osm = osmdata
    )
    
    # Execute the previous comand using subprocess
    outcmd = exec_cmd(cmd)


def xls_to_pgsql(conPSQL, xlsTbl, outTable, excelSheet=None, isAppend=None):
    """
    XLS TO POSTGRESQL using Pandas API
    """
    
    from gasp.fm.xls import xls_to_df
    
    xlsDf = xls_to_df(xlsTbl, sheet=excelSheet)
    
    df_to_pgsql(conPSQL, xlsDf, outTable, append=isAppend)
    
    return outTable


def dbf_to_psql(conParam, dbf, pg_tbl, isAppend=None):
    """
    DBF TO POSTGRESQL using Pandas
    """
    
    from gasp.fm.dbf import dbf_to_df
    
    dbfDf = dbf_to_df(dbf)
    
    df_to_pgsql(conParam, dbfDf, pg_tbl, append=isAppend)
    
    return pg_tbl


def ods_to_psql(conpsql, inOds, sheet, pgtable, isAppend=None):
    """
    ODS file data to PGSQL Table
    """
    
    from gasp.fm.xls import ods_to_df
    
    df = ods_to_df(inOds, sheet)
    
    return df_to_pgsql(conpsql, df, pgtable, append=isAppend)

