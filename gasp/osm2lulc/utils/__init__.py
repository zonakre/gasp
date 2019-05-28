"""
Generic method to select all osm features to be used in a certain rule
"""

from gasp.osm2lulc.var import DB_SCHEMA, PROCEDURE_DB

def osm_to_sqdb(osmXml, osmSQLITE):
    """
    Convert OSM file to SQLITE DB
    """
    
    from gasp.to.shp import shp_to_shp
    
    return shp_to_shp(
        osmXml, osmSQLITE, gisApi='ogr', supportForSpatialLite=True)


def osm_to_pgsql(osmXml, conPGSQL):
    """
    Use GDAL to import osmfile into PostGIS database
    """
    
    from gasp import exec_cmd
    
    cmd = (
        "ogr2ogr -f PostgreSQL \"PG:dbname='{}' host='{}' port='{}' "
        "user='{}' password='{}'\" {} -lco COLUM_TYPES=other_tags=hstore"
    ).format(
        conPGSQL["DATABASE"], conPGSQL["HOST"], conPGSQL["PORT"],
        conPGSQL["USER"], conPGSQL["PASSWORD"], osmXml
    )
    
    cmdout = exec_cmd(cmd)
    
    return conPGSQL["DATABASE"]


def record_time_consumed(timeData, outXls):
    """
    Record the time consumed by a OSM2LULC procedure version
    in a excel table
    """
    
    import pandas
    from gasp.to import obj_to_tbl
    
    # Produce main table - Time consumed by rule
    main = [{
        'rule' : timeData[i][0], 'time' : timeData[i][1]
    } for i in range(len(timeData.keys())) if timeData[i]]
    
    # Produce detailed table - Time consumed inside rules
    timeInsideRule = []
    timeDataKeys = timeData.keys()
    timeDataKeys.sort()
    
    for i in timeDataKeys:
        if not timeData[i]:
            continue
        
        if len(timeData[i]) == 2:
            timeInsideRule.append({
                'rule' : timeData[i][0],
                'task' : timeData[i][0],
                'time' : timeData[i][1]
            })
        
        elif len(timeData[i]) == 3:
            taskKeys = timeData[i][2].keys()
            taskKeys.sort()
            for task in taskKeys:
                if not timeData[i][2][task]:
                    continue
                
                timeInsideRule.append({
                    'rule' : timeData[i][0],
                    'task' : timeData[i][2][task][0],
                    'time' : timeData[i][2][task][1]
                })
        
        else:
            print 'timeData object with key {} is not valid'.format(i)
    
    # Export tables to excel
    dfs = [pandas.DataFrame(main), pandas.DataFrame(timeInsideRule)]
    
    return obj_to_tbl(dfs, outXls, sheetsName=['general', 'detailed'])


def osm_project(osmDb, srs_epsg, api='SQLITE', isGlobeLand=None):
    """
    Reproject OSMDATA to a specific Spatial Reference System
    """
    
    if api != 'POSTGIS':
        from gasp.sql.mng.prj import ogr2ogr_transform_inside_sqlite as proj
    else:
        from gasp.sql.mng.qw   import ntbl_by_query as proj
        from gasp.sql.mng.geom import add_idx_to_geom
    from .var import osmTableData, GEOM_AREA
    
    osmtables = {}
    
    GEOM_COL = "geometry" if api != "POSTGIS" else "wkb_geometry"
    
    for table in osmTableData:
        if table == "polygons":
            Q = (
                "SELECT building, selection, buildings, area_upper, t_area_upper, "
                "area_lower, t_area_lower, {geomColTrans} AS geometry, "
                "ST_Area(ST_Transform({geomCol}, {epsg})) AS {geom_area} "
                "FROM {t} WHERE selection IS NOT NULL OR "
                "buildings IS NOT NULL OR area_upper IS NOT NULL OR "
                "area_lower IS NOT NULL"
            ).format(
                "" if isGlobeLand else "buildings, ",
                geomColTrans=GEOM_COL if api != 'POSTGIS' else \
                    "ST_Transform({}, {})".format(GEOM_COL, srs_epsg),
                geomCol=GEOM_COL, epsg=srs_epsg,
                t=osmTableData[table], geom_area=GEOM_AREA
            ) if not isGlobeLand else (
                "SELECT building, selection, {geomColTrans} AS geometry FROM "
                "{t} WHERE selection IS NOT NULL"
            ).format(
                geomColTrans=GEOM_COL if api != 'POSTGIS' else \
                    "ST_Transform({}, {})".format(GEOM_COL, srs_epsg),
                    t=osmTableData[table]
            )
        
        elif table == 'lines':
            Q = (
                "SELECT{} roads, bf_roads, basic_buffer, bf_basic_buffer, "
                "{} AS geometry FROM {} "
                "WHERE roads IS NOT NULL OR basic_buffer IS NOT NULL"
            ).format(
                "" if api != 'POSTGIS' else " row_number() OVER(ORDER BY roads) AS gid,",
                GEOM_COL if api != 'POSTGIS' else \
                    "ST_Transform({}, {})".format(GEOM_COL, srs_epsg),
                osmTableData[table]
            )
        
        elif table == 'points':
            Q = "SELECT {}, {} AS geometry FROM {}{}".format(
                "NULL AS buildings" if isGlobeLand else "buildings",
                GEOM_COL if api != 'POSTGIS' else \
                    "ST_Transform({}, {})".format(GEOM_COL, srs_epsg),
                osmTableData[table],
                "" if isGlobeLand else " WHERE buildings IS NOT NULL"
            )
        
        if api != 'POSTGIS':
            proj(
                osmDb, table, 4326, srs_epsg,
                '{}_{}'.format(table, str(srs_epsg)),
                sql=Q
            )
        else:
            proj(osmDb, '{}_{}'.format(table, str(srs_epsg)), Q, api='psql')
            
            add_idx_to_geom(osmDb, '{}_{}'.format(table, str(srs_epsg)), "geometry")
        
        osmtables[table] = '{}_{}'.format(table, str(srs_epsg))
    
    return osmtables


def osm_features_by_rule(nomenclature, rule):
    
    from gasp.fm.sql import query_to_df
    
    COLS = [
        DB_SCHEMA[nomenclature]["CLS_FK"],
        DB_SCHEMA["OSM_FEATURES"]["OSM_KEY"],
        DB_SCHEMA["OSM_FEATURES"]["OSM_VALUE"]
    ]
    
    if rule == 'area_upper' or rule == 'area_lower':
        rule_info_field = ", {}.{}".format(
            DB_SCHEMA[nomenclature]["OSM_RELATION"],
            DB_SCHEMA[nomenclature]["RULES_FIELDS"]["AREA"]
        )
        
        rule_info_field_ = ", osm_cls_rule.{}".format(
            DB_SCHEMA[nomenclature]["RULES_FIELDS"]["AREA"]
        )
        
        COLS.append(DB_SCHEMA[nomenclature]["RULES_FIELDS"]["AREA"])
    
    elif rule == 'roads' or rule == 'basic_buffer':
        rule_info_field = ', {}.{}'.format(
            DB_SCHEMA[nomenclature]["OSM_RELATION"],
            DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"]
        )
        
        rule_info_field_ = ", osm_cls_rule.{}".format(
            DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"]
        )
        
        COLS.append(DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"])
    
    else:
        rule_info_field  = ""
        rule_info_field_ = ""
    
    QUERY = (
        "SELECT osm_cls_rule.{rellulccls}, {osmfeat}.{key}, "
        "{osmfeat}.{val}{rsupfield_} FROM {osmfeat} INNER JOIN ("
            "SELECT {osmrel}.{relosmid}, {osmrel}.{rellulccls}, "
            "{rules}.{_rule_id}, {rules}.{rule_name}{rsupfield} "
            "FROM {osmrel} "
            "INNER JOIN {rules} ON {osmrel}.{rule_id} = {rules}.{_rule_id} "
            "WHERE {rules}.{rule_name} = '{rule_in_processing}'"
        ") AS osm_cls_rule ON {osmfeat}.{osmid} = osm_cls_rule.{relosmid}"
    ).format(
        osmfeat=DB_SCHEMA["OSM_FEATURES"]["NAME"],
        osmid=DB_SCHEMA["OSM_FEATURES"]["OSM_ID"],
        key=DB_SCHEMA["OSM_FEATURES"]["OSM_KEY"],
        val=DB_SCHEMA["OSM_FEATURES"]["OSM_VALUE"],
        osmrel=DB_SCHEMA[nomenclature]["OSM_RELATION"],
        relosmid=DB_SCHEMA[nomenclature]["OSM_FK"],
        rellulccls=DB_SCHEMA[nomenclature]["CLS_FK"],
        rule_id=DB_SCHEMA[nomenclature]["RULE_FK"],
        rules=DB_SCHEMA["RULES"]["NAME"],
        _rule_id=DB_SCHEMA["RULES"]["RULE_ID"],
        rule_name=DB_SCHEMA["RULES"]["RULE_NAME"],
        rule_in_processing=rule,
        rsupfield=rule_info_field,
        rsupfield_=rule_info_field_
    )
    
    osm_featTable = query_to_df(PROCEDURE_DB, QUERY, db_api='sqlite')
    
    return osm_featTable


def get_osm_feat_by_rule(nomenclature):
    
    from gasp.fm.sql import query_to_df
    
    Q = (
        "SELECT jtbl.{rellulccls}, {osmfeat}.{key}, {osmfeat}.{val}, "
        "jtbl.{ruleName}, jtbl.{bufferCol}, jtbl.{areaCol} "
        "FROM {osmfeat} INNER JOIN ("
            "SELECT {osmrel}.{relosmid}, {osmrel}.{rellulccls}, "
            "{rules}.{ruleID}, {rules}.{ruleName}, "
            "{osmrel}.{bufferCol}, {osmrel}.{areaCol} "
            "FROM {osmrel} "
            "INNER JOIN {rules} ON {osmrel}.{_ruleID} = {rules}.{ruleID} "
        ") AS jtbl ON {osmfeat}.{osmid} = jtbl.{relosmid}"
    ).format(
        osmfeat    = DB_SCHEMA["OSM_FEATURES"]["NAME"],
        osmid      = DB_SCHEMA["OSM_FEATURES"]["OSM_ID"],
        key        = DB_SCHEMA["OSM_FEATURES"]["OSM_KEY"],
        val        = DB_SCHEMA["OSM_FEATURES"]["OSM_VALUE"],
        osmrel     = DB_SCHEMA[nomenclature]["OSM_RELATION"],
        relosmid   = DB_SCHEMA[nomenclature]["OSM_FK"],
        rellulccls = DB_SCHEMA[nomenclature]["CLS_FK"],
        _ruleID    = DB_SCHEMA[nomenclature]["RULE_FK"],
        rules      = DB_SCHEMA["RULES"]["NAME"],
        ruleID     = DB_SCHEMA["RULES"]["RULE_ID"],
        ruleName   = DB_SCHEMA["RULES"]["RULE_NAME"],
        bufferCol  = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"],
        areaCol    = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["AREA"]
    )
    
    return query_to_df(PROCEDURE_DB, Q, db_api='sqlite')


def add_lulc_to_osmfeat(osmdb, osmTbl, nomenclature, api='SQLITE'):
    """
    Add LULC Classes in OSM Data Tables
    """
    
    from gasp.sql.mng.qw   import exec_write_q
    from gasp.osm2lulc.var import DB_SCHEMA
    
    KEY_COL   = DB_SCHEMA["OSM_FEATURES"]["OSM_KEY"]
    VALUE_COL = DB_SCHEMA["OSM_FEATURES"]["OSM_VALUE"]
    LULC_COL  = DB_SCHEMA[nomenclature]["CLS_FK"]
    RULE_NAME = DB_SCHEMA["RULES"]["RULE_NAME"]
    
    osmFeaturesDf = get_osm_feat_by_rule(nomenclature)
    
    osmFeaturesDf.loc[:, VALUE_COL] = osmFeaturesDf[KEY_COL] + "='" + \
        osmFeaturesDf[VALUE_COL] + "'"
    
    Q = []
    for rule in osmFeaturesDf[RULE_NAME].unique():
        filterDf = osmFeaturesDf[osmFeaturesDf[RULE_NAME] == rule]
        
        if rule == 'selection' or rule == 'buildings':
            OSM_TABLE  = 'polygons'
            BUFFER_COL = None
            AREA_COL   = None
        
        elif rule == 'roads':
            OSM_TABLE  = 'lines'
            BUFFER_COL = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"]
            AREA_COL   = None
        
        elif rule == 'area_upper' or rule == 'area_lower':
            OSM_TABLE  = 'polygons'
            BUFFER_COL = None
            AREA_COL   = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["AREA"]
        
        elif rule == 'basic_buffer':
            OSM_TABLE  = 'lines'
            BUFFER_COL = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"]
            AREA_COL   = None
        
        filterDf.loc[:, VALUE_COL] = osmTbl[OSM_TABLE] + "." + filterDf[VALUE_COL]
        
        Q.append(
            "ALTER TABLE {} ADD COLUMN {} integer".format(
                osmTbl[OSM_TABLE], rule
            )
        )
        
        if BUFFER_COL:
            Q.append("ALTER TABLE {} ADD COLUMN {} integer".format(
                osmTbl[OSM_TABLE], "bf_" + rule
            ))
        
        if AREA_COL:
            Q.append("ALTER TABLE {} ADD COLUMN {} integer".format(
                osmTbl[OSM_TABLE], "t_" + rule
            ))
        
        for cls in filterDf[LULC_COL].unique():
            __filterDf = filterDf[filterDf[LULC_COL] == cls]
        
            Q.append("UPDATE {} SET {}={} WHERE {}".format(
                osmTbl[OSM_TABLE], rule, cls,
                str(__filterDf[VALUE_COL].str.cat(sep=" OR "))
            ))
        
        if BUFFER_COL:
            for bfdist in filterDf[BUFFER_COL].unique():
                __filterDf = filterDf[filterDf[BUFFER_COL] == bfdist]
                
                Q.append("UPDATE {} SET {}={} WHERE {}".format(
                    osmTbl[OSM_TABLE], "bf_" + rule,
                    bfdist, str(__filterDf[VALUE_COL].str.cat(sep=" OR "))
                ))
        
        if AREA_COL:
            for areaval in filterDf[AREA_COL].unique():
                __filterDf = filterDf[filterDf[AREA_COL] == areaval]
                
                Q.append("UPDATE {} SET {}={} WHERE {}".format(
                    osmTbl[OSM_TABLE], "t_" + rule, areaval,
                    str(__filterDf[VALUE_COL].str.cat(sep=" OR "))
                ))
        
        if rule == 'buildings':
            fd = osmFeaturesDf[
                (osmFeaturesDf[RULE_NAME] == 'selection') & \
                (osmFeaturesDf[KEY_COL] == 'building') & \
                (osmFeaturesDf[LULC_COL] == 12)
            ]
            
            Q += [
                "ALTER TABLE {} ADD COLUMN {} integer".format(
                    osmTbl["points"], rule
                ),
                "UPDATE {} SET {}={} WHERE {}".format(
                    osmTbl["points"], rule, 12,
                    str(fd[VALUE_COL].str.cat(sep=" OR "))
                )
            ]
    
    exec_write_q(osmdb, Q, api='psql' if api == 'POSTGIS' else 'sqlite')

