import unittest
import datetime
import os
import shutil

from jsondb import utils

class testClass(object):
    """docstring for testClass"""
    def __init__(self, arg):
        self.arg = arg

class UtilsTest(unittest.TestCase):

    def test_isclass(self):
        self.assertTrue(utils.is_class(datetime.datetime))
        self.assertFalse(utils.is_class(datetime.datetime.now()))

    def test_class_path(self):
        p = utils.get_table_name('db', datetime.datetime)
        self.assertEquals(p, os.path.sep.join(('db', 'datetime', 'datetime')) + ".json")

    def test_obj_path(self):
        p = utils.get_table_name('db', datetime.datetime.now())
        self.assertEquals(p, os.path.sep.join(('db', 'datetime', 'datetime')) + ".json")

    def test_makepath(self):
        path = 'hello/world/hello'
        self.assertFalse(os.path.exists(path))
        utils.make_path(path)
        self.assertTrue(os.path.exists(path))
        shutil.rmtree(path)



