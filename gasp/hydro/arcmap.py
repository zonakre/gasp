"""
Hydrologic procedures
"""


def generate_waterlines(mdt, waterbodies, accumulation_value=500,
                        workspace=None):
    """
    Generate Water Bodies lines
    """
    
    import os
    from gasp.oss                      import get_fileformat
    from gasp.cpu.arcg.lyr             import rst_lyr
    from gasp.prop.ff                  import vector_formats, raster_formats
    from gasp.cpu.arcg.spanlst.algebra import rstcalc
    from gasp.cpu.arcg.spanlst.hydro   import fill
    from gasp.cpu.arcg.spanlst.hydro   import flow_accumulation
    from gasp.cpu.arcg.spanlst.hydro   import flow_direction
    from gasp.cpu.arcg.spanlst.hydro   import stream_to_feature
    
    workspace = workspace if workspace else \
        os.path.dirname(waterbodies)
    
    raster_format = os.path.splitext(os.path.basename(waterbodies))[1]
    
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True
    
    fill_rst = fill(mdt, 'flow_raster{}'.format(raster_format),
                    template=mdt)
    
    dire_rst = flow_direction(
        fill_rst, 'direction_raster{}'.format(raster_format),
        template=mdt
    )
    
    flow_acc = flow_accumulation(
        dire_rst, 'flow_raster{}'.format(raster_format),
        template=mdt
    )
    
    # Split water bodies from the other accumulation data
    lyr_flow = rst_lyr(flow_acc)
    
    outFormat = os.path.splitext(os.path.basename(waterbodies))[1]
    rstFormat = raster_formats()
    vecFormat = vector_formats()
    
    waterRst = waterbodies if outFormat in rstFormat else \
        os.path.join(
            workspace,
            os.path.splitext(os.path.basename(waterbodies))[0] + raster_format
        ) if outFormat in vecFormat else None
    
    if not waterRst:
        raise ValueError('Your output is not a raster and is not a vector')
    
    waterRst = rstcalc(
        '{r} > {a}'.format(
            r=os.path.splitext(os.path.basename(flow_acc))[0],
            a=str(accumulation_value)
        ),
        waterRst, template=mdt
    )
    
    if outFormat in vecFormat:
        stream_to_feature(waterRst, dire_rst, waterbodies)
        
        return waterbodies
    
    else:
        return waterRst

