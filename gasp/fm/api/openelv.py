"""
Extract data from the Open Elevation API

More info at: https://open-elevation.com/
and https://github.com/Jorl17/open-elevation/blob/master/docs/api.md
"""


def locations_elev(locations):
    """
    Return the elevation of a set of elevations
    
    locations is array like:
    {"locations": [
        {"latitude": 42.562, "longitude": -8.568},
        {"latitude": 41.161758, "longitude": -8.583933}
    ]}
    """
    
    from gasp.web import data_from_post
    
    URL = 'https://api.open-elevation.com/api/v1/lookup'
    
    data = data_from_post(URL, locations)
    
    return data

