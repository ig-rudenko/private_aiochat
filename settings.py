import sys
import pathlib
import logging

BASE_DIR = pathlib.Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

HOST = '0.0.0.0'
PORT = '8080'

REDIS_CON = 'localhost', 6379

DEBUG = True

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
logger.addHandler(console)


TESTING = 'nosetests' in sys.argv[0]


try:
    from settings_local import *  # noqa
except ImportError:
    pass
