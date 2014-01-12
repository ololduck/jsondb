# -*- coding:utf8 -*-

import os

from jsondb import logger

class JSONdb(object):
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.tables = {}
        if(not os.path.exists(self.dbpath)):
            os.mkdir(self.dbpath)
        # maybe we should load all classes?

    def loaddb(self):
        for f in os.walk(self.dbpath):
            logger.debug(f)

    def add(self, obj_or_class):
        pass

    def get(self, *args, **kwargs):
        pass

