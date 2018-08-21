"""
Network Analyst tools converted to Python
"""


import arcpy
import os

def closest_facility(network, rdv_name, facilities, incidents, table,
                    oneway_restriction=False):
    """
    Execute the Closest Facility tool - Produce Closest Facility Layer
    
    * facilities = destiny points
    * incidents = start/origins points
    """
    
    from gasp.cpu.arcg.lyr import feat_lyr
    from gasp.cpu.arcg.mng import table_to_table
    
    """if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
    
    else:
        raise ValueError('Network analyst extension is not avaiable')"""
    
    if oneway_restriction:
        oneway = "Oneway"
    else:
        oneway = ""
    
    nName = str(os.path.basename(network))
    junc = nName + '_Junctions'
    
    arcpy.MakeClosestFacilityLayer_na(
        in_network_dataset=network, 
        out_network_analysis_layer="cls_fac", 
        impedance_attribute="Minutes",
        travel_from_to="TRAVEL_TO", 
        default_cutoff="",
        default_number_facilities_to_find="1",
        accumulate_attribute_name="",
        UTurn_policy="NO_UTURNS",
        restriction_attribute_name=oneway,
        hierarchy="NO_HIERARCHY",
        hierarchy_settings="",
        output_path_shape="TRUE_LINES_WITH_MEASURES",
        time_of_day="",
        time_of_day_usage="NOT_USED"
    )
    
    lyr_fa = feat_lyr(facilities)
    arcpy.AddLocations_na(
        "cls_fac", "Facilities", lyr_fa, "", "5000 Meters", "",
        "{_rdv} SHAPE;{j} NONE".format(_rdv=str(rdv_name), j=str(junc)),
        "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE",
        "{_rdv} #;{j} #".format(_rdv=str(rdv_name), j=str(junc))
    )
    
    lyr_in = feat_lyr(incidents)
    arcpy.AddLocations_na(
        "cls_fac", "Incidents", lyr_in, "", "5000 Meters", "",
        "{_rdv} SHAPE;{j} NONE".format(_rdv=str(rdv_name), j=str(junc)),
        "MATCH_TO_CLOSEST", "APPEND", "NO_SNAP", "5 Meters", "INCLUDE",
        "{_rdv} #;{j} #".format(_rdv=str(rdv_name), j=str(junc))
    )
    
    arcpy.Solve_na("cls_fac", "SKIP", "TERMINATE", "")
    
    table_to_table("cls_fac\\Routes", table)


def polygons_to_facility(netdataset, polygons, facilities, outTbl,
                         oneway=None, rdv=None, junctions=None,
                         save_result_input=None):
    """
    Execute the Closest Facility tool after calculation of polygons
    centroids
    """
    
    from gasp.cpu.arcg.lyr       import feat_lyr
    from gasp.cpu.arcg.mng.feat  import feat_to_pnt
    from gasp.cpu.arcg.mng.fld   import add_field
    from gasp.cpu.arcg.mng.fld   import calc_fld
    from gasp.cpu.arcg.mng.joins import join_table    
    
    arcpy.env.overwriteOutput = True
    
    # Polygons to Points
    polLyr = feat_lyr(polygons)
    pntShp = os.path.join(
        os.path.dirname(polygons),
        os.path.splitext(os.path.basename(polygons))[0] + '_pnt.shp'
    )
    pntShp = feat_to_pnt(polLyr, pntShp, pnt_position='INSIDE')
    
    closest_facility(
        netdataset, facilities, pntShp, outTbl, 
        oneway_restriction=oneway, rdv=rdv, junc=junctions
    )
    
    field_output = 'dst' + os.path.splitext(os.path.basename(facilities))[0]
    add_field(outTbl, field_output[:10], "FLOAT", "10", "3")
    calc_fld(outTbl, field_output[:10], "[Total_Minu]")
    
    if save_result_input:
        add_field(outTbl, 'j', "SHORT", "6")
        calc_fld(outTbl, 'j', "[IncidentID]-1")
        join_table(polLyr, "FID", outTbl, "j", field_output[:10])


def folderPolygons_to_facility(inFolder, network, dest, outFolder,
                               oneway=None, rdv=None, junctions=None):
    """
    Run execute polygons_to_facility for every feature class in the inFolder
    """
    
    from gasp.oss import list_files
    
    lst_fc = list_files(inFolder, file_format='shp')
    
    for fc in lst_fc:
        out = os.path.join(
            outFolder,
            os.path.splitext(os.path.basename(fc))[0] + '.dbf'
        )
        
        polygons_to_facility(
            network, fc, dest, out,
            oneway=oneway, rdv=rdv, junctions=junctions
        )


def points_to_facility(netDataset, rdv_name, points, facilities, outTable,
                       oneway=None, save_result_input=None):
    """
    Execute Closest Facility and save the result in the points table
    """
    
    from gasp.cpu.arcg.mng.fld   import add_field
    from gasp.cpu.arcg.mng.fld   import calc_fld
    from gasp.cpu.arcg.mng.joins import join_table
    
    arcpy.env.overwriteOutput = True
    
    closest_facility(
        netDataset, rdv_name, facilities, points, outTable,
        oneway_restriction=oneway
    )
    
    if save_result_input:
        add_field(outTable, 'j', "SHORT", 6)
        calc_fld(outTable, 'j', "[IncidentID]-1")
        join_table(points, "FID", outTable, "j", "Total_Minu")


def folderPoints_to_facility(netDataset, rdv_name, lst_points, facilities,
                             ONEWAY=None):
    """
    Execute points_to_facilities in loop
    """
    
    import os
    
    for fc in lst_points:
        points_to_facility(
            netDataset, rdv_name, fc, facilities,
            os.path.join(
                os.path.dirname(fc),
                'tbl_{}.dbf'.format(os.path.splitext(os.path.basename(fc))[0])
            ),
            oneway=ONEWAY, save_result_input=True
        )

