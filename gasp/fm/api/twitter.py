"""
Methods to extract data from Twitter
"""

# Twitter
TWITTER_TOKEN = {
    'TOKEN'           : "3571004715-NiOnRpRrQZVGpQFvgT2B5zYB6vm3ey01ZBk9QT9",
    'SECRET'          : "WhKkqFzshpFLzRIsS9puPTVZZgKYWhOYcf8JPcAbBFKMI",
    'CONSUMER_KEY'    : "zuDY4LEW37TCesUfObKMeMBPf",
    'CONSUMER_SECRET' : "os60OvpWjb9TLW1ABaiZeRZy8QWcOfwknwYGLBgJOGBE5tQfrM"
}

def search_tweets(lat=None, lng=None, radius=None, keyword=None,
                  NR_ITEMS=500, only_geo=None, __lang=None, key=None,
                  resultType='mixed'):
    """
    Basic tool to extract data from Twitter using a keyword and/or a buffer
    
    * radius should be in Km
    * options for resulType: mixed, recent, popular
    
    Returns an array with the encountered data
    """
    
    import tweepy
    import pandas
    from gasp.cpu.pnd.mng.fld import listval_to_newcols
    from gasp                 import unicode_to_str
    
    if not key:
        TOKEN, SECRET, CONSUMER_KEY, CONSUMER_SECRET = TWITTER_TOKEN['TOKEN'],\
            TWITTER_TOKEN['SECRET'], TWITTER_TOKEN['CONSUMER_KEY'],\
            TWITTER_TOKEN['CONSUMER_SECRET']
    else:
        TOKEN, SECRET, CONSUMER_KEY, CONSUMER_SECRET = key
    
    resultType = None if resultType == 'mixed' else resultType
    
    # Give our credentials to the Twitter API
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    
    auth.set_access_token(TOKEN, SECRET)
    
    api = tweepy.API(auth)
    
    # Request data from twitter
    if not keyword:
        keyword = ''
    
    else:
        if type(keyword) == unicode:
            keyword = unicode_to_str(keyword)
    
    if not lat or not lng or not radius:
        data = [i._json for i in tweepy.Cursor(
            api.search, q=keyword, lang=__lang, count=50,
            result_type=resultType
        ).items(NR_ITEMS)]
    
    else:
        __geostr = '{_lat},{_lng},{r}km'.format(
            _lat=str(lat), _lng=str(lng), r=str(radius)
        )
        
        data = [i._json for i in tweepy.Cursor(
            api.search, q=keyword, geocode=__geostr, lang=__lang,
            count=50, result_type=resultType
        ).items(NR_ITEMS)]
    
    data = pandas.DataFrame(data)
    
    if not data.shape[0]:
        return None
    
    data.rename(columns={
        "id"   : "fid", "created_at" : "tweet_time",
        "lang" : "tweet_lang"
    }, inplace=True)
    
    if "place" in data.columns.values:
        from shapely.geometry import shape
        
        def get_wkt(x):
            if type(x) == dict:
                g = shape(x)
            
                return str(g.wkt)
            
            else:
                return 'None'
        
        # Split in several columns
        data = listval_to_newcols(data, "place")
        
        cols = list(data.columns.values)
        colsRename = {}
        for c in cols:
            if c == "name":
                colsRename[c] = "place_name"
            elif c == "country":
                colsRename[c] = "place_country"
            elif c == "country_code":
                colsRename[c] = "place_countryc"
            elif c == "id":
                colsRename[c] = "place_id"
            else:
                continue
        
        data.rename(columns=colsRename, inplace=True)
        
        if 'bounding_box' in data.columns.values:
            data["place_box"] = data.bounding_box.apply(get_wkt)
        
        else:
            data["place_box"] = 'None'
    
    cols = list(data.columns.values)
    
    INTEREST_COLS = [
        'user', 'text', 'fid', 'geo', 'tweet_time', 'retweeted',
        'tweet_lang', 'place_name', 'place_country', 'place_countryc',
        'place_id', 'place_box'
    ]
    
    delCols = [x for x in cols if x not in INTEREST_COLS]
    
    data.drop(delCols, axis=1, inplace=True)
    
    dfGeom = data[data["geo"].astype(str) != 'None']
    
    if only_geo and not dfGeom.shape[0]:
        return None
    
    elif not only_geo and not dfGeom.shape[0]:
        result = data
        
        result["latitude"]  = result["geo"]
        result["longitude"] = result["geo"]
        result.drop("geo", axis=1, inplace=True)
    
    else:
        dfGeom = pandas.concat([
            dfGeom.drop(["geo"], axis=1),
            dfGeom["geo"].apply(pandas.Series)
        ], axis=1)
        
        dfGeom = pandas.concat([
            dfGeom.drop(["coordinates"], axis=1),
            dfGeom["coordinates"].apply(pandas.Series)
        ], axis=1)
        
        dfGeom.rename(columns={0 : 'latitude', 1 : 'longitude'}, inplace=True)
        
        dfGeom.drop("type", axis=1, inplace=True)
        
        if only_geo:
            result = dfGeom
        
        else:
            dfNoGeom = data[data["geo"].astype(str) == 'None']
            dfNoGeom["latitude"] = dfNoGeom["geo"]
            dfNoGeom["longitude"] = dfNoGeom["geo"]
            
            dfNoGeom.drop("geo", axis=1, inplace=True)
            
            result = dfGeom.append(dfNoGeom, ignore_index=True)
    
    result = pandas.concat([
        result.drop(["user"], axis=1),
        result["user"].apply(pandas.Series)
    ], axis=1)
    
    result.rename(columns={
        'screen_name' : 'user', 'id' : 'user_id', 'location' : 'user_location',
        'name' : 'username'
    }, inplace=True)
    
    INTEREST_COLS += [
        'user', 'followers_count', 'user_id', 'user_location', 'username',
        'latitude', 'longitude'
    ]
    cols = list(result.columns.values)
    delCols = [c for c in cols if c not in INTEREST_COLS]
    
    result.drop(delCols, axis=1, inplace=True)
    
    result["url"] = 'https://twitter.com/' + \
        result["user"].astype(str) + '/status/' + \
        result["fid"].astype(str)
    
    return result


def tweets_to_json(lat, lng, radius, keyword, jsonfile,
                   NR_ITEMS=500, ONLY_GEO=None):
    """
    Search for tweets and save them in a json file
    """

    import tweepy
    import json

    if not keyword:
        keyword=''

    data = search_tweets(lat=lat, lng=lng, radius=float(radius)/1000.0, keyword=keyword,
                         NR_ITEMS=NR_ITEMS, only_geo=ONLY_GEO)

    with open(jsonfile, mode='w') as f:
        json.dump(data, f, encoding='utf-8')

    return jsonfile


def search_places(_lat, lng, radius):
    """
    Search Places using API Twitter
    """
    
    import tweepy
    
    # Give our credentials to the Twitter API
    auth = tweepy.OAuthHandler(
        TWITTER_TOKEN['CONSUMER_KEY'], TWITTER_TOKEN['CONSUMER_SECRET']
    )

    auth.set_access_token(
        TWITTER_TOKEN['TOKEN'], TWITTER_TOKEN['SECRET']
    )

    api = tweepy.API(auth_handler=auth)
    
    # Reqest data from twitter
    data = api.reverse_geocode(lat=_lat, long=lng,
        accuracy=radius
    )
    
    return data

