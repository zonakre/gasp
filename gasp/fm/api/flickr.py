"""
Methods to extract data from Flickr
"""

# Flickr
FLICKR_PUBLIC = 'b4f00205d43bfe8a4edd40f800388eb3'
FLICKR_SECRET = 'c235398aae0743f0'

def search_photos(lat=None, lng=None, radius=None, keyword=None,
                  apiKey=None):
    """
    Method to connect with Flickr in order to querie photos and other kinds
    of data using keyworkds, coordinates and a radius
    
    Returns a Pandas Dataframe
    """
    
    import pandas
    from flickrapi            import FlickrAPI
    from gasp                 import unicode_to_str
    from gasp.cpu.pnd.mng.fld import listval_to_newcols
    
    if apiKey:
        FLIC_PUB, FLIC_SEC = apiKey
    else:
        FLIC_PUB, FLIC_SEC = FLICKR_PUBLIC, FLICKR_SECRET
    
    flickr_engine = FlickrAPI(
        FLIC_PUB, FLIC_SEC, format='parsed-json', store_token=False
    )
    
    extras = 'url_l,geo,date_taken,date_upload,description'
    
    if not keyword:
        keyword=''
    
    else:
        if type(keyword) == unicode:
            keyword = unicode_to_str(keyword)
    
    if not lat or not lng or not radius:
        data = flickr_engine.photos.search(
            text=keyword, pp=500, extras=extras
        )
    
    else:
        data = flickr_engine.photos.search(
            text=keyword, lat=lat, lon=lng, radius=radius, pp=500,
            extras=extras
        )
    
    photos_array = pandas.DataFrame(data['photos']['photo'])
    
    if not photos_array.shape[0]:
        return None
    
    photos_array = listval_to_newcols(photos_array, "description")
    
    return photos_array

