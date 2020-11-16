from os.path import dirname, realpath, join, abspath
import os
import psycopg2
from psycopg2 import extras
import yaml


APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
#print('templates dir', TEMPLATES_DIR)

STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')
#print('static dir', STATIC_DIR)


LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

DGGS_PID_PREFIX = 'ec2-13-238-161-97-ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/'

# get db conn settings from yaml file
directory = os.path.dirname(os.path.realpath(__file__))
file = os.path.join(directory, "secrets.yml")
DB_CON_DICT = yaml.safe_load(open(file))
print('dbcon', DB_CON_DICT)


if DB_CON_DICT is None:
    print('You must set up a secrets.yml file containing the DB login credentials')
    exit()


def db_select(q):
    print('q', q)
    try:
        conn = psycopg2.connect(**DB_CON_DICT['db_con'])
        print('con', conn)

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(q)
        return cur.fetchall()
    except Exception as e:
        print(e)
