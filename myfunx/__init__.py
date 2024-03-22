#!/bin/env python3

__all__ = ('Client', 'JsonManager', 'my_id')

__version__ = '0.2.0'
VERSION = __version__

from aiotgm.logger import get_logger
logger = get_logger('myfunx ' + VERSION)
del get_logger

my_id = 265705876
from .client import Client
from .json_manager import JsonManager
