from os.path import dirname, realpath, join, abspath
import os
import psycopg2
from psycopg2 import extras
import yaml

#
#
APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')
#
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True
#

