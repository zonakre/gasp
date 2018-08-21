"""
Use web responses
"""


def json_fm_httpget(url):
    """
    Return a json object with the json data available in a URL
    """
    
    import urllib2
    import json
    
    web_response = urllib2.urlopen(url)
    
    read_page = web_response.read()
    
    json_data = json.loads(read_page)
    
    return json_data


def get_file_ul(url, output):
    """
    Return a file from the web and save it somewhere
    """
    
    import urllib
    
    data_file = urllib.URLopener()
    
    data_file.retrieve(url, output)
    
    return output


def get_file(url, output):
    """
    Save content of url
    """
    
    import requests
    
    r = requests.get(url, allow_redirects=True)
    
    with open(output, 'wb') as f:
        f.write(r.content)
    
    return output


def data_from_get(url, getParams):
    """
    Return json from URL - GEST Request
    """
    
    import json
    import requests
    
    response = requests.get(url=url, params=getParams)
    
    return json.loads(response.text)


def data_from_post(url, postdata, head='application/json'):
    """
    Return data retrieve by a POST Request
    """
    
    import json
    import requests
    
    r = requests.post(
        url, data=json.dumps(postdata),
        headers={'content-type' : head}
    )
    
    return r.json()


"""
Parse HTML data via Python
"""
def get_text_in_html(url, tags=['h1', 'h2', 'h3', 'p']):
    """
    Get p tags from HTML
    """
    
    import urllib2
    import re
    from bs4 import BeautifulSoup
    
    response = urllib2.urlopen(url)
    
    html_doc = response.read()
    
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    txtData = {
        tag : [unicode(
            re.sub('<[^>]+>', '', str(x)).strip('\n'),
            'utf-8'
        ) for x in soup.find_all(tag)] for tag in tags
    }
    
    return txtData


def get_text_in_CssClass(url, classTag, cssCls, texTags=['p']):
    """
    Get text from tags inside a specific object with one tag (classTag) and
    CSS Class (cssCls)
    
    Not recursive: textTags must be direct child of the classTag/cssCls
    """
    
    import urllib2
    import re
    from bs4  import BeautifulSoup
    from gasp import goToList
    
    resp = urllib2.urlopen(url)
    
    html_doc = resp.read()
    
    soup = BeautifulSoup(html_doc, 'html.parser')
    
    data = soup.find_all(classTag, class_=cssCls)
    
    rslt = {}
    texTags = goToList(texTags)
    for node in data:
        for t in texTags:
            chld = node.findChildren(t, recursive=False)
            
            l = [unicode(
                re.sub('<[^>]+>', '', str(x)).strip('\n'), 'utf-8'
            ) for x in chld]
            
            if t not in rslt:
                rslt[t] = l
            
            else:
                rslt[t] += l
    
    return rslt


"""
E-mail related
"""

def email_exists_old(email):
    """
    Verify if a email exists
    """
    
    from validate_email import validate_email
    
    return validate_email(email, verify=True)


def email_exists(email):
    """
    Verify if a email exists using MailBoxLayer API
    
    
    """
    
    API_KEY = "b7bee0fa2b3ceb3408bd8245244b1479"
    
    URL = (
        "http://apilayer.net/api/check?access_key={}&email={}&"
        "smtp=1&format=1"
    ).format(API_KEY, str(email))
    
    jsonArray = json_fm_httpget(URL)
    
    return jsonArray["smtp_check"]
