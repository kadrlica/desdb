desdb
=====

DES file locations and database access

Preparation
-----------
Put your des database username and password in a file ~/.desdb_pass

    username
    pass

And make sure the file is not readable or writable to others

    chmod go-rw ~/.desdb_pass

Generic Queries
---------------

After installation, the script des-query will be in your path.  You
can send queries on standard input or via the -q option

    des-query -q query
    des-query < 

examples

    #  
Installation
------------

### dependencies 

Note you must first install the oracle libraries and the cx_Oracle python
library.  Because the official version of cx_Oracle for OSX is broken, we have
bundled a patched version in the following files. Choose the one for your
architecture.

    http://www.cosmo.bnl.gov/www/esheldon/code/misc/des-oracle-linux-x86-64-v1.tar.gz
    http://www.cosmo.bnl.gov/www/esheldon/code/misc/des-oracle-macosx-x86-64-v1.tar.gz
    http://www.cosmo.bnl.gov/www/esheldon/code/misc/des-oracle-macosx-i386-v1.tar.gz

Install with

    ./do-install directory

And follow the instructions for setting your paths.

### code install

Get the source .tar.gz file, untar the file, cd into
the created directory.  To install in the "usual" place

    python setup.py install

To install under a particular prefix

    python setup.py install --prefix=/some/directory
