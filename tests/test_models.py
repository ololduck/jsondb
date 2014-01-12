import unittest
import os
from jsondb import models

class C(object):
    def __init__(self,arg):
        self.arg = arg

class JSONdbTest(unittest.TestCase):

    def setUp(self):
        self.db = models.JSONdb('db')
        self.sample_data = [C("hello"), C("Hello2")]

    def add_some_to_db(self):
        self.db.add(self.sample_data[0])
        self.db.add(self.sample_data[1])

    def test_db_create(self):
        self.assertTrue(
            os.path.exists(self.db.dbpath) and os.path.isdir(self.db.dbpath),
            "The DB path has not been created...")

    def test_db_load(self):
        self.add_some_to_db()
        self.assertIsNotNone(self.db.get(C))
