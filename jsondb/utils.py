import os

def is_class(obj):
    """
    returns True if obj is a class, and not an object.
    Works only on new-style classes (class C(object):)

    >>> class C(object):
    ...     def __init__(self, arg):
    ...         self.arg = arg
    ...     def __repr__(self):
    ...         return '<C: {0}>'.format(self.arg)
    ...
    >>> c = C("hello")
    >>> is_class(c)
    False
    >>> is_class(C)
    True
    """
    return obj.__class__ == type

def _get_class_classpath(clazz):
    """
    returns a path to the class, effectively replacing the dots with os.path.sep
    """
    t = clazz.__module__.split('.')
    t.append(clazz.__name__)
    return os.path.sep.join(t)

def get_classpath(obj):
    """
    Returns the classpath to the class represented by obj.
    obj may be an object or a class.
    Convenience function for _get_class_classpath.

    >>> import datetime, os
    >>> get_classpath(datetime.datetime.now()).replace(os.path.sep, '/')
    'datetime/datetime'
    >>> get_classpath(datetime.datetime).replace(os.path.sep, '/')
    'datetime/datetime'
    """
    if(is_class(obj)):
        return _get_class_classpath(obj)
    else:
        return _get_class_classpath(obj.__class__)

def get_table_name(dbpath, obj):
    """
    returns the path to the table containing
    objects of type obj. obj may be an instance
    or a class.

    >>> import datetime, os
    >>> get_table_name('test_db', datetime.datetime.now()).replace(os.path.sep, '/')
    'test_db/datetime/datetime.json'
    """
    if(is_class(obj)):
        #this is a class
        return os.path.sep.join((dbpath, get_classpath(obj))) + ".json"
    else:
        #this is an object
        return get_table_name(dbpath, obj.__class__)

def make_path(path):
    paths = path.split(os.path.sep)
    done = []
    for path in paths:
        current = done + [path,]
        if(not os.path.exists(os.path.sep.join(current))):
            os.mkdir(os.path.sep.join(current))
        done.append(path)

def class_import(name):
    mod_str = name[:name.rfind('.')]
    class_str = name[name.rfind('.')+1:]
    mod = __import__(mod_str, fromlist=[class_str])
    cl = getattr(mod, class_str)
    return cl
