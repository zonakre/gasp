"""
Assist the module GASP with methods to process geospatial
data on PostgreSQL
"""

import psycopg2


def pgsql_special_words():
    return ['table', 'column', 'natural', 'group', 'left', 'right', 'order']


def connection(conParam):
    """
    Connect to PostgreSQL Database
    
    example - conParam = {
        "HOST" : "localhost", "USER" : "postgres",
        "PORT" : "5432", "PASSWORD" : "admin",
        "DATABASE" : "db_name"
    }
    """
    
    try:
        if "DATABASE" not in conParam:
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            c = psycopg2.connect(
                user=conParam["USER"], password=conParam["PASSWORD"],
                host=conParam["HOST"], port=conParam["PORT"]
            )
            c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
        else:
            c = psycopg2.connect(
                database=conParam["DATABASE"], user=conParam["USER"],
                password=conParam["PASSWORD"], host=conParam["HOST"],
                port=conParam["PORT"],
            )
        
        return c
    
    except psycopg2.Error as e:
        raise ValueError(str(e))


def alchemy_engine(conParam):
    """
    Get engine that could be used for pandas to import data into
    PostgreSQL
    """
    
    from sqlalchemy import create_engine
    
    return create_engine(
        'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}'.format(
            user=conParam["USER"], password=conParam["PASSWORD"],
            host=conParam["HOST"], port=conParam["PORT"],
            db=conParam["DATABASE"]
        )
    )


def run_sql_file(lnk, database, sqlfile):
    """
    Run a sql file do whatever is on that script
    """
    
    from gasp import exec_cmd
    
    cmd = 'psql -h {host} -U {usr} -p {port} -w {db} < {sql_script}'.format(
        host = lnk['HOST'], usr = lnk['USER'], port = lnk['PORT'],
        db  = database    , sql_script = sqlfile
    )
    
    outcmd = exec_cmd(cmd)

