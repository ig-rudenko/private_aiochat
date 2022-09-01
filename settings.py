import sys
import pathlib
import logging

BASE_DIR = pathlib.Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

HOST = '0.0.0.0'
PORT = '8080'
