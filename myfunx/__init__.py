#!/bin/env python3

__all__ = ('Client', 'JsonManager',)

__version__ = '0.5.2'
VERSION = __version__

from aiotgm.logging import get_logger
logger = get_logger('myfunx ' + VERSION)
del get_logger

from .client import Client
from .json_manager import JsonManager
