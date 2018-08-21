"""
SQLITE Python tools
"""

def alchemy_eng(database):
    """
    Return Alchemy Engine for SQLITE
    """
    
    from gasp.oss   import os_name
    from sqlalchemy import create_engine
    
    if os_name() == 'Windows':
        constr = r'sqlite:///{}'.format(database)
    else:
        constr = 'sqlite:///{}'.format(database)
    
    return create_engine(constr)

