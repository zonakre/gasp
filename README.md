GeoData Algorithms for Spatial Problems
====================

The GeoData Algorithms for Spatial Problems (GASP) is a free and open source library for geospatial data science.
It consistes of a set of Python Methods to support the automatization of spatial analysis activities based on Geographic Information Systems Software inside any application. These Python Methods could be included in any high-level application for spatial analysis.


GASP Components
====================
##### Methods and Algorithms for Land Use/ Land Cover mapping #####

- **OSM2LULC** - implementation in Python of an algorithm for the conversion of OpenStreetMap data into Land Use/Land Cover (LULC) maps. [Know more about OSM2LULC!](/gasp/osm2lulc/)

##### Methods and Algorithms for other applications #####

- **TODO**

Installation
====================

### Install dependencies: ###
	
- [Ubuntu/Debian;](/doc/DOC_DEBIAN.md)

### Install GASP: ###

1 - Clone GASP repository from github.com:

	user = "$(whoami)"
	mkdir /home/$user/xpto
	cd /home/$user/xpto
	git clone https://github.com/jasp382/gasp.git

2 - Set some environment variables:

	echo "export PGPASSWORD=yourpostgresqlpassword" | sudo tee --append /home/$user/.bashrc
	echo "export GDALDATA=/usr/share/gdal" | sudo tee --append /home/$user/.bashrc

3 - Edit /../../gasp/gasp/osm2lulc/con-postgresql.json file according your PostgreSQL configuration;

4 - Replace default osmconf.ini file in your GDAL-DATA configuration folder:

	sudo rm /usr/share/gdal/osmconf.ini
	sudo cp /home/$user/xpto/gasp/gasp/osm2lulc/osmconf-gdal.ini /usr/share/gdal/osmconf.ini

5 - Create Python Virtual Environment:

	sudo -H pip install virtualenv
	cd /home/$user/xpto
	virtualenv gasp_env

6 - Install gasp in the created virtual environment:

	source gasp_env/bin/activate
	cd /home/$user/xpto/gasp
	python setup.py install

Documentation
====================
TODO

Development
====================
TODO

Bug reports
====================

License information
====================

See the file \"LICENSE\" for information about the terms & conditions and a DISCLAIMER OF ALL WARRANTIES.