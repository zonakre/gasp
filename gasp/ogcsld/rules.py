"""
Get Rules for SLD
"""


def get_categorical_rules(attr_val_color, attr_name, geometry,
                          transparency):
    """
    Get Rules for categorical data
    """
    
    from gasp  import idcolor_to_hex
    from .symb import get_sld_geom_symbolizer

    sldRules = {}
    nr_rules = 1

    for value in attr_val_color:
        color = attr_val_color[value]
        __hex = idcolor_to_hex(color)

        __stroke = idcolor_to_hex(attr_val_color[value]['STROKE']) \
            if 'STROKE' in attr_val_color[value] else None
        
        __width = attr_val_color[value]['STROKE']['width'] if 'STROKE' in \
            attr_val_color[value] and \
            'width' in attr_val_color[value]['STROKE'] else None

        sldRules[(nr_rules, 'sld:Rule')] = {
            'sld:Name'   : 'rule{}'.format(str(nr_rules)),
            'sld:Title'  : unicode(value, 'utf-8'),
            'ogc:Filter' : {
                'ogc:PropertyIsEqualTo' : {
                    'ogc:PropertyName': str(attr_name),
                    'ogc:Literal'     : unicode(value, 'utf-8')
                }
            }
        }

        sldRules[(nr_rules, 'sld:Rule')].update(
            get_sld_geom_symbolizer(
                geometry, __hex, opacity=transparency,
                polyStroke=__stroke,
                strokeWidth=__width 
            )
        )

        nr_rules += 1

    return sldRules


def get_quantitative_rules(colorIntervals, attr_name, geometry,
                           transparency):
    """
    Get Rules for quantitative data
    """

    from gasp  import idcolor_to_hex
    from .symb import get_sld_geom_symbolizer

    sldRules = {}
    nr_rules = 1

    for cls in colorIntervals:
        # Convert RGB to HEX
        __hex = idcolor_to_hex(colorIntervals[cls])

        # Convert Stroke RGB to HEX
        __stroke = idcolor_to_hex(colorIntervals[cls]['STROKE']) \
            if 'STROKE' in colorIntervals[cls] else None
        
        __width = colorIntervals[cls]['STROKE']['width'] if 'STROKE' in \
            colorIntervals[cls] and \
            'width' in colorIntervals[cls]['STROKE'] else None
        
        if cls == 1:
            first_hex = __hex
            first_stroke = __stroke
            first_with = __width

        # Create rule tree
        sldRules[(nr_rules, 'sld:Rule')] = {
            'sld:Name'   : 'rule{}'.format(str(nr_rules)),
            'sld:Title'  : '{}..{}'.format(
                str(colorIntervals[cls]['min']),
                str(round(colorIntervals[cls]['max'], 2))
                ),
            'ogc:Filter' : {
                'ogc:And' : {
                    'ogc:PropertyIsGreaterThan' : {
                        'ogc:PropertyName' : str(attr_name),
                        'ogc:Literal'      : str(colorIntervals[cls]['min'])
                        },
                    'ogc:PropertyIsLessThanOrEqualTo' : {
                        'ogc:PropertyName' : str(attr_name),
                        'ogc:Literal'      : str(colorIntervals[cls]['max'])
                    }
                }
            }
        }

        sldRules[(nr_rules, 'sld:Rule')].update(
            get_sld_geom_symbolizer(
                geometry, __hex, opacity=transparency,
                polyStroke=__stroke,
                strokeWidth=__width
            )
        )

        nr_rules += 1
    
    sldRules[(nr_rules, 'sld:Rule')] = {
        'sld:Name'   : 'rule{}'.format(str(nr_rules)),
        'sld:Title'  : 'minimum',
        'ogc:Filter' : {
            'ogc:PropertyIsEqualTo' : {
                'ogc:PropertyName' : str(attr_name),
                'ogc:Literal'      : str(colorIntervals[1]['min'])
            }
        }
    }
    
    sldRules[(nr_rules, 'sld:Rule')].update(
        get_sld_geom_symbolizer(
            geometry, first_hex, opacity=transparency,
            polyStroke=first_stroke,
            strokeWidth=first_with
        )
    )

    return sldRules

