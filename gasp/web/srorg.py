"""
Get Data related to one EPSG Code from the web
"""

def get_prj_web(epsg, output):
    from gasp.web import get_file
    
    if epsg != 3857:
        sr_org = 'http://spatialreference.org/ref/epsg/{srs}/prj/'.format(
            srs=str(epsg)
        )
    
    else:
        sr_org = 'http://spatialreference.org/ref/sr-org/7483/prj/'
    
    prj_file = get_file(sr_org, output)
    
    return prj_file


def get_wkt_web(epsg):
    import requests
    
    
    if epsg != 3857:
        URL = 'http://spatialreference.org/ref/epsg/{}/ogcwkt/'.format(
            str(epsg)
        )
    
    else:
        URL = 'http://spatialreference.org/ref/sr-org/7483/ogcwkt/'
    
    r = requests.get(URL)
    
    return r.text


def get_wkt_esri(epsg):
    import requests
    
    if epsg != 3857:
        URL = 'http://spatialreference.org/ref/epsg/{}/esriwkt/'.format(
            str(epsg)
        )
    
    else:
        URL = 'http://spatialreference.org/ref/sr-org/6864/esriwkt/'
    
    r = requests.get(URL)
    
    return str(r.text)

