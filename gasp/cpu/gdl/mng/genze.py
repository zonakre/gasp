"""
Generalization tools using OGR
"""

def ogr_dissolve(shp, fld, out, field_statistics=None):
    """
    Dissolve with OGR and sqlite sql
    
    field_statitics used to preserve numeric fields aggregating their values
    using some statistics
    field_statistics = {fld_name: SUM, fld_name: AVG}
    
    TODO: DISSOLVE WITHOUT FIELD
    """
    
    import os
    from gasp import exec_cmd
    
    if not field_statistics:
        cmd = (
            'ogr2ogr {o} {i} -dialect sqlite -sql '
            '"SELECT ST_Union(geometry), {f} '
            'FROM {t} GROUP BY {f};"'
        ).format(
            o=out, i=shp, f=fld,
            t=os.path.splitext(os.path.basename(shp))[0]
        )
    
    else:
        cmd = (
            'ogr2ogr {o} {i} -dialect sqlite -sql '
            '"SELECT ST_Union(geometry), {f}, {stat} '
            'FROM {t} GROUP BY {f};"'
        ).format(
            o=out, i=shp, f=fld,
            t=os.path.splitext(os.path.basename(shp))[0],
            stat=','.join(
                ['{s}({f}) AS {f}'.format(
                    f=str(fld),
                    s=field_statistics[fld]) for fld in field_statistics]
            )
        )
    
    # Execute command
    outcmd = exec_cmd(cmd)
    
    return out

