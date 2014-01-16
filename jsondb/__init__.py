__version__ = '0.0.2+beta.0'

import logging

logger = logging.getLogger('jsondb')

import utils
from .models import JSONdb, ConsistencyError
