#!/usr/bin/env python
import cx_Oracle, psycopg2
from psycopg2.extensions import connection as pgConnection

# This is essentially PasswordGetter but modified to take services
# file if available.
from auth import Authenticator

class BaseConnection(object):
    def __init__(self, **keys):
        p=Authenticator(**keys)
        self._pwd_getter=p
        self._port = keys.get('port',p.port)
        self._dbname = keys.get('port',p.dbname)

class OracleConnection(BaseConnection,cx_Oracle.Connection):
    """ Oracle Connection object """

    _url_template = "%s:%s/%s"

    def __init__(self, **kwargs):
        super(OracleConnection,self).__init__(**kwargs)
        p = self._pwd_getter
        url = self._url_template%(p.host, self._port, self._dbname)
        cx_Oracle.Connection.__init__(self,p.user,p.password,url)

class PostgresConnection(BaseConnection,pgConnection):
    """ Postgres Connection object """

    _url_template = 'host=%s dbname=%s user=%s password=%s port=%s'

    def __init__(self, **kwargs):
        super(PostgresConnection,self).__init__(**kwargs)
        p = self._pwd_getter
        url = self._url_template%(p.host,p.dbname,p.user,p.password,p.port)
        pgConnection.__init__ (self, url)

class Connection(object):
    def __init__(self, **kwargs):
        p = Authenticator(**kwargs)
        if p.dbtype=='oracle':
            self.conn = OracleConnection(**kwargs)
        elif p.dbtype=='postgres':
            self.conn = PostgresConnection(**kwargs)
        else:
            msg = "Unrecognized db type: %s"%self._auth.dbtype
            raise TypeError
        
    def __getattr__(self,name):
        # Return 'value' of parameters
        # __getattr__ tries the usual places first.
        return self.conn.__getattr__(name)

### class Connection2(OracleConnection,PostgresConnection):
###     pass
###  
### This would be ideal, but raises 
### TypeError: Error when calling the metaclass bases
###     multiple bases have instance lay-out conflict
### Due to differing C layouts for psyopg2 and cx_oracle

