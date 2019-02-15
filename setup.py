#from distutils.core import setup
from setuptools import setup

setup(
    name='gasp',
    version='0.0.1',
    description='GASP',
    url='https://github.com/JoaquimPatriarca/GIS-SENPY',
    author='Joaquim Patriarca',
    author_email='joaquimaspatriarca@gmail.com',
    license='GPL',
    packages=[
        # Main module
        'gasp', 'gasp.anls', 'gasp.mng', 'gasp.prop',
        # ******************************************************************** #
        'gasp.djg', 'gasp.djg.files', 'gasp.djg.gis', 'gasp.djg.mdl',
        # ******************************************************************** #
        'gasp.fm'         , 'gasp.fm.api', 'gasp.fm.api.fb', 'gasp.fm.api.glg',
        'gasp.fm.api.here',
        # ******************************************************************** #
        'gasp.cpu',
        # ******************************************************************** #
        'gasp.cpu.arcg'        ,      'gasp.cpu.arcg._3D', 'gasp.cpu.arcg._3D.mng',
        'gasp.cpu.arcg.anls'   ,      'gasp.cpu.arcg.mng', 'gasp.cpu.arcg.mng.rst',
        'gasp.cpu.arcg.maps'   , 'gasp.cpu.arcg.netanlst',
        'gasp.cpu.arcg.spanlst',    'gasp.cpu.arcg.stats',
        # ******************************************************************** #
        'gasp.cpu.gdl'      ,    'gasp.cpu.gdl.anls', 'gasp.cpu.gdl.anls.prox',
        'gasp.cpu.gdl.img'  ,     'gasp.cpu.gdl.mng',   'gasp.cpu.gdl.mng.rst',
        'gasp.cpu.gdl.spanlst',    'gasp.cpu.gdl.splite',
        'gasp.cpu.gdl.stats',
        # ******************************************************************** #
        'gasp.cpu.grs'        , 'gasp.cpu.grs.anls'    , 'gasp.cpu.grs.img',
        'gasp.cpu.grs.mng'    , 'gasp.cpu.grs.netanlst', 'gasp.cpu.grs.spanlst',
        # ******************************************************************** #
        'gasp.cpu.pnd'             ,     'gasp.cpu.pnd.anls',
        'gasp.cpu.pnd.mng'         , 'gasp.cpu.pnd.netanlst',
        'gasp.cpu.pnd.netanlst.glg',     'gasp.cpu.pnd.prop',
        # ******************************************************************** #
        'gasp.cpu.psql'    , 'gasp.cpu.psql.anls', 'gasp.cpu.psql.charts',
        'gasp.cpu.psql.mng',
        # ******************************************************************** #
        'gasp.cpu.qgis', 'gasp.cpu.qgis.anls', 'gasp.cpu.qgis.mng',
        # ******************************************************************** #
        'gasp.cpu.saga'    ,    'gasp.cpu.saga.anls',
        'gasp.cpu.saga.mng', 'gasp.cpu.saga.spanlst',
        # ******************************************************************** #
        'gasp.geosrv', 'gasp.geosrv.stores', 'gasp.geosrv.styl',
        # ******************************************************************** #
        'gasp.ine', 'gasp.lndsld', 'gasp.mapseries', 'gasp.ogcsld',
        # ******************************************************************** #
        'gasp.osm2lulc',
        # ******************************************************************** #
        'gasp.oss',
        # ******************************************************************** #
        'gasp.sqLite', 'gasp.sqLite.mng', 'gasp.terrain',
        # ******************************************************************** #
        'gasp.to', 'gasp.to.rst', 'gasp.to.shp',
        # ******************************************************************** #
        'gasp.mob',
        # ******************************************************************** #
        'gasp.xls', 'gasp.xls.adv'
    ],
    install_requires=[
        'psycopg2==2.7.7',
        'click==7.0', 'click-plugins==1.0.4', 'cligj==0.5.0',
        'django==1.11.18', 'django-widget-tweaks==1.4.1',
        'numpy==1.15.4',
        'sqlalchemy==1.2.15', 'geoalchemy2==0.5.0',
        'shapely==1.6.4',
        'fiona==1.8.4', 'pyproj==1.9.6',
        'pandas==0.24.1', 'geopandas==0.4.0',
        'xlrd==1.2.0', 'xlwt==1.3.0', 'xlsxwriter==1.1.5',
        #'pygdal==1.11.3.3',
        'netCDF4==1.4.2',
        'polyline==1.3.2',
        'google-api-python-client==1.7.7',
        'unidecode==1.0.23',
        'flickrapi==2.4.0',
        'six==1.12.0',
        'requests==2.11.1',
        'requests_oauthlib==1.1.0',
        'requests_toolbelt==0.8.0',
        'tweepy==3.7.0',
        'pysocks==1.6.7'
    ],
    include_package_data=True
)
