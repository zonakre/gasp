"""
GIS API's subpackage:

GRASS GIS Python tools
"""

"""
Other option to start a GRASS GIS Session is:

from grass_session import Session
from grass.script import core as gcore

with Session(gisdb=workspace, location='vteste', create_opts="EPSG:3763"):
    convert('/path/to/file', 'rviaria')
    convert('/path/to/file', 'nos_corr')
    vedit_break('rviaria', 'nos_corr', geomType='line')
    convert('rviaria', '/path/to/file')
"""
