"""
Terrain Modelling Tools
"""


def make_DEM(grass_workspace, data, field, output, extent_template,
             method="IDW"):
    """
    Create Digital Elevation Model
    
    Methods Available:
    * IDW;
    * BSPLINE;
    * SPLINE;
    * CONTOUR
    """
    
    from gasp.oss     import get_filename
    from gasp.cpu.grs import run_grass
    from gasp.cpu.gdl.mng.prj import get_epsg_raster
    
    LOC_NAME = get_filename(data, forceLower=True)[:5] + "_loc"
    
    # Get EPSG From Raster
    EPSG = get_epsg_raster(extent_template)
    
    # Create GRASS GIS Location
    grass_base = run_grass(grass_workspace, location=LOC_NAME, srs=EPSG)
    
    # Start GRASS GIS Session
    import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grass_base, grass_workspace, LOC_NAME, 'PERMANENT')
    
    # IMPORT GRASS GIS MODULES #
    from gasp.to.rst.grs   import rst_to_grs, grs_to_rst
    from gasp.to.shp.grs   import shp_to_grs
    from gasp.cpu.grs.conf import rst_to_region
    
    # Configure region
    rst_to_grs(extent_template, 'extent')
    rst_to_region('extent')
    
    # Convert elevation "data" to GRASS Vector
    elv = shp_to_grs(data, 'elevation')
    
    OUTPUT_NAME = get_filename(output, forceLower=True)
    
    if method == "BSPLINE":
        # Convert to points
        from gasp.cpu.grs.mng.feat     import feat_vertex_to_pnt
        from gasp.cpu.grs.spanlst.surf import bspline
        
        elev_pnt = feat_vertex_to_pnt(elv, "elev_pnt", nodes=None)
        
        outRst = bspline(elev_pnt, field, OUTPUT_NAME, lyrN=1, asCMD=True)
    
    elif method == "SPLINE":
        # Convert to points
        from gasp.cpu.grs.mng.feat     import feat_vertex_to_pnt
        from gasp.cpu.grs.spanlst.surf import surfrst
        
        elev_pnt = feat_vertex_to_pnt(elv, "elev_pnt", nodes=None)
        
        outRst = surfrst(elev_pnt, field, OUTPUT_NAME, lyrN=1, ascmd=True)
    
    elif method == "CONTOUR":
        from gasp.to.rst.grs           import shp_to_raster
        from gasp.cpu.grs.spanlst.surf import surfcontour
        
        # Elevation (GRASS Vector) to Raster
        elevRst = shp_to_raster(elv, 'rst_elevation', field)
        
        # Run Interpolator
        outRst = surfcontour(elevRst, OUTPUT_NAME, ascmd=True)
    
    elif method == "IDW":
        from gasp.cpu.grs.spanlst.surf import ridw
        from gasp.cpu.grs.spanlst      import mapcalc
        from gasp.to.rst.grs           import shp_to_raster
        
        # Elevation (GRASS Vector) to Raster
        elevRst = shp_to_raster(elv, 'rst_elevation', field)
        # Multiply cells values by 100 000.0
        mapcalc('int(rst_elevation * 100000)', 'rst_elev_int')
        # Run IDW to generate the new DEM
        ridw('rst_elev_int', 'dem_int', numberPoints=15)
        # DEM to Float
        mapcalc('dem_int / 100000.0', OUTPUT_NAME)
    
    # Export DEM to a file outside GRASS Workspace
    grs_to_rst(OUTPUT_NAME, output)
    
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

