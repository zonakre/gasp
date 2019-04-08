"""
Data to a Relational Database
"""

def psql_insert_query(dic_pgsql, query, execute_many_data=None):
    """
    Insert data into a PGSQL Table
    """
    
    from gasp.sql.c      import connection
    from psycopg2.extras import execute_values
    
    con = psqlcon(dic_pgsql)
    
    cursor = con.cursor()
    if execute_many_data:
        execute_values(cursor, query, execute_many_data)
    
    else:
        cursor.execute(query)
    
    con.commit()
    cursor.close()
    con.close()


def sqlite_insert_query(db, table, cols, new_values, execute_many=None):
    """
    Method to insert data into SQLITE Database
    """
    
    import sqlite3
    from gasp import goToList
    
    cols = goToList(cols)
    
    if not cols:
        raise ValueError('cols value is not valid')
    
    conn = sqlite3.connect(db)
    cs = conn.cursor()
    
    if not execute_many:
        cs.execute(
            "INSERT INTO {} ({}) VALUES {}".join(
                table, ', '.join(cols),
                ', '.join(
                    ['({})'.format(', '.join(row)) for row in new_values]
                )
            )
        )
    
    else:
        cs.executemany(
            '''INSERT INTO {} ({}) VALUES ({})'''.format(
                table, ', '.join(cols),
                ', '.join(['?' for i in range(len(cols))])
            ),
            new_values
        )
    
    conn.commit()
    cs.close()
    conn.close()


def df_to_db(conParam, df, table, append=None, api='psql'):
    """
    Pandas Dataframe to PGSQL table
    
    API options:
    * psql;
    * sqlite
    """
    
    if api != 'psql' and api != 'sqlite':
        raise ValueError('API {} is not available'.format(api))
    
    from gasp.sql.c import alchemy_engine
    
    pgengine = alchemy_engine(conParam, api=api)
    
    df.to_sql(
        table, pgengine,
        if_exists='replace' if not append else 'append',
        index=False
    )
    
    return table


def geodf_to_psql(conParam, df, pgtable, epsg, geomType,
                  colGeom="geometry", isAppend=None):
    """
    Pandas GeoDataframe to PGSQL table
    """
    
    from geoalchemy2 import Geometry, WKTElement
    from gasp.sql.c  import alchemy_engine
    
    pgengine = alchemy_engine(conParam, api='psql')
    
    df["geom"] = df[colGeom].apply(
        lambda x: WKTElement(x.wkt, srid=epsg)
    )
    
    if colGeom != 'geom':
        df.drop(colGeom, axis=1, inplace=True)
    
    df.to_sql(
        pgtable, pgengine, if_exists='replace' if not isAppend else 'append',
        index=False, dtype={'geom' : Geometry(geomType, srid=epsg)}
    )
    
    return pgtable


def db_to_db(conDBA, conDBB, typeDBA, typeDBB):
    """
    All tables in one Database to other database
    
    typesDB options:
    * sqlite
    * psql
    """
    
    import os
    from gasp.fm.sql      import query_to_df
    from gasp.sql.mng.tbl import lst_tbl
    from gasp.sql.mng.db import create_db
    
    # List Tables in DB A
    tbls = lst_tbl(conDBA, excludeViews=True, api=typeDBA)
    
    # Create database B
    if typeDBB == 'psql':
        con_param = {
            "HOST" : conDBB["HOST"], "USER" : conDBB["USER"],
            "PORT" : conDBB["PORT"], "PASSWORD" : conDBB["PASSWORD"]
        }
        
        if "TEMPLATE" in conDBB:
            con_param["TEMPLATE"] = conDBB["TEMPLATE"]
        
        NEW_DB = conDBB["DATABASE"]
    
    else:
        con_param = os.path.dirname(conDBB)
        NEW_DB = os.path.basename(conDBB)
    
    db_b = create_db(con_param, NEW_DB, overwrite=False, api=typeDBB)
    
    # Table to Database B
    for tbl in tbls:
        df = query_to_df(
            conDBA, "SELECT * FROM {}".format(tbl), db_api=typeDBA
        )
        
        df_to_db(conDBB, df, tbl, append=None, api=typeDBB)


def tbl_to_db(tblFile, dbCon, sqlTbl, delimiter=None, encoding_='utf-8',
              sheet=None, isAppend=None, api_db='psql'):
    """
    Table file to Database Table
    
    API's available:
    * psql;
    * sqlite;
    """
    
    import os
    from gasp import goToList
    from gasp.oss import get_fileformat, get_filename
    from gasp.fm  import tbl_to_obj
    
    if os.path.isdir(tblFile):
        from gasp.oss import list_files
        
        tbls = list_files(tblFile)
    
    else:
        tbls = goToList(tblFile)
    
    outSQLTbl = goToList(sqlTbl)
    
    RTBL = []
    for i in range(len(tbls)):
        ff = get_fileformat(tbls[i])
    
        if ff == '.csv' or ff == '.txt' or ff == '.tsv':
            if not delimiter:
                raise ValueError((
                    "To convert TXT to DB table, you need to give a value for the "
                    "delimiter input parameter"
                ))
        
            __enc = 'utf-8' if not encoding_ else encoding_
        
            data = tbl_to_obj(
                tbls[i], _delimiter=delimiter, encoding_=__enc
            )
    
        elif ff == '.dbf':
            data = tbl_to_obj(tbls[i])
    
        elif ff == '.xls' or ff == '.xlsx':
            data = tbl_to_obj(tbls[i], sheet=sheet)
    
        elif ff == '.ods':
            if not sheet:
                raise ValueError((
                    "To convert ODS to DB table, you need to give a value "
                    "for the sheet input parameter"
                ))
        
            data = tbl_to_obj(tbls[i], sheet=sheet)
    
        else:
            raise ValueError('{} is not a valid table format!'.format(fFormat))
    
        # Send data to database
        _rtbl = df_to_db(
            dbCon, data,
            outSQLTbl[i] if i+1 <= len(tbls) else get_filename(tlbs[i]),
            append=isAppend, api=api_db
        )
        
        RTBL.append(_rtbl)
    
    return RTBL[0] if len(RTBL) == 1 else RTBL


def shp_to_psql(con_param, shpData, srsEpsgCode, pgTable=None, api="pandas"):
    """
    Send Shapefile to PostgreSQL
    
    if api is equal to "pandas" - GeoPandas API will be used;
    if api is equal to "shp2pgsql" - shp2pgsql tool will be used.
    """
    
    import os
    from gasp.oss import get_filename
    
    if api == "pandas":
        from gasp.fm        import tbl_to_obj
        from gasp.prop.feat import get_geom_type
    
    elif api == "shp2pgsql":
        from gasp         import exec_cmd
        from gasp.sql     import run_sql_file
        from gasp.oss.ops import del_file
    
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
            df = tbl_to_obj(shapes[_i])
            
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


def shps_to_onepsql(folder_shp, epsg, conParam, out_table):
    """
    Send all shps to PGSQL and merge the data into a single table
    """
    
    from gasp.sql.mng.tbl import tbls_to_tbl, del_tables
    
    pgTables = shp_to_psql(
        conParam, folder_shp, epsg, api="shp2pgsql"
    )
    
    tbls_to_tbl(conParam, pgTables, out_table)
    
    del_tables(conParam, pgTables)
    
    return out_table


def rst_to_psql(rst, srs, lnk={
        'HOST': 'localhost', 'PORT': '5432',
        'PASSWORD': 'admin', 'USER': 'postgres',
        'DATABASE': 'shogun_db'}, sql_script=None):
    """
    Run raster2pgsql to import a raster dataset into PostGIS Database
    """
    
    import os
    from gasp     import exec_cmd
    from gasp.sql import run_sql_file
    
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


def txts_to_db(folder, conDB, delimiter, __encoding='utf-8', apidb='psql',
               dbIsNew=None, rewrite=None, toDBViaPandas=True):
    """
    Executes tbl_to_db for every file in a given folder
    
    The file name will be the table name
    """
    
    from gasp.oss import list_files, get_filename
    
    if dbIsNew:
        # Create database
        from gasp.sql.mng.db import create_db
        
        if api == 'psql':
            __con = {
                'HOST' : conDB["HOST"], 'PORT' : conDB["PORT"],
                'USER' : conDB["USER"], 'PASSWORD' : conDB["PASSWORD"]
            }
            
            DB = conDB["DATABASE"]
        
        else:
            import os
            __con = os.path.dirname(conDB)
            DB = os.path.basename(conDB)
        
        create_db(__con, DB, api=apidb, overwrite=rewrite)
    
    __files = list_files(folder, file_format=['.txt', '.csv', '.tsv'])
    
    if toDBViaPandas:
        """
        Send data to DB using Pandas
        """
        for __file in __files:
            tbl_to_db(
                __file, conDB, get_filename(__file),
                delimiter=delimiter, encoding_=__encoding, api_db=apidb
            )
    
    else:
        """
        Send data to DB using regular Python API
        """
        
        from gasp.sql.mng.fld import pgtypes_from_pandasdf
        from gasp.sql.mng.tbl import create_tbl
        from gasp.fm          import tbl_to_obj
        
        # Get Table data
        table_data = {get_filename(f) : tbl_to_obj(
            f, _delimiter=delimiter, encoding_=__encoding
        ) for f in __files}
        
        
        if apidb == 'psql':
            # Create Tables
            dicColsT = {}
            for table in table_data:
                cols = list(table_data[table].columns)
            
                colsT = pgtypes_from_pandasdf(table_data[table])
                dicColsT[table] = colsT
            
                create_tbl(conDB, table, colsT, orderFields=cols)
            
            # Insert data into tables
            for table in table_data:
                cols = list(table_data[table].columns)
                
                tableDf = table_data[table]
                
                for i in range(len(cols)):
                    if not i:
                        if dicColsT[table][cols[i]] == "text":
                            tableDf["row"] = u"('" + \
                                tableDf[cols[i]].astype(unicode) + u"'"
                        
                        else:
                            tableDf["row"] = u"(" + \
                                tableDf[cols[i]].astype(unicode)
                    
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
                
                psql_insert_query(conDB, sql)
        else:
            raise ValueError("API {} is not available".format(apidb))

