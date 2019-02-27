from gasp.anls.ovlay import check_shape_diff

# Inputs

SHAPES_TO_COMPARE = {
    '/home/osmtolulc/webvia/coimbra/v11_cmb.shp'       : "cls_int",
    '/home/osmtolulc/webvia/coimbra/v12_cmb.shp'       : "cls_int",
    '/home/osmtolulc/webvia/coimbra/v13_cmb_2x2.shp'   : "cls_int",
    '/home/osmtolulc/webvia/coimbra/v13_cmb_5x5.shp'   : "cls_int",
    '/home/osmtolulc/webvia/coimbra/v13_cmb_10x10.shp' : "cls_int",
    '/home/osmtolulc/webvia/coimbra/v14_cmb_2x2.shp'   : "cls_int",
    '/home/osmtolulc/webvia/coimbra/v14_cmb_5x5.shp'   : "cls_int",
    '/home/osmtolulc/webvia/coimbra/v14_cmb_10x10.shp' : "cls_int"
}

OUT_FOLDER = '/home/osmtolulc/webvia/cmb_anls'
REPORT     = '/home/osmtolulc/webvia/cmb_compare.xlsx'

conPARAM = {
    "HOST" : "localhost", "PORT" : "5432",
    "USER" : "postgres", "PASSWORD" : "admin", "TEMPLATE" : "template_postgis"
}

DB = "cmb_compare"

srs_code = 3857

RASTER_TEMPLATE = '/home/osmtolulc/webvia/boundaries/coimbra_20x20.shp'

check_shape_diff(SHAPES_TO_COMPARE, OUT_FOLDER, REPORT, conPARAM, DB, srs_code,
                GIS_SOFTWARE="GRASS", GRASS_REGION_TEMPLATE=RASTER_TEMPLATE)

