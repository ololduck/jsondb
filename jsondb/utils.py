import os

def is_class(obj):
    return obj.__class__ == type

def get_table_name(dbpath, obj):
    """
    returns the path to the table containing
    objects of type obj. obj may be an instance
    or a class.
    """
    if(is_class(obj)):
        #this is a class
        return os.path.sep.join((dbpath, obj.__module__, obj.__name__)) + ".json"
    else:
        #this is an object
        return get_table_name(dbpath, obj.__class__)
