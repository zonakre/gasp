"""
GRASS GIS Tools for Feature Class
"""

from grass.pygrass.modules import Module

def feat_vertex_to_pnt(inShp, outPnt, nodes=True):
    """
    Feature Class to a Point Feature Class
    
    v.to.points - Creates points along input lines in new vector map with
    2 layers.
    
    v.to.points creates points along input 2D or 3D lines, boundaries and
    faces. Point features including centroids and kernels are copied from
    input vector map to the output. For details see notes about type parameter.
    
    The output is a vector map with 2 layers. Layer 1 holds the category of
    the input features; all points created along the same line have the same
    category, equal to the category of that line. In layer 2 each point has
    its unique category; other attributes stored in layer 2 are lcat - the
    category of the input line and along - the distance from line's start.
    
    By default only features with category are processed, see layer parameter
    for details.
    """
    
    toPnt = Module(
        "v.to.points", input=inShp,
        output=outPnt,
        use="node" if nodes else "vertex",
        overwrite=True, run_=False,
        quiet=True
    )
    
    toPnt()
    
    return outPnt


def geomattr_to_db(shp, attrCol, attr, geomType, createCol=True,
                   unit=None, lyrN=1, ascmd=None):
    """
    v.to.db - Populates attribute values from vector features.
    
    v.to.db loads vector map features or metrics into a database table,
    or prints them (or the SQL queries used to obtain them) in a form
    of a human-readable report. For uploaded/printed category values '-1'
    is used for 'no category' and 'null'/'-' if category cannot be
    found or multiple categories were found. For line azimuths '-1' is used
    for closed lines (start equals end).
    
    attrs options area:
    * cat: insert new row for each category if doesn't exist yet
    * area: area size
    * compact: compactness of an area, calculated as 
    compactness = perimeter / (2 * sqrt(PI * area))
    * fd: fractal dimension of boundary defining a polygon, calculated as
    fd = 2 * (log(perimeter) / log(area))
    * perimeter: perimeter length of an area
    * length: line length
    * count: number of features for each category
    * coor: point coordinates, X,Y or X,Y,Z
    * start: line/boundary starting point coordinates, X,Y or X,Y,Z
    * end: line/boundary end point coordinates, X,Y or X,Y,Z
    * sides: categories of areas on the left and right side of the boundary,
    'query_layer' is used for area category
    * query: result of a database query for all records of the geometry(or
    geometries) from table specified by 'query_layer' option
    * slope: slope steepness of vector line or boundary
    * sinuous: line sinuousity, calculated as line length / distance between
    end points
    * azimuth: line azimuth, calculated as angle between North direction and
    endnode direction at startnode
    * bbox: bounding box of area, N,S,E,W
    """
    
    from gasp import goToList
    
    attrCol = goToList(attrCol)
    
    if createCol:
        from gasp.mng.grstbl import add_field
        
        for c in attrCol:
            add_field(shp, c, "DOUBLE PRECISION", asCMD=ascmd) 
    
    if not ascmd:
        vtodb = Module(
            "v.to.db", map=shp, type=geomType, layer=lyrN, option=attr,
            columns=",".join(attrCol) if attr != 'length' else attrCol[0],
            units=unit, run_=False, quiet=True
        )
        
        vtodb()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.to.db map={} type={} layer={} option={} "
            "columns={} units={} --quiet"
        ).format(
            shp, geomType, lyrN, attr,
            ",".join(attrCol) if attr != 'length' else attrCol[0],
            unit
        ))


def copy_insame_vector(inShp, colToBePopulated, srcColumn, destinyLayer,
                       geomType="point,line,boundary,centroid",
                       asCMD=None):
    """
    Copy Field values from one layer to another in the same GRASS Vector
    """
    
    if not asCMD:
        vtodb = Module(
            "v.to.db", map=inShp, layer=destinyLayer, type=geomType,
            option="query", columns=colToBePopulated,
            query_column=srcColumn, run_=False, quiet=True
        )
    
        vtodb()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.to.db map={} layer={} type={} option=query columns={} "
            "query_column={} --quiet"
        ).format(inShp, destinyLayer, geomType, colToBePopulated,
                 srcColumn))

