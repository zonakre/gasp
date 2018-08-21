"""
Tools to convert OSM data into PGSQL Database
"""

def osm2pgsql_to_shapefile(osm_data, epsg, wOut, lmt=None,
                           dicPostgre={
                               'HOST': 'localhost',
                               'USER': 'postgres',
                               'DATABASE': 'uk_sample',
                               'TEMPLATE': 'postgis_template',
                               'PASSWORD': 'admin',
                               'PORT' : '5432'
                               }):
    """
    Tool to convert osm data into shapefile using osm2pgsql
    """

    import os
    from gasp.cpu.psql.mng import create_db
    from gasp.to.shp       import psql_to_shp


    # Name of the tables with osmdata after the import with osm2pgsql
    OsmData = {
        'polygon' : 'planet_osm_polygon',
        'line' : 'planet_osm_line',
        'point' : 'planet_osm_point'
    }

    # ################ #
    # Auxiliar Methods #
    # ################ #
    def ReprojectOsmData(dic_link, osmdata, epsg, ic):
        from gasp.cpu.psql.mng.prj import re_project

        for key in osmdata.keys():
            proj_table, pk, geom = re_project(
                dic_link, osmdata[key], 'way', str(epsg), key, del_cols=ic)
            osmdata[key] = [proj_table, pk, geom]
        return osmdata

    # ##################### #
    # OSM To ESRI Shapefile #
    # ##################### #
    # ############################# #
    # Extract OSM data with osmosis #
    # ############################# #
    if lmt != None:
        from gasp.osm.osmosis import osmosis_extract
        
        pbf = os.path.join(
            wOut, 'extracted.pbf'
        )
        osmosis_extract(
            lmt, osm_data, epsg, wOut, pbf
        )
    else:
        pbf=osm_data

    # ################################### #
    # Create a new database on PostgreSQL #
    # ################################### #
    create_db(dicPostgre, dicPostgre['DATABASE'])

    # ######################################### #
    # Import OSM Data into the created database #
    # ######################################### #
    run_osm2pgsql(
        pbf, dicPostgre['DATABASE'], dicPostgre['HOST'], dicPostgre['USER']
    )

    # ################## #
    # Reproject OSM DATA #
    # ################## #
    if int(epsg) != 4326:
        IrrelevantCols = ['addr:housename', 'addr:housenumber',
                          'addr:interpolation', 'generator:source', 'tower:type']
        OsmData = ReprojectOsmData(dicPostgre, OsmData,
                                   int(epsg), IrrelevantCols)
    else:
        for k in OsmData.keys():
            OsmData[k] = [OsmData[k], '', 'way']

    # ######################## #
    # Export Data to Shapefile #
    # ######################## #
    for k in OsmData.keys():
        export = psql_to_shp(
            dicPostgre, OsmData[k][0],
            os.path.join(wOut, 'osm_{}.shp'.format(k)),
            geom_col=OsmData[k][2], api='pgsql2shp'
        )
        OsmData[k] = os.path.join(wOut, 'osm_{}.shp'.format(k))

    return OsmData


def get_osm_shape(inputBoundary, outputSHP, EPSG=4326,
                  conPGSQL={
                      'HOST': 'localhost', 'USER': 'postgres',
                      'TEMPLATE': 'postgis_template', 'PASSWORD': 'admin',
                      'PORT' : '5432', 'DATABASE': 'osmdata'
                      }):
    """
    Download data from OSM and convert it to a OGR Compilant File Format
    
    Requires connection to PostgreSQL with PostGIS
    """
    
    import os
    from gasp.oss.ops         import create_folder, del_folder
    from gasp.cpu.gdl.osm.get import download_by_boundary
    
    # Temporary output
    wTmp = create_folder(os.path.join(
        outputSHP, 'osmdata'
    ))
    
    # Get OSM data
    downOSM = os.path.join(
        wTmp, 'osmdatafile.xml'
    )
    status = download_by_boundary(inputBoundary, downOSM, epsg=EPSG)
    
    # OSM TO SHAPEFILE
    osmshp = osm2pgsql_to_shapefile(
        downOSM, EPSG, outputSHP, dicPostgre=conPGSQL
    )
    
    del_folder(wTmp)

