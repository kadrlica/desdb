#!/usr/bin/env python

import os
import sys
from sys import stdout,stderr

_defhost = 'leovip148.ncsa.uiuc.edu'
_defdb = 'dessci'
_deftype = 'oracle'
_defport = {'oracle':1521,'postgres':5432}
_defsec = 'db-dessci'

class Authenticator:
    """
    Try to get username/password from different sources.

    First there are the keywords 'user', 'password' which take precedence.

    The types to try are listed in the 'types' keyword as a list.
    Allowed types are:
       'services', 'netrc', or 'desdb_pass' (deprecated)

    'sevices' and 'netrc' are more general, and can be used for any url.
    """
    def __init__(self, user=None, password=None, 
                 types=['services','netrc','desdb_pass'], **kwargs):
        # Should use default dictionary
        self._host    = kwargs.get('host',_defhost)
        self._dbname  = kwargs.get('name',_defdb)
        self._dbtype  = kwargs.get('dbtype',_deftype)
        self._port    = kwargs.get('port',_defport[self.dbtype])
        self._section = kwargs.get('section',_defsec)

        self._types=types
        self._type=None

        self._password=None
        self._user=None

        if user is not None or password is not None:
            self._try_keywords(user=user, password=password)
            return
        
        for type in types:
            if self._set_username_password(type):
                self._type=type
                break

        if self._user==None:
            raise ValueError("could not determine "
                             "username/password for host '%s'" % self._host)

    @property
    def user(self):
        return self._user
    @property
    def password(self):
        return self._password
    @property
    def host(self):
        return self._host
    @property
    def dbname(self):
        return self._dbname
    @property
    def dbtype(self):
        return self._dbtype
    @property
    def port(self):
        return self._port
    @property
    def type(self):
        return self._type

    def _set_username_password(self, type):
        gotit=False
        if type=='netrc':
            gotit=self._try_netrc()
        elif type=='desdb_pass':
            gotit=self._try_desdb_pass()
        elif type=='services':
            gotit=self._try_services()
        else:
            raise ValueError("expected type 'netrc','services', or 'desdb_pass'")

        return gotit

    def _check_perms(self,fname):
        import stat
        fname=os.path.expanduser(fname)
        with open(fname) as fobj:
            prop = os.fstat(fobj.fileno())
            if prop.st_mode & (stat.S_IRWXG | stat.S_IRWXO):
                err=("file has incorrect mode.  On UNIX use\n"
                     "    chmod go-rw %s" % fname)
                raise IOError(err)

    def _try_netrc(self):
        import netrc

        fname = os.path.join(os.environ['HOME'], ".netrc")
        if not os.path.exists(fname):
            return False

        self._check_perms(fname)

        res=netrc.netrc().authenticators(self._host)

        if res is None:
            # no authentication is needed for this host
            return False

        (user,account,passwd) = res
        self._user=user
        self._password=passwd

        return True

    def _try_keywords(self, user=None, password=None):
        if user is None or password is None:
            raise ValueError("Send either both or neither of user "
                             "password")

        self._user=user
        self._password=password
        self._type='keyword'


    def _try_desdb_pass(self):
        """
        Old deprecated way
        """
        fname=os.path.join( os.environ['HOME'], '.desdb_pass')
        if not os.path.exists(fname):
            return False

        self._check_perms(fname)

        with open(fname) as fobj:
            data=fobj.readlines()
            if len(data) != 2:
                raise ValueError("Expected first line user second line "
                                 "pass in %s" % fname)
            self._user=data[0].strip()
            self._password=data[1].strip()

        return True

    def _try_services(self):
        """
        DES services file:
        https://deswiki.cosmology.illinois.edu/confluence/x/aoAM
        """
        import ConfigParser

        fname=os.path.join( os.environ['HOME'], '.desservices.ini')
        if not os.path.exists(fname):
            return False

        self._check_perms(fname)

        c = ConfigParser.RawConfigParser()
        c.read(fname)

        d={}
        [d.__setitem__(k,v.lower()) for (k,v) in c.items(self._section)]

        self._user = d.get('user')
        self._password = d.get('passwd')
        self._host = d.get('server')
        self._dbtype = d.get('type')
        self._dbname = d.get('name')
        if self._dbtype=='oracle'  : self._port = d.get('port',_defport['oracle'])
        if self._dbtype=='postgres': self._port = d.get('port',_defport['postgres'])
        return True

if __name__ == "__main__":
    import argparse
    description = "python script"
    parser = argparse.ArgumentParser(description=description)
    opts = parser.parse_args()
