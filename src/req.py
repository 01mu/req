#
# req
# github.com/01mu
#

import urllib2
import sys
import requests
import os
import json
import ast
import glob
import errno

from base import base

dir_path = os.path.dirname(os.path.realpath(__file__))

COOKIE_ROOT = dir_path + '/cookies'
ROUTES_FILE = dir_path + '/res/routes'
TEST_FILE = dir_path + '/res/test'

base = base(COOKIE_ROOT, ROUTES_FILE, TEST_FILE)

while 1:
    base.line()

    for i in range(int(base.columns) / 2 - 5):
        sys.stdout.write(' ')
        sys.stdout.flush()

    print '\033[1m[req]\033[0;0m'
    base.get_routes_from_file()
    base.display_routes()
    base.line()
    print 'type \'cmds\' for commands'
    base.get_command(raw_input())
    base.short.clear()
    base.groups.clear()
