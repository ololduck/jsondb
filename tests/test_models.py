import unittest
import os
import shutil
import json
from jsondb import models, utils

class C(object):
    def __init__(self,arg=None):
        self.arg = arg

    def sample_method(self):
        return "hello!"

    def __repr__(self):
        return u"<C: arg={0}>".format(self.arg)

class JSONdbTest(unittest.TestCase):

    def setUp(self):
        self.db = models.JSONdb('test_db')
        self.sample_data = [C("hello"), C("Hello2")]

    def tearDown(self):
        shutil.rmtree(self.db.dbpath)
        pass

    def add_some_to_db(self):
        self.db.add(self.sample_data[0])
        self.db.add(self.sample_data[1])

    def test_db_create(self):
        self.assertTrue(
            os.path.exists(self.db.dbpath) and os.path.isdir(self.db.dbpath),
            "The DB path has not been created...")

    def test_db_add(self):
        self.db.add(self.sample_data[0])
        self.assertTrue('test_models.C' in self.db.tables)
        self.assertTrue(os.path.exists(os.path.sep.join(('test_db',
            'test_models', 'C.json'))))

    def test_savedb(self):
        self.add_some_to_db()
        with open(os.path.sep.join(('test_db', 'test_models', 'C.json'))) as f:
            data = f.read()
            recovered_data = json.loads(data)
            self.assertIsNotNone(recovered_data,
                "Could not get back the json data. Corruption when saving.\nGot: \"{0}\"".format(data))

    def test_db_load(self):
        self.add_some_to_db()
        res = self.db.get(clazz=C, arg="hello")
        self.assertNotEqual(res, [])
        self.assertEqual(len(res), 1)
        print(res)
        self.assertEqual(res[0].arg, self.sample_data[0].arg)

