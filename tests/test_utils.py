import unittest

import datetime
from jsondb import utils
import os

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



