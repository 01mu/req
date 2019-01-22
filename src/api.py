#
# api
# github.com/01mu
#

import urllib2
import sys
import requests
import os
import json
import ast

COOKIE_ROOT = 'cookies/'

class group:
    ''' group of routes referenced by a name '''
    def __init__(self, name):
        self.name = name
        self.routes = []
        self.cookies = {}

        self.get_cookies()

    def get_cookies(self):
        ''' get cookies for group to be sent for every group route request '''
        cookie_count = 0
        cookie_dir = COOKIE_ROOT + self.name + '/'

        if not os.path.exists(cookie_dir):
            os.makedirs(cookie_dir)

        cookie_files = os.listdir(cookie_dir)

        for cookie_name in cookie_files:
            cookie = open(cookie_dir + cookie_name, 'r').read()

            if cookie_name not in self.cookies.iterkeys():
                self.cookies[cookie_name] = cookie
                cookie_count = cookie_count + 1

        self.cookie_count = cookie_count

class route:
    ''' route consisting of a request type, url, and parameter dict '''
    def __init__(self, group, route_str):
        ''' init route with group name and rotue string from file '''
        self.route_str = route_str
        self.group = group
        self.fix()

    def fix(self):
        ''' set short, request type, url, and params from file '''
        split = self.route_str.split('|')

        self.short = split[1]
        self.type = split[2]
        self.url = split[3]

        if len(split[4]) > 0:
            header = split[4].replace('\n', '')
            self.header = ast.literal_eval(header)
        else:
            self.header = ''

        if len(split[5]) > 0:
            params = split[5].replace('\n', '')
            self.params = ast.literal_eval(params)
        else:
            self.params = ''

        if self.short not in short.iterkeys():
            short[self.short] = self
        else:
            print 'Duplicate short found.'
            sys.exit()

def get_routes_from_file():
    ''' get routes from rotes file '''
    with open('routes', 'r') as fl:
        for data in fl:
            data = data.replace('\n', '')
            split = data.split('|')
            group_name = split[0]

            if group_name not in groups.iterkeys():
                groups[group_name] = group(group_name)

            new_route = route(group_name, data)
            groups[group_name].routes.append(new_route)

def display_routes():
    ''' show routes '''
    for key in groups:
        print ("----------------------------------------"
            "----------------------------------------")
        print (key + ' (' + str(groups[key].cookie_count) + ' cookies)'
            "\n----------------------------------------"
            "----------------------------------------")

        for route in groups[key].routes:
            print route.short + ' | ' +  route.type + ' | ' + route.url
            print 'header: ' + str(route.header)
            print 'params: ' + str(route.params)
            print ''

def execute(name, short):
    ''' execute route and return result '''
    if len(name) == 0 or name not in short:
        return

    route = short[name]
    direct = COOKIE_ROOT + route.group

    print 'Loading "' + name + '"...'
    print ("----------------------------------------"
        "----------------------------------------")

    if route.type == 'GET':
        request = requests.get(url = route.url,
            params = route.params,
            cookies = groups[route.group].cookies)
    elif route.type == 'POST':
        request = requests.post(url = route.url,
            params = route.params,
            cookies = groups[route.group].cookies)

    cookies = request.cookies.get_dict()

    try:
        parsed = json.loads(request.text)
        print(json.dumps(parsed, indent=4, sort_keys=True))
    except ValueError, e:
        print request.text

    print ''

    for key in cookies:
        print '[cookie "' + key + '" added to "' + route.group + '"]'
        f = open(direct + '/' + key, 'w')
        f.write(cookies[key])

    raw_input()

if not os.path.exists('cookies'):
    os.makedirs('cookies')

while 1:
    groups = {}
    short = {}

    get_routes_from_file()
    display_routes()

    print ("----------------------------------------"
        "----------------------------------------")
    print '[enter route key]'
    execute(raw_input(), short)
