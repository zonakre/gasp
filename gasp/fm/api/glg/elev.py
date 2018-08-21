"""
Tools to give use to the Google Elevation API
"""

from . import select_api_key
from . import record_api_utilization
from . import check_result

from gasp.web import json_fm_httpget
# ------------------------------ #
"""
Global Variables
"""
GOOGLE_ELEVATION_URL = 'https://maps.googleapis.com/maps/api/elevation/json?'
# ------------------------------ #


def pnt_elev(x, y):
    """
    Get point elevation
    """
    
    # Get key
    KEY_FID, GOOGLE_API_KEY, NR_REQUESTS = select_api_key()
    
    # Record KEY utilization
    record_api_utilization(KEY_FID, GOOGLE_API_KEY, NR_REQUESTS + 1)
    
    try:
        elev_array = json_fm_httpget(
            '{url}locations={lat},{lng}&key={key}'.format(
                url=GOOGLE_ELEVATION_URL,
                lat=str(y), lng=str(x), key=GOOGLE_API_KEY
            )
        )
    except:
        raise ValueError(
            'Something went wrong. The URL was {}'.format(URL)
        )
    
    return check_result(elev_array, "ELEVATION")


def pnts_elev(pnt_coords):
    """
    Get Points Elevation
    """
    
    # Get key
    KEY_FID, GOOGLE_API_KEY, NR_REQUESTS = select_api_key()
    
    URL = '{url}locations={loc}&key={key}'.format(
        url=GOOGLE_ELEVATION_URL, key=GOOGLE_API_KEY,
        loc=pnt_coords
    )
    
    record_api_utilization(KEY_FID, NR_REQUESTS + 1)
    
    try:
        elv = json_fm_httpget(URL)
    
    except:
        raise ValueError(
            'Something went wrong. The URL was {}'.format(URL)
        )
    
    return elv

