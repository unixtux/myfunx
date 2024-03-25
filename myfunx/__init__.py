#!/bin/env python3

__all__ = ('Client', 'JsonManager',)

__version__ = '0.4.5'
VERSION = __version__

from aiotgm._logging import get_logger
logger = get_logger('myfunx ' + VERSION)
del get_logger

from .client import Client
from .json_manager import JsonManager
