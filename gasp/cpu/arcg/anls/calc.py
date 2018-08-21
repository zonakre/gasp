"""
Calculate some indicators based on geometric relations
"""

import arcpy


def count_geom_by_polygon(shp_geom, polygons, w,
                          count_geom_field='COUNT', population_field=None):
    """
    Intersect a given geometry with all polygons in a feature class and
    count the number of geometries inside each polygon.

    The user can also give a population field. The method will return the number
    of geometries by person * 1000.

    E.g. Count the number of points (health care centers, sports) by 
    statistical unit;
    E.g. Count the number of points by inhabitants in each statistical unit.
    """

    from gasp.cpu.arcg.lyr        import feat_lyr
    from gasp.cpu.arcg.mng.fld    import add_field
    from gasp.cpu.arcg.anls.ovlay import intersect
    from gasp.cpu.arcg.anls.exct  import select_by_attr

    # ArcGIS environment
    arcpy.env.workspace = w
    arcpy.env.overwriteOutput = True

    polygon_lyr = feat_lyr(polygons)

    add_field(polygon_lyr, count_geom_field, "SHORT", "8")

    if population_field:
        geom_pop = count_geom_field + population_field
        if len(geom_pop) >= 10:
            geom_pop = geom_pop[:10]
        add_field(polygon_lyr, geom_pop, "FLOAT", "")

    # Update polygon layer
    cursor = arcpy.UpdateCursor(polygon_lyr)
    line = cursor.next()
    while line:
        """TODO: Use select by attributes and not select analysis"""
        fid = int(line.getValue("FID"))

        poly_extracted = "poly_{f}.shp".format(f=str(fid))
        select_by_attr(
            polygon_lyr,
            "FID = {f}".format(f=str(fid)),
            poly_extracted
        )

        intersected = "pnt_{f}.shp".format(f=str(fid))
        intersect([shp_geom, poly_extracted], intersected)

        cs = arcpy.SearchCursor(intersected)
        nr_pnt = 0
        for i in cs:
            nr_pnt += 1

        if population_field:
            population = int(line.getValue(population_field))
            pnt_by_pop = (nr_pnt / float(pnt_by_pop)) * 1000.0
            line.setValue(geom_pop, pnt_by_pop)

        line.setValue(count_geom_field, nr_pnt)

        cursor.updateRow(line)

        line = cursor.next()


def area_by_population(polygons, inhabitants, field_inhabitants, work,
                       area_field='area_pop'):
    """
    Feature area (polygons) by feature inhabitant (inhabitants)
    """

    from gasp.cpu.arcg.lyr        import feat_lyr
    from gasp.cpu.arcg.mng.fld    import add_field
    from gasp.mng.genze  import dissolve
    from gasp.cpu.arcg.anls.ovlay import intersect
    from gasp.cpu.arcg.anls.exct  import select_by_attr

    # ArcGIS environment
    arcpy.env.overwriteOutput=True
    arcpy.env.workspace = work

    inhabitant_lyr = feat_lyr(inhabitants)

    add_field(inhabitant_lyr, area_field, "FLOAT", "")

    cursor = arcpy.UpdateCursor(inhabitant_lyr)
    lnh = cursor.next()

    while lnh:
        """TODO: Use intersection only once"""
        f = int(lnh.getValue("FID"))

        poly_extracted = "poly_{fid}.shp".format(fid=str(f))
        select_by_attr(
            inhabitant_lyr,
            "FID = {fid}".format(fid=str(f)),
            poly_extracted
        )

        intersected = "int_{fid}.shp".format(fid=str(f))
        intersect([polygons, poly_extracted], intersected)
        
        dissolved = dissolve(
            intersected, "diss_{f_}.shp".format(f_=str(f)),
            "FID", api='arcpy'
        )

        cs = arcpy.SearchCursor(dissolved)

        l = cs.next()

        geom = arcpy.Describe(dissolved).shapeFieldName

        while l:
            area = float(l.getValue(geom).area)
            l = cs.next()

        pop = int(lnh.getValue(field_inhabitants))

        try:
            indicator = area / pop
        except:
            indicator = 0.0 / pop

        lnh.setValue(area_field)
        cursor.updateRow(lnh)

        lnh = cursor.next()

