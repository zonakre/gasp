"""
Terrain Modelling Tools
"""


def make_DEM(grass_workspace, data, field, output, EPSG, extent_template):
    from gasp.cpu.grs import run_grass
    
    # Create GRASS GIS Location
    grass_base = run_grass(
        grass_workspace, location='gr_loc', srs=EPSG
    )
    
    # Start GRASS GIS Session
    import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grass_base, grass_workspace, 'gr_loc', 'PERMANENT')
    
    # IMPORT GRASS GIS MODULES #
    from gasp.to.rst.grs           import shp_to_raster, rst_to_grs, grs_to_rst
    from gasp.to.shp.grs           import shp_to_grs
    from gasp.cpu.grs.conf         import rst_to_region
    from gasp.cpu.grs.spanlst      import mapcalc
    from gasp.cpu.grs.spanlst.surf import ridw
    
    # Configure region
    rst_to_grs(extent_template, 'extent')
    rst_to_region('extent')
    
    # Convert elevation "data" to GRASS Vector
    elv = shp_to_grs(data, 'elevation')
    
    # Elevation (GRASS Vector) to Raster
    shp_to_raster(elv, 'rst_elevation', field)
    
    # Multiply cells values by 100 000.0
    mapcalc('int(rst_elevation * 100000)', 'rst_elev_int')
    
    # Run IDW to generate the new DEM
    ridw('rst_elev_int', 'dem_int', numberPoints=15)
    
    # DEM to Float
    mapcalc('dem_int / 100000.0', 'final_dem')
    
    # Export DEM to a file outside GRASS Workspace
    grs_to_rst('final_dem', output)
    
    return output


def compare_mdt_with_google_data(grass_workspace, dem, nr_pnt_sample, output, epsg=3763):
    """
    Method to compare a random sample of a DEM to Google Maps Elevation API
    """
    """
    grass_workspace - path to grass_workspace
    
    dem - path to dem
    
    nr_pnt_sample - number of the point sample that will be used to compare
    the elevation data
    
    output - path to the output
    
    epsg - Spatial Reference System EPSG code
    """
    from . import run_grass
    
    # Create GRASS GIS Location
    grass_base = run_grass(grass_workspace, 'gr_loc', epsg)
    
    # Start GRASS GIS Session
    import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grass_base, grass_workspace, 'gr_loc', 'PERMANENT')
    
    # Configure GRASS GIS Region
    from gasp.cpu.grs.conf import rst_to_region
    from gasp.to.rst.grs   import rst_to_grs
    # Import DEM to GRASS
    rst_to_grs(dem, 'dem')
    
    # Create Random Points
    from .tools import create_random_points_on_raster
    create_random_points_on_raster('dem', nr_pnt_sample, 'points')
    
    # Extract elevation values of each point
    # Extrair para cada ponto o valor de altitude da celula do MDT que inclui
    # esse ponto
    # Usar ferramenta do v.what.rast do GRASS GIS
    # A utilizacao desta ferramenta implica que exista um campo preparado na
    # tabela do tema 'points' para receber a informacao de altitude a ser 
    # extraidado raster 'dem'
    # A ferramenta que cria um campo na tabela de atributos e a v.db.addcolumn
    
    # Export points
    # Use convert
    
    # Extract data from Google Maps Elevation API
    # Use method 'elevation_to_pntshp'. It is in the file /grass_gis/google.py
    
    # Calculate the difference of the elevation values

