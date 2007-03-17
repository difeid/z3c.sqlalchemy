##########################################################################
# z3c.sqlalchemy - A SQLAlchemy wrapper for Python/Zope
#
# (C) 2007, Haufe-Mediengruppe, Freiburg, Germany
# (C) 2007, ZOPYX Ltd. & Co. KG, Tuebingen, Germany
# 
# Published under der Zope Public License V 2.1 
##########################################################################


import sys
import threading

import sqlalchemy

from zope.interface import implements

from z3c.sqlalchemy.interfaces import ISQLAlchemyWrapper
from z3c.sqlalchemy.base import BaseWrapper

from zope_mixin import ZopeMixin

class PythonPostgresWrapper(BaseWrapper):

    implements(ISQLAlchemyWrapper)

    def findDependentTables(self, schema='public', ignoreErrors=False):
        """ Returns a mapping tablename -> [list of referencing table(names)].
            ATT: this method is specific to Postgres databases!
            ATT: This method is limited to a particular schema.
        """

        if not hasattr(_cache, 'ref_mapping'):
            
            d = {}
            db = self._engine
            rs = db.execute("select * from pg_tables where schemaname = '%s'" % schema)

            for row in rs: 
                tablename = row.tablename

                try:
                    table = sqlalchemy.Table(tablename, db, autoload=True)
                except KeyError:
                    if ignoreErrors:
                        print >>sys.stderr, 'Can\'t load table %s' % tablename
                        continue
                    else: 
                        raise
                    
                for c in table.c:
                    fk = c.foreign_key
                    if fk is not None:

                        ref_by_table = fk.column.table
                        ref_by_table_name = ref_by_table.name

                        if not d.has_key(ref_by_table_name):
                            d[ref_by_table_name] = list()

                        if not tablename in d[ref_by_table_name]:
                            d[ref_by_table_name].append(tablename)

            _cache.ref_mapping = d

        return _cache.ref_mapping


class ZopePostgresWrapper(PythonPostgresWrapper, ZopeMixin):
    """ A wrapper to be used from within Zope. It connects
        the session with the transaction management of Zope.
    """

