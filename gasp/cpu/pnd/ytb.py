"""
Extract Geodata from Youtube using OGR
"""


def geovideos_to_array(search_words, epsg_out=4326,
                  spatial_filter=None, epsg_filter=4326):
    """
    Locate videos on youtube and save these locations to a vectorial file
    """
    
    import os
    
    from gasp.oss.ops               import del_files_by_name
    from gasp.cpu.gdl               import create_point
    from gasp.cpu.gdl.mng.prj       import project_geom
    from gasp.fm.api.glg.ytb        import get_video_details_by_keyword
    from gasp.cpu.gdl.anls.topology import point_in_polygon
    from gasp.cpu.gdl.anls.prox.bfs import draw_buffer
    
    videos = get_video_details_by_keyword(search_words)
    
    videos_with_location = []
    
    for video in videos:
        if video['y'] and video['x']:
            videos_with_location.append(video)
    
    if not len(videos_with_location):
        # Return nodata
        return 0
    
    if spatial_filter:
        from gasp.cpu.gdl.anls.prox.bfs import getBufferParam
        
        x_center, y_center, dist = getBufferParam(
            spatial_filter, epsg_filter)
        
        bufferCenter = project_geom(
            create_point(x_center, y_center), 4326, 3857)
        
        bufferGeom = draw_buffer(bufferCenter, dist)
        filterData = []
    
    for instance in videos_with_location:
        # Create point
        WGS_POINT = create_point(
            float(instance['x']),
            float(instance['y'])
        )
        
        point = project_geom(WGS_POINT, 4326, 3857)
        
        isPointInPolygon = point_in_polygon(point, bufferGeom)
        
        if isPointInPolygon:
            if epsg_out != 4326:
                trans_point = project_geom(WGS_POINT, 4326, epsg_out)
                
                instance['x'] = trans_point.GetX()
                instance['y'] = trans_point.GetY()
            
            filterData.append(instance)
    
    return filterData


def geovideos_to_shp(buffer_shp, epsg_in, outshp, keyword, epsg_out=4326):
    """
    Search for data in Youtube and return a Shapefile with that data
    """
    
    from gasp.to.shp import df_to_shp
    
    videos = geovideos_to_array(
        keyword, epsg_out=epsg_out, 
        spatial_filter=buffer_shp, 
        epsg_filter=epsg_in
    )
    
    if not videos: return None
    
    array_to_shp(videos, outshp, epsg=epsg_out)

