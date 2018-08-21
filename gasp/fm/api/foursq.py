"""
Do things with FourSquare Data
"""

CLIENT_ID     = '4CEA0BIIJKNPKHY3T4XWGEM5QKC5KP2MIO0ODU5RNKICOPPT'
CLIENT_SECRET = 'QVDLNJ01NQ2LCS02AIZSXJI5WZHM5TCH5JRVL1KJUVGOGMCG'


def search_places(lat, lng, radius):
    """
    Search places using an radius as reference.
    """
    
    import pandas
    from gasp.web             import data_from_get
    from gasp.cpu.pnd.mng.fld import listval_to_newcols
    
    data = data_from_get(
        'https://api.foursquare.com/v2/venues/search', dict(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
            v='20180323', ll='{},{}'.format(str(lat), str(lng)),
            intent='browse', radius=str(radius), limit=50
        )
    )
    
    dataDf = pandas.DataFrame(data['response']['venues'])
    
    if not dataDf.shape[0]: return None
    
    dataDf.drop([
        'contact', 'hasPerk', 'referralId', 'venuePage', 'verified',
        'venueChains', 'id'
    ], axis=1, inplace=True)
    
    dataDf.rename(columns={'name' : 'name_main'}, inplace=True)
    
    dataDf = listval_to_newcols(dataDf, 'location')
    
    dataDf.drop([
        "labeledLatLngs", "neighborhood", "state", "distance",
        "crossStreet", 'country', 'city', 'cc', 'address' 
    ], axis=1, inplace=True)
    
    dataDf["formattedAddress"] = dataDf["formattedAddress"].astype(str)
    
    dataDf = listval_to_newcols(dataDf, 'stats')
    dataDf = listval_to_newcols(dataDf, 'categories')
    dataDf = listval_to_newcols(dataDf, 0)
    
    dataDf.drop([
        "primary", "id", "icon"
    ], axis=1, inplace=True)
    
    dataDf = listval_to_newcols(dataDf, 'beenHere')
    
    dataDf.drop([
        "marked", "unconfirmedCount", "lastCheckinExpiredAt"
    ], axis=1, inplace=True)
    
    return dataDf

