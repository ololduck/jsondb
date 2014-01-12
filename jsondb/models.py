# -*- coding:utf8 -*-

import os
import json

from jsondb import logger
from jsondb import utils
class JSONdb(object):
    class Filter(object):
        def __init__(self, field, expected):
            self.field = field
            self.expected = expected

        def validate(self, obj):
            if(hasattr(obj, self.field)):
                if(obj.__dict__[self.field] == self.expected):
                    return True
            return False


    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.tables = {}
        if(not os.path.exists(self.dbpath)):
            os.mkdir(self.dbpath)
        self.loaddb()

    def loaddb(self):
        def class_loader_visitor(arg, dirname, names):
            for name in names:
                with open(os.path.sep.join((dirname, name))) as f:
                    self.tables.update(
                        {'.'.join((dirname.replace(os.path.sep, '.'), name)):
                        json.loads(f.read())})

        os.walk(self.dbpath, class_loader_visitor, None)

    def save_table(self, table_name):
        logger.info("saving table {0}".format(table_name))
        utils.make_path(table_name[:table_name.rfind('/')])
        table_key = table_name.strip('.json').strip(
            self.dbpath).strip(os.path.sep).replace(os.path.sep, '.')
        logger.debug("table_key: {0}: {1}".format(table_key,
            json.dumps(self.tables.get(table_key), sort_keys=True, indent=2)))
        with open(table_name, 'w+') as f:
            f.write(json.dumps(self.tables.get(table_key),
                sort_keys=True, indent=2))

    def savedb(self):
        for key, value in self.tables.items():
            self.save_table(key.replace('.', os.path.sep), value)

    def add(self, obj):
        classpath = utils.get_classpath(obj)
        if(classpath.replace(os.path.sep, '.') not in self.tables):
            self.tables.update({classpath.replace(os.path.sep, '.'): []})
        self.tables[classpath.replace(os.path.sep, '.')].append(obj.__dict__)
        logger.debug(self.tables)
        self.save_table(utils.get_table_name(self.dbpath, obj))

    def get(self, clazz, **kwargs):
        # Here, we should use the visitor pattern, maybe?
        # Or a filter system ~=chain of responsability?
        # Yeah, filter system, let's go.
        classpath = utils.get_classpath(clazz).replace(os.path.sep, '.')
        data = self.tables[classpath]
        objects = []
        filters = []
        for field, expected in kwargs.items():
            filters.append(JSONdb.Filter(field, expected))

        def is_valid(obj):
            for filter in filters:
                if(not filter.validate(obj)):
                    return False
            return True
        for d in data:
            obj = clazz()
            obj.__dict__.update(d)
            if(is_valid(obj)):
                objects.append(obj)
        return objects


