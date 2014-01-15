# -*- coding:utf8 -*-

import os
import json
import random
import sys

from jsondb import logger
from jsondb import utils

class JSONdb(object):
    class Filter(object):
        def __init__(self, field, expected):
            self.field = field
            self.expected = expected

        def __repr__(self):
            return '<Filter: {0}=={1}>'.format(self.field, self.expected)

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
        for root, dirs, files in os.walk(self.dbpath):
            for f in files:
                with open(os.path.sep.join((root, f))) as fil:
                    self.tables.update(
                        {'.'.join((root.replace(os.path.sep, '.'), f)):
                        json.loads(fil.read())})

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

    def _check_if_obj_has_not_primitive_fields(self, obj):
        '''
        >>> class C(object):
        ...     def __init__(self, arg):
        ...         self.arg = arg
        ...     def __repr__(self):
        ...         return '<C: {0}>'.format(self.arg)
        ...
        >>> c = C("hello")
        >>> d = C(c)
        >>> db = JSONdb('test_db')
        >>> db._check_if_obj_has_not_primitive_fields(c)
        []
        >>> db._check_if_obj_has_not_primitive_fields(d)
        ['arg']
        '''
        outcasts = []
        for key, value in obj.__dict__.items():
            if(type(value) not in (int, float, bool, dict, list, str)):
                # the it is not a primitive type
                outcasts.append(key)
        return outcasts

    def add(self, obj):
        logger.debug("adding object {0}".format(obj.__dict__))
        classpath = utils.get_classpath(obj)
        outcasts = self._check_if_obj_has_not_primitive_fields(obj)
        for outcast in outcasts:
            # we need to add an id for this field, and put it on the corresponding object.
            r = random.randint(0, sys.maxint)
            obj.__dict__[outcast].__dict__['jsondb_id'] = r
            self.add(obj.__dict__[outcast])
            obj.__dict__[outcast] = "<jsondb_id:({0};{1})>".format(utils.get_classpath(obj.__dict__[outcast]).replace(os.path.sep, '.'), r)

        if(classpath.replace(os.path.sep, '.') not in self.tables):
            self.tables.update({classpath.replace(os.path.sep, '.'): []})
        self.tables[classpath.replace(os.path.sep, '.')].append(obj.__dict__)
        logger.debug(self.tables)
        self.save_table(utils.get_table_name(self.dbpath, obj))

    def _get_relational_fields(self, obj):
        '''
        >>> class C(object):
        ...     def __init__(self, arg):
        ...         self.arg = arg
        ...     def __repr__(self):
        ...         return '<C: {0}>'.format(self.arg)
        ...
        >>> c = C("<jsondb_id:(test.path.C;146546)>")
        >>> d = C(c)
        >>> db = JSONdb('test_db')
        >>> db._get_relational_fields(c)
        ['arg']
        >>> db._get_relational_fields(d)
        []
        '''
        fields = []
        for key, value in obj.__dict__.items():
            if(type(value) == str and value.startswith("<jsondb_id:(")):
                # then it is another object, and we need to load it
                fields.append(key)
        return fields

    def get(self, clazz, **kwargs):
        # Here, we should use the visitor pattern, maybe?
        # Or a filter system ~=chain of responsability?
        # Yeah, filter system, let's go.
        classpath = utils.get_classpath(clazz).replace(os.path.sep, '.')
        if(classpath not in self.tables):
            return []
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
            if('jsondb_id' in d):
                del d['jsondb_id']
            obj = clazz()
            obj.__dict__.update(d)
            if(is_valid(obj)):
                for field in self._get_relational_fields(obj):
                    # load the object's class, and get it
                    pass
                objects.append(obj)
        return objects

    def relget(self, clazz, **kwargs):
        return []


