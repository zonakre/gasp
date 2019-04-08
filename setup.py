#from distutils.core import setup
from setuptools import setup

setup(
    name='gasp',
    version='0.0.1',
    description='GASP',
    url='https://github.com/jasp382/gasp',
    author='jasp382',
    author_email='joaquimaspatriarca@gmail.com',
    license='GPL',
    packages=[
        # Main module
        'gasp',
        # ******************************************************************** #
        'gasp.anls', 'gasp.anls.prox',
        # ******************************************************************** #
        'gasp.dt', 'gasp.dt.sat',
        # ******************************************************************** #
        'gasp.fm',
        # ******************************************************************** #
        'gasp.hydro',
        # ******************************************************************** #
        'gasp.lndsld',
        # ******************************************************************** #
        'gasp.maps', 'gasp.maps.arctbx',
        # ******************************************************************** #
        'gasp.mng', 'gasp.mng.fld', 'gasp.mng.xlstbx',
        # ******************************************************************** #
        'gasp.mob', 'gasp.mob.api', 'gasp.mob.api.glg',
        'gasp.mob.arctbx', 'gasp.mob.grstbx',
        # ******************************************************************** #
        'gasp.osm2lulc',
        # ******************************************************************** #
        'gasp.oss',
        # ******************************************************************** #
        'gasp.prop',
        # ******************************************************************** #
        'gasp.spanlst',
        # ******************************************************************** #
        'gasp.sql', 'gasp.sql.anls', 'gasp.sql.charts', 'gasp.sql.mng',
        # ******************************************************************** #
        'gasp.stats',
        # ******************************************************************** #
        'gasp.terrain',
        # ******************************************************************** #
        'gasp.to', 'gasp.to.rst', 'gasp.to.shp',
        # ******************************************************************** #
        'gasp.web',
        'gasp.web.dsn', 'gasp.web.dsn.fb',
        'gasp.web.geosrv', 'gasp.web.geosrv.styl', 'gasp.web.geosrv.styl.sld',
        'gasp.web.glg',
        # ******************************************************************** #
        'gasp.cpu',
        'gasp.cpu.arcg'     , 'gasp.cpu.arcg._3D', 'gasp.cpu.arcg._3D.mng',
        'gasp.cpu.arcg.anls', 'gasp.cpu.arcg.mng', 'gasp.cpu.arcg.mng.rst',
        'gasp.cpu.arcg.spanlst', 'gasp.cpu.arcg.stats',
        # ******************************************************************** #
        'gasp.cpu.grs', 'gasp.cpu.grs.mng', 'gasp.cpu.grs.spanlst',
    ],
    install_requires=[
        'psycopg2-binary==2.8.2',
        'click==7.0', 'click-plugins==1.0.4', 'cligj==0.5.0',
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
