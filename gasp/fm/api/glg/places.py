"""
Google Places API Web Service
"""

from . import select_api_key
from . import record_api_utilization

from gasp.web import json_fm_httpget

# ------------------------------ #
"""
Global Variables
"""
GOOGLE_PLACES_URL = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
# ------------------------------ #

def get_places_by_radius(lat, lng, radius, keyword=None,
                         _type=None):
    """
    Get Places
    """
    
    def sanitize_coord(coord):
        if ',' in str(coord):
            return str(coord).replace(',', '.')
        
        else:
            return str(coord)
    
    from gasp import unicode_to_str
    
    # Get Google Maps Key
    KEY_FID, GOOGLE_API_KEY, NR_REQUESTS = select_api_key()
    
    # Prepare URL
    keyword = unicode_to_str(keyword) if type(keyword) == unicode else \
        keyword
    
    str_keyword = '' if not keyword else '&keyword={}'.format(
        keyword
    )
    
    _type = unicode_to_str(_type) if type(_type) == unicode else \
        _type
    
    str_type = '' if not _type else '&type={}'.format(_type)
    
    URL = '{url}location={lt},{lg}&radius={r}&key={apik}{kw}{typ}'.format(
        url  = GOOGLE_PLACES_URL,
        apik = GOOGLE_API_KEY,
        lt   = sanitize_coord(lat),
        lg   = sanitize_coord(lng),
        r    = sanitize_coord(radius),
        kw   = str_keyword, typ = str_type
    )
    
    data = json_fm_httpget(URL)
    
    # Record Key utilization
    record_api_utilization(KEY_FID, NR_REQUESTS)
    
    return data

