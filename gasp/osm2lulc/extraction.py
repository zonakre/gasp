"""
Extract specific data from osm files or osm data in a database
"""


def get_unused_data_on_lulcp(pbf, pgsql_data, out_work, nomenclature,
                                dicPostgre={
                                    'HOST': 'localhost',
                                    'USER': 'postgres',
                                    'DATABASE': 'osm',
                                    'TEMPLATE': 'template_postgis',
                                    'PASSWORD': 'admin',
                                    'PORT' : '5432'}):
    """
    Return data not used in osm2lulc procedure
    """


    import os
    from gasp.cpu.psql         import run_sql_file
    from gasp.cpu.psql.mng     import create_db
    from gasp.fm.psql          import sql_query
    from gasp.cpu.psql.mng.fld import cols_name
    from gasp.cpu.psql.pgkeys  import create_pk
    from gasp.to.shp           import psql_to_shp
    from gasp.to.psql          import osm_to_pgsql
    # TODO: replace postgis
    from gasp.postgis.analysis import new_geom_table

    # ################ #
    # Global Variables #
    # ################ #
    # Name of the tables with osmdata after the import with osm2pgsql
    OsmData = {
        'polygon' : 'planet_osm_polygon',
        'line' : 'planet_osm_line',
        'point' : 'planet_osm_point'
    }

    IrrelevantCols = ['addr:housename', 'addr:housenumber', 'addr:interpolation',
                      'generator:source', 'tower:type']

    if nomenclature == 'URBAN_ATLAS':
        tbl_relation = 'rel_osm_ua'
        id_osm = 'osm_id'
    elif nomenclature == 'CORINE_LAND_COVER':
        tbl_relation = 'rel_osm_clc'
        id_osm = 'osm_id'
    elif nomenclature == 'GLOB_LAND_30':
        tbl_relation = 'rel_osm_global'
        id_osm = 'id_osm'

    # ################ #
    # Auxiliar Methods #
    # ################ #
    def get_where_string(dic, operator, table):
        l = []
        for fid in dic:
            if dic[fid][0] == '' or dic[fid][1] == '' or dic[fid][0] == 'sidewalk'\
               or dic[fid][0] == 'cycleway' or dic[fid][0] == 'busway'\
               or dic[fid][0] == 'enity' or dic[fid][0] == 'healthcare':
                continue
            l.append(
                "{t}.{col}{o}'{val}'".format(
                    col=dic[fid][0], o=operator, val=dic[fid][1],
                    t=table
                )
            )
        return " OR ".join(l)


    create_db(dicPostgre, dicPostgre['DATABASE'])
    run_sql_file(dicPostgre, dicPostgre['DATABASE'], pgsql_data)
    run_osm2pgsql(
        pbf, dicPostgre['DATABASE'], dicPostgre['HOST'], dicPostgre['USER']
    )
    # 1. Obtain data used on OSM2LULC procedure
    # 1.1 Get key and value for osm features
    id_related_with = [x[0] for x in sql_query(
        dicPostgre,
        "SELECT {fid} FROM {t}".format(t=tbl_relation, fid=id_osm)
    )]
    key_value = {x[0]: [x[1], x[2]] for x in sql_query(
        dicPostgre,
        "SELECT id, key, value FROM osm_features WHERE {s}".format(
            s=' OR '.join(['id={y}'.format(y=str(x)) for x in id_related_with])
        ))}
    # 1.2 Extract data with this combinations of keys and values
    for tbl in OsmData:
        # Create new primary key
        create_pk(dicPostgre, OsmData[tbl], 'pk_fid')
        cols = cols_name(dicPostgre, OsmData[tbl])
        cols_clean = []
        for i in cols:
            if i not in IrrelevantCols:
                if i == 'natural':
                    cols_clean.append("{t}.{col}".format(
                        t=OsmData[tbl], col=i
                    ))
                else:
                    cols_clean.append(i)
        whr = get_where_string(key_value, "=", OsmData[tbl])
        new_geom_table(
            dicPostgre, cols_clean, OsmData[tbl],
            whr,
            'used{t}'.format(t=OsmData[tbl]),
            pk=False
        )                
        export = psql_to_shp(
            dicPostgre, 'used{t}'.format(t=OsmData[tbl]),
            os.path.join(out_work, 'used{t}.shp'.format(t=OsmData[tbl])),
            api="pgsql2shp", geom_col='way'
        )
    # 2. Obtain data not used on OSM2LULC procedure
    for tbl in OsmData:
        new_geom_table(
            dicPostgre, ['*'], OsmData[tbl],
            "{t}.pk_fid NOT IN (SELECT pk_fid FROM used{t})".format(t=OsmData[tbl]),
            'unused{t}'.format(t=OsmData[tbl]), pk=False
        )
        export = psql_to_shp(
            dicPostgre, 'unused{t}'.format(t=OsmData[tbl]),
            os.path.join(out_work, 'unused{t}.shp'.format(t=OsmData[tbl])),
            api="pgsql2shp", geom_col='way'
        )

