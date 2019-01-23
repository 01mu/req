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

COOKIE_ROOT = 'cookies'
ROUTES_FILE = 'res/routes'

rows, columns = os.popen('stty size', 'r').read().split()

class group:
    def __init__(self, name):
        self.name = name
        self.routes = []
        self.cookies = {}
        self.get_cookies()

    def remove_group(self):
        temp = short.copy()

        for route in temp.iterkeys():
            if short[route].group == self.name:
                del short[route]

        update_file()

    def set_name(self, new_name):
        for route in short.iterkeys():
            if short[route].group == self.name:
                short[route].group = new_name

        try:
            cookie_dir = COOKIE_ROOT + '/'
            os.rename(cookie_dir + self.name, cookie_dir + new_name)
        except OSError, e:
            print ('cookies from "' + self.name + '" will not be ' +
                'transferred to "' + new_name + '"')
            raw_input()

        update_file()

    def write_cookies(self, request):
        cookies = request.cookies.get_dict()

        for key in cookies:
            print '"' + key + '" added to "' + self.name + '"'
            f = open(COOKIE_ROOT + '/' + self.name + '/' + key, 'w')
            f.write(cookies[key])

    def show_cookies(self):
        for key in self.cookies.iterkeys():
            print key + ': ' + self.cookies[key] + '\n'

    def clear_cookies(self):
        cookie_dir = COOKIE_ROOT + '/' + self.name + '/*'
        files = glob.glob(cookie_dir)

        for f in files:
            os.remove(f)

    def get_cookies(self):
        cookie_count = 0
        cookie_dir = COOKIE_ROOT + '/' + self.name + '/'

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
    def __init__(self, group, route_str):
        self.route_str = route_str
        self.group = group
        self.fix()

    def set(self, which, edit):
        if len(edit) == 0:
            return

        if which == 'url':
            self.url = edit
        elif which == 'name':
            self.short = edit
        elif which == 'group':
            self.group = edit
        else:
            self.type = edit

        update_file()

    def edit(self, which, edit):
        if edit == '{}':
            if which == 'header':
                self.header.clear()
            else:
                self.params.clear()

            update_file()
            return

        new = edit.split(',')

        for n in new:
            a = n.split(':')

            if len(a) > 1:
                if which == 'header':
                    if len(a[1]) == 0:
                        del self.header[a[0]]
                    else:
                        self.header[a[0]] = a[1]
                else:
                    if len(a[1]) == 0:
                        del self.params[a[0]]
                    else:
                        self.params[a[0]] = a[1]

        update_file()

    def fix(self):
        split = self.route_str.split('|')
        self.short = split[1]
        self.type = split[2]
        self.url = split[3]

        if split[4] != '{}':
            header = split[4].replace('\n', '')
            self.header = ast.literal_eval(header)
        else:
            self.header = {}

        if split[5] != '{}':
            params = split[5].replace('\n', '')
            self.params = ast.literal_eval(params)
        else:
            self.params = {}

        if self.short not in short.iterkeys():
            short[self.short] = self
        else:
            print 'duplicate short found: "' + self.short + '"'
            sys.exit()

def get_routes_from_file():
    with open(ROUTES_FILE, 'r') as fl:
        for data in fl:
            if len(data) > 1:
                data = data.replace('\n', '')
                split = data.split('|')
                group_name = split[0]

                if group_name not in groups.iterkeys():
                    groups[group_name] = group(group_name)

                new_route = route(group_name, data)
                groups[group_name].routes.append(new_route)

def display_routes():
    for key in groups:
        groups[key].routes.sort(key=lambda x: x.short, reverse=False)

        r_str = ('\033[1m[' + key + ']\033[0;0m (' +
            str(groups[key].cookie_count) + ' cookies, ' +
            str(len(groups[key].routes)) + ' routes)')

        text_header(r_str)

        for route in groups[key].routes:
            print ('\033[1m[' + route.short + ']\033[0;0m | ' +
                route.type + ' | ' + route.url)
            print 'header: ' + str(route.header)
            print 'params: ' + str(route.params)
            print ''

def execute(name, short):
    if len(name) == 0 or name not in short:
        return

    route = short[name]
    group = groups[route.group]

    print 'Loading "' + name + '"...'

    if route.type == 'GET':
        request = requests.get(url = route.url,
            params = route.params,
            cookies = group.cookies)
    elif route.type == 'POST':
        request = requests.post(url = route.url,
            params = route.params,
            cookies = group.cookies)

    headers = request.headers
    text_header('[response]')

    try:
        parsed = json.loads(request.text)
        print(json.dumps(parsed, indent=4, sort_keys=True))
    except ValueError, e:
        print request.text

    text_header('[stats]')

    print ('status code: ' + str(request.status_code) +
        ', time: ' + str(request.elapsed.total_seconds()) + ' seconds, ' +
        'size: ' + (str(len(request.content)/float(1 << 10)) + ' KB'))

    text_header('[headers]')

    for key in headers.iterkeys():
        print key + ': ' + headers[key]

    text_header('[cookies]')
    group.write_cookies(request)
    raw_input()

def line():
    for i in range(int(columns)):
        sys.stdout.write('-')
        sys.stdout.flush()

def text_header(text):
    line()
    print '\033[1m' + text + '\033[0;0m'
    line()

def get_command(cmd):
    cmds = cmd.split(' ')

    if cmds[0] == 'cookies' and cmds[1] == 'show' and len(cmds) == 3:
        show_cookies(cmds[2])
    elif cmds[0] == 'cookies' and cmds[1] == 'clear' and len(cmds) == 3:
        clear_cookies(cmds[2])
    elif len(cmds) == 3 and cmds[1] == 'url':
        if cmds[0] in short:
            short[cmds[0]].set('url', cmds[2])
    elif len(cmds) == 3 and cmds[1] == 'name':
        if cmds[0] in short:
            short[cmds[0]].set('name', cmds[2])
    elif len(cmds) == 3 and cmds[1] == 'type':
        if cmds[0] in short:
            short[cmds[0]].set('type', cmds[2])
    elif len(cmds) == 3 and cmds[1] == 'group':
        if cmds[0] in short:
            short[cmds[0]].set('group', cmds[2])
    elif len(cmds) == 3 and cmds[1] == 'header':
        if cmds[0] in short:
            short[cmds[0]].edit('header', cmds[2])
    elif len(cmds) == 3 and cmds[1] == 'params':
        if cmds[0] in short:
            short[cmds[0]].edit('params', cmds[2])
    elif cmds[0] == 'cmds':
        print '\n<route> | make http request\n'
        print '<route> url <url> | set route url'
        print '<route> name <name> | set route name'
        print '<route> type <type> | set route type'
        print '<route> type <group> | set route group'
        print '<route> header {...} | set route header, \'{}\' to clear'
        print '<route> params {...} | set route params, \'{}\' to clear\n'
        print 'cookies show <group> | show cookies for group'
        print 'cookies clear <group> | clear cookies for group\n'
        print 'route add <group> <route> <type> <url> | add new route'
        print 'route remove <route> | remove route\n'
        print 'group name <group> <name> | set group name'
        print 'group remove <group> | remove group and all associated routes'
        raw_input()
    elif len(cmds) == 4 and cmds[0] == 'group' and cmds[1] == 'name':
        if cmds[2] in groups.iterkeys():
            groups[cmds[2]].set_name(cmds[3])
    elif len(cmds) == 3 and cmds[0] == 'group' and cmds[1] == 'remove':
        if cmds[2] in groups.iterkeys():
            groups[cmds[2]].remove_group()
    elif len(cmds) == 6 and cmds[0] == 'route' and cmds[1] == 'add':
        add_route(cmds)
    elif len(cmds) == 3 and cmds[0] == 'route'  and cmds[1] == 'remove':
        if cmds[2] in short:
            del short[cmds[2]]
            update_file()
    else:
        execute(cmd, short)

def update_file():
    f = open(ROUTES_FILE, "w")

    for route in short:
        r = short[route]
        f.write((r.group + '|' + r.short + '|' + r.type + '|' +
            r.url + '|' + str(r.header) + '|' + str(r.params) + '\n'))

def add_route(cmds):
    group = cmds[2]
    sh = cmds[3]
    req_type = cmds[4]
    url = cmds[5]

    for value in cmds:
        if len(value) == 0:
            return

    if sh in short.iterkeys():
        print 'duplicate short found: "' + sh + '"'
        raw_input()
        return

    f = open(ROUTES_FILE, "a")
    f.write((group + '|' + sh + '|' + req_type + '|' +
        url + '|{}|{}\n'))

def show_cookies(group):
    line()

    if group not in groups.iterkeys():
        return

    groups[group].show_cookies()
    raw_input()

def clear_cookies(group):
    line()

    if group not in groups.iterkeys():
        return

    print (str(groups[group].cookie_count) + ' cookies cleared for "' +
        group + '"')

    groups[group].clear_cookies()
    raw_input()

if not os.path.exists(COOKIE_ROOT):
    os.makedirs(COOKIE_ROOT)

if not os.path.exists(os.path.dirname(ROUTES_FILE)):
    try:
        os.makedirs(os.path.dirname(ROUTES_FILE))

        with open(ROUTES_FILE, "w") as f:
            f.write('')
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

while 1:
    groups = {}
    short = {}
    line()

    for i in range(int(columns) / 2 - 5):
        sys.stdout.write(' ')
        sys.stdout.flush()

    print '\033[1m[req]\033[0;0m'
    get_routes_from_file()
    display_routes()
    line()
    print 'type \'cmds\' for commands'
    get_command(raw_input())
