# -*- coding:utf8 -*-

import os
import json
import random
import sys

from jsondb import logger
from jsondb import utils

class ConsistencyError(Exception):
    pass

class JSONdb(object):
    """
    Main db class.

    Instanciate with the path where the db files will be kept.

    >>> from jsondb import JSONdb
    >>> db = JSONdb('db')
    >>> class C(object):
    ...     def __init__(self, arg=None):
    ...         self.arg = arg
    ...     def __repr__(self):
    ...         return '<C: {0}>'.format(self.arg)
    ...
    >>> db.add(C("hello"))
    >>> c = db.get(C, arg="hello")
    >>> c
    [<C: hello>]
    """
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
        self._loaddb()

    def _loaddb(self):
        for root, dirs, files in os.walk(self.dbpath):
            for f in files:
                with open(os.path.sep.join((root, f))) as fil:
                    self.tables.update(
                        {'.'.join((root.replace(os.path.sep, '.'), f)):
                        json.loads(fil.read())})

    def _save_table(self, table_name):
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
            self._save_table(key.replace('.', os.path.sep))

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
        """
        Adds a object to the DB.

        The class defining the model must be a new-style class, ie.:
        class C(object):
            def __init__(self):
                pass

        Moreover, We need the object to be built with no arguments,
        ie. no required arguments on the class' __init__. Working on that.
        """
        logger.debug("adding object {0}".format(obj.__dict__))
        classpath = utils.get_classpath(obj)
        outcasts = self._check_if_obj_has_not_primitive_fields(obj)
        for outcast in outcasts:
            # we need to add an id for this field, and put it on the corresponding object.
            r = random.randint(0, sys.maxint)
            obj.__dict__[outcast].__dict__['jsondb_id'] = r
            self.add(obj.__dict__[outcast])
            obj.__dict__[outcast] = "<jsondb_id:({0};{1})>".format(
                utils.get_classpath(obj.__dict__[outcast]).replace(
                    os.path.sep, '.'), r)

        if(classpath.replace(os.path.sep, '.') not in self.tables):
            self.tables.update({classpath.replace(os.path.sep, '.'): []})
        self.tables[classpath.replace(os.path.sep, '.')].append(obj.__dict__)
        logger.debug(self.tables)
        self._save_table(utils.get_table_name(self.dbpath, obj))

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
        """
        retrieve an object from db.
        The first arg is the class to instanciante and populate with db values.
        every other keyword is a 'filter', to limit the selection of db objects.

        >>> class C(object):
        ...     def __init__(self, arg=None):
        ...         self.arg = arg
        ...     def __repr__(self):
        ...         return '<C: {0}>'.format(self.arg)
        ...
        >>> c1 = C("hello1")
        >>> c2 = C("hello2")
        >>> db = JSONdb('test_db')
        >>> db.add(c1)
        >>> db.add(c2)
        >>> db.get(C)
        [<C: hello1>, <C: hello2>]
        >>> db.get(C, arg="hello1")
        [<C: hello1>]
        """
        # We need to test if we have the same id in the same table. highly unlikely, but still.
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
        logger.debug("found objects {0}, who must match {1}".format(data, filters))
        for d in data:
            logger.debug("treating object {0}".format(d))
            obj = clazz()
            obj.__dict__.update(d)
            if(is_valid(obj)):
                logger.debug("object {0} is valid!".format(obj.__dict__))
                for field in self._get_relational_fields(obj):
                    # load the object's class, and get it
                    classname = obj.__dict__[field][
                    obj.__dict__[field].find('(')+1:obj.__dict__[field].find(';')
                        ]
                    jsondb_id = int(obj.__dict__[field][
                        obj.__dict__[field].find(';')+1:obj.__dict__[field].find(')')
                        ])
                    logger.debug("obj to load: {0}:{1}".format(
                        classname, jsondb_id))
                    obj_loaded = self.get(
                        utils.class_import(classname), jsondb_id=jsondb_id)
                    if(obj_loaded == []):
                        raise ConsistencyError("We could not load field {0}\
                         of object {1}! get returned []".format(
                            field, obj.__dict__))
                    obj.__dict__[field] = obj_loaded[0]

                if('jsondb_id' in obj.__dict__):
                    del obj.__dict__['jsondb_id']
                objects.append(obj)
        return objects



