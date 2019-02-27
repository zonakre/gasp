"""
Write SLD with Python
"""


def write_sld(attribute_name, attribute_value_colors, sld_path,
              geometry=None, opacity=None, DATA='CATEGORICAL'):
    """
    Write a sld file using an association between field attributes and a color

    * attribute_name - name of a column in a layer
    * DATA - Options: CATEGORICAL | QUANTITATIVE
    
    * attribute_colors - dict or table with attribute values as keys and
    colors (HEX/RGB) as values.
    
    For QUANTITATIVE DATA: 'attribute_value_colors' should be a xls
    table with the following structure
    
    COLORS SHEET STRUCTURE (Sheet Index = 0):
         | min | max | R | G | B
       1 |  0  |  5  | X | X | X
       2 |  5  |  10 | X | X | X
       3 |  10 |  15 | X | X | X
       4 |  15 |  20 | X | X | X
       5 |  20 |  25 | X | X | X
    
    OR a dict with such:
    dict = {
        1 : {'min':  0, 'max':  5, 'R': X, 'G': X, 'B': X},
        2 : {'min':  5, 'max': 10, 'R': X, 'G': X, 'B': X},
        3 : {'min': 10, 'max': 15, 'R': X, 'G': X, 'B': X},
        4 : {'min': 15, 'max': 20, 'R': X, 'G': X, 'B': X},
        5 : {'min': 20, 'max': 25, 'R': X, 'G': X, 'B': X}
    }

    NOTE: This will work only for polygon/linear features
    TODO: CATEGORICAL works with JSON and dict
          QUANTITATIVE works with xls
    """

    import os
    from gasp.Xml          import write_xml_tree
    from gasp.ogcsld.rules import get_categorical_rules
    from gasp.ogcsld.rules import get_quantitative_rules

    if type(attribute_value_colors) != dict and \
       os.path.exists(attribute_value_colors):
        if os.path.splitext(attribute_value_colors)[1] == '.json':
            if DATA == 'CATEGORICAL':
                import json
                json_data = open(attribute_value_colors, 'r')
                attribute_value_colors = json.load(json_data)
            
            elif DATA == 'QUANTITATIVE':
                raise ValueError((
                    'At the moment, this method could not generate a sld '
                    'for quantitative data using a JSON File'
                ))
            
            else:
                raise ValueError((
                    '{} is not a valid option! Please use one of the two: '
                    'QUANTITATIVE; CATEGORICAL.'
                ).format(DATA))
        
        elif os.path.splitext(attribute_value_colors)[1] == '.xls':
            if DATA == 'CATEGORICAL':
                raise ValueError((
                    'At the moment, this method could not generate a sld '
                    'for categorical data using a JSON File'
                ))
            
            elif DATA == 'QUANTITATIVE':
                from gasp.fm.xls import xls_to_dict
                attribute_value_colors = xls_to_dict(attribute_value_colors)
            
            else:
                raise ValueError((
                    '{} is not a valid option! Please use one of the two: '
                    'QUANTITATIVE; CATEGORICAL.'
                ).format(DATA))            
        
        else:
            raise ValueError('Your file is not a json or a xls')

    elif type(attribute_value_colors) != dict and not \
         os.path.exists(attribute_value_colors):
        raise ValueError((
            'ERROR in argument attribute_value_colors: '
            'You need to define a dict or give a valid path to a json file or'
            ' to a xls file'
        ))

    GEOMETRY = str(geometry) if geometry else 'Polygon'
    OPACITY = str(opacity) if opacity else '0.5'

    # Create Feature Type Style RULES
    sldRules = get_categorical_rules(
        attribute_value_colors, attribute_name, GEOMETRY, OPACITY
    ) if DATA == 'CATEGORICAL' else get_quantitative_rules(
        attribute_value_colors, attribute_name, GEOMETRY, OPACITY
    ) if DATA == 'QUANTITATIVE' else None
    
    if not sldRules: raise ValueError(
        'DATA should has the value CATEGORICAL or QUANTITATIVE'
    )

    # SLD Basic structure
    xml_sld_root = (
        'sld:StyledLayerDescriptor', 'xmlns', 'http://www.opengis.net/sld',
        'xmlns:sld', 'http://www.opengis.net/sld',
        'xmlns:gml', 'http://www.opengis.net/gml',
        'xmlns:ogc', 'http://www.opengis.net/ogc',
        'version', '1.0.0'
    )

    sld = {
        xml_sld_root: {
            'sld:UserLayer' : {
                'sld:LayerFeatureConstraints': {
                    'sld:FeatureTypeConstraint': ''
                },
                'sld:UserStyle': {
                    'sld:Name' : 'Default Styler',
                    'sld:IsDefault': '1',
                    'sld:FeatureTypeStyle': {
                        'sld:Name': 'group 0',
                        'sld:FeatureTypeName': 'Feature',
                        (1, 'sld:SemanticTypeIdentifier'): 'generic:geometry',
                        (2, 'sld:SemanticTypeIdentifier'): 'colorbrewer:unique:corinne'
                    }
                }
            }
        }
    }

    sld_order = {
        xml_sld_root : ['sld:UserLayer'],
        'sld:UserLayer' : ['sld:LayerFeatureConstraints', 'sld:UserStyle'],
        'sld:UserStyle' : ['sld:Name', 'sld:IsDefault', 'sld:FeatureTypeStyle'],
        'sld:FeatureTypeStyle' : ['sld:Name', 'sld:FeatureTypeName',
                                  (1, 'sld:SemanticTypeIdentifier'),
                                  (2, 'sld:SemanticTypeIdentifier')],
        'ogc:PropertyIsEqualTo' : ['ogc:PropertyName', 'ogc:Literal'],
        'ogc:And' : ['ogc:PropertyIsLessThanOrEqualTo', 'ogc:PropertyIsGreaterThan'],
        'ogc:PropertyIsLessThanOrEqualTo' : ['ogc:PropertyName', 'ogc:Literal'],
        'ogc:PropertyIsGreaterThan' : ['ogc:PropertyName', 'ogc:Literal'],
        'sld:Fill': [
            ('sld:CssParameter', 'name', 'fill'),
            ('sld:CssParameter', 'name', 'fill-opacity')
        ]
    }

    sld[xml_sld_root]['sld:UserLayer']['sld:UserStyle']['sld:FeatureTypeStyle'].update(sldRules)

    symbolizer = 'sld:PolygonSymbolizer' if GEOMETRY == 'Polygon' \
        else 'sld:LineSymbolizer' if GEOMETRY == 'Line' \
        else 'sld:PolygonSimbolizer'

    for i in range(len(sldRules.keys())):
        sld_order['sld:FeatureTypeStyle'].append((i+1, 'sld:Rule'))
        sld_order[(i+1, 'sld:Rule')] = [
            'sld:Name', 'sld:Title', 'ogc:Filter', symbolizer
        ]

    write_xml_tree(sld, sld_path, nodes_order=sld_order)

    return sld_path


def write_sld_from_pgtable(
    table, attr_field_source, sld_path,
    attr_field_table=None, rgb_fields=None, pgsql={
        'HOST': 'localhost', 'PORT': '5432',
        'USER': 'postgres', 'PASSWORD': 'admin',
        'DATABASE': 'shogun_db'
        }, geom=None, opacity=None, query=None
    ):
    
    from gasp.fm.psql import sql_query

    colsName = [attr_field_table,
                rgb_fields['R'], rgb_fields['G'], rgb_fields['B']]

    QUERY = query if query else 'SELECT {cols} FROM {t}'.format(
        t=table, cols=', '.join(colsName)
    )

    data = sql_query(pgsql, QUERY)

    values_colors = {
        row[0]: [row[1], row[2], row[3]] for row in data
    }

    sld = write_sld(
        attr_field_source, values_colors, sld_path,
        geometry=geom, opacity=opacity
    )

    return sld


def write_raster_sld(attrProp, outSld, dataType="CATEGORICAL"):
    """
    Write a SLD for a raster with categorical values
    
    attrProp = {
        raster_value : {"COLOR" : hex, "LABEL" : some_label},
        ...
    }
    
    OR
    attrProp = {
        raster_value : {
            "COLOR" : (red value, green_value, blue_value),
            "LABEL" : some_label
        },
        ...
    }
    
    dataType Options:
    * CATEGORICAL;
    * FLOATING;
    """
    
    from gasp.Xml import write_xml_tree
    from gasp import rgb_to_hex
    
    # SLD Basic Structure
    sldRoot = (
        'sld:StyledLayerDescriptor', 'xmlns', 'http://www.opengis.net/sld',
        'xmlns:sld', 'http://www.opengis.net/sld',
        'xmlns:gml', 'http://www.opengis.net/gml',
        'xmlns:ogc', 'http://www.opengis.net/ogc',
        'version', '1.0.0'
    )
    
    # Create a propor dict with style options for every value
    attrStyleOptions = {}
    RASTER_VALUES = attrProp.keys()
    RASTER_VALUES.sort()
    rules_Order = []
    i = 1
    for k in RASTER_VALUES:
        # Get Color Value
        if type(attrProp[k]["COLOR"]) == list or type(attrProp[k]["COLOR"]) == tuple:
            r, g, b = attrProp[k]["COLOR"]
            hex_color = rgb_to_hex(r, g, b)
        else:
            hex_color = str(attrProp[k]["COLOR"])
        
        # Get Opacity Value
        if "OPACITY" in attrProp[k]:
            opacity = str(attrProp[k]["OPACITY"])
        else:
            opacity = "1.0"
        
        so =  (
            "sld:ColorMapEntry", "color", hex_color,
            "opacity", opacity, "quantity", str(k),
            "label", str(attrProp[k]["LABEL"])
        )
        attrStyleOptions[so] = ''
        rules_Order.append(so)
        i += 1
    
    # Get Type of Color Ramp
    TYPE_PALETE = 'ramp' if dataType == "FLOATING" else 'values' 
    
    # Create SLD Tree
    sldTree = {
        sldRoot : {
            'sld:UserLayer' : {
                'sld:LayerFeatureConstraints': {
                    'sld:FeatureTypeConstraint': ''
                },
                'sld:UserStyle' : {
                    'sld:Name'      : 'Default Styler',
                    'sld:IsDefault' : '1',
                    'sld:FeatureTypeStyle': {
                        'sld:Rule' : {
                            'sld:RasterSymbolizer' : {
                                ('sld:ColorMap', 'type', TYPE_PALETE) : attrStyleOptions
                            }
                        }
                    }
                }
            }
        }
    }
    
    sldOrder = {
        sldRoot         : ['sld:UserLayer'],
        'sld:UserLayer' : ['sld:LayerFeatureConstraints', 'sld:UserStyle'],
        'sld:UserStyle' : ['sld:Name', 'sld:IsDefault', 'sld:FeatureTypeStyle'],
        ('sld:ColorMap', 'type', TYPE_PALETE)  : rules_Order
    }
    # Write SLD file
    write_xml_tree(sldTree, outSld, nodes_order=sldOrder)
    
    return outSld

