"""
PostGIS stores creation
"""


def create_store(store, workspace, pg_con, gs_con={
        'USER':'admin', 'PASSWORD': 'geoserver',
        'HOST':'localhost', 'PORT': '8888'
    }, protocol='http'):
    """
    Create a store for PostGIS data
    """
    
    import os
    import requests
    
    from gasp.oss.ops import create_folder, del_folder
    from gasp         import random_str
    from gasp.Xml     import write_xml_tree
    
    # Create folder to write xml
    wTmp = create_folder(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            random_str(7)
        )
    )
    
    # Create obj with data to be written in the xml
    tree_order = {
        "dataStore": ["name", "type", "enabled", "workspace",
                      "connectionParameters", "__default"],
        "connection:Parameters": [
            ("entry", "key", "port"), ("entry", "key", "user"),
            ("entry", "key", "passwd"), ("entry", "key", "dbtype"),
            ("entry", "key", "host"), ("entry", "key", "database"),
            ("entry", "key", "schema")
        ]
    }
    
    xml_tree = {
        "dataStore" : {
            "name"      : store,
            "type"      : "PostGIS",
            "enabled"   : "true",
            "workspace" : {
                "name"  : workspace
            },
            "connectionParameters" : {
                ("entry", "key", "port") : pg_con["PORT"],
                ("entry", "key", "user") : pg_con["USER"],
                ("entry", "key", "passwd") : pg_con["PASSWORD"],
                ("entry", "key", "dbtype") : "postgis",
                ("entry", "key", "host") : pg_con["HOST"],
                ("entry", "key", "database") : pg_con["DATABASE"],
                ("entry", "key", "schema") : "public"
            },
            "__default" : "false"
        }
    }
    
    # Write xml
    xml_file = write_xml_tree(
        xml_tree, os.path.join(wTmp, 'pgrest.xml'), nodes_order=tree_order
    )
    
    # Create Geoserver Store
    url = (
        '{pro}://{host}:{port}/geoserver/rest/workspaces/{wname}/'
        'datastores.xml'
    ).format(
        host=gs_con['HOST'], port=gs_con['PORT'], wname=workspace, pro=protocol
    )
    
    with open(xml_file, 'rb') as f:
        r = requests.post(
            url,
            data=f,
            headers={'content-type': 'text/xml'},
            auth=(gs_con['USER'], gs_con['PASSWORD'])
        )
        f.close()
    
    del_folder(wTmp)
    
    return r

