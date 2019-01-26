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

from group import group
from route import route
from test import test

class base:
    #
    # initiate base with locations of needed files, create them if they do
    # not exist, and initialize groups and routes dicts
    #
    def __init__(self, COOKIE_ROOT, ROUTES_FILE, TEST_FILE):
        self.groups = {}
        self.short = {}

        self.COOKIE_ROOT = COOKIE_ROOT
        self.ROUTES_FILE = ROUTES_FILE
        self.TEST_FILE = TEST_FILE

        self.rows, self.columns = os.popen('stty size', 'r').read().split()

        if not os.path.exists(self.COOKIE_ROOT):
            os.makedirs(self.COOKIE_ROOT)

        if not os.path.exists(os.path.dirname(self.ROUTES_FILE)):
            try:
                os.makedirs(os.path.dirname(self.ROUTES_FILE))

                with open(self.ROUTES_FILE, "w") as f:
                    f.write('')
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

    #
    # split each route from the routes file and assign the contents to the
    # groups and routes dicts
    #
    def get_routes_from_file(self):
        with open(self.ROUTES_FILE, 'r') as fl:
            for data in fl:
                if len(data) > 1:
                    data = data.replace('\n', '')
                    split = data.split('|')
                    group_name = split[0]

                    if group_name not in self.groups.iterkeys():
                        self.groups[group_name] = (group(group_name,
                            self.COOKIE_ROOT))

                    new_route = route(group_name, data, self.short)
                    self.groups[group_name].routes.append(new_route)

    #
    # display routes ordered by name and seperated by group
    #
    def display_routes(self):
        for key in self.groups:
            self.groups[key].routes.sort(key=lambda x: x.short, reverse=False)

            r_str = ('\033[1m[' + key + ']\033[0;0m (' +
                str(self.groups[key].cookie_count) + ' cookies, ' +
                str(len(self.groups[key].routes)) + ' routes)')

            self.text_header(r_str)

            for route in self.groups[key].routes:
                print ('\033[1m[' + route.short + ']\033[0;0m | ' +
                    route.type + ' | ' + route.url)
                print 'header: ' + str(route.header)
                print 'params: ' + str(route.params)
                print ''

    #
    # print the contents of an http request
    #
    def print_request(self, request, group):
        headers = request.headers
        self.text_header('[response]')

        try:
            parsed = json.loads(request.text)
            print(json.dumps(parsed, indent=4, sort_keys=True))
        except ValueError, e:
            print request.text

        self.text_header('[stats]')

        print ('status code: ' + str(request.status_code) +
              ', time: ' + str(request.elapsed.total_seconds()) + ' seconds, ' +
            'size: ' + (str(len(request.content)/float(1 << 10)) + ' KB'))

        self.text_header('[headers]')

        for key in headers.iterkeys():
            print key + ': ' + headers[key]

        self.text_header('[cookies]')
        group.write_cookies(request, 1)

    #
    # make http request and return response object
    #
    def make_request(self, route, group):
        if route.type == 'GET':
            request = requests.get(url = route.url,
                params = route.params,
                cookies = group.cookies)
        elif route.type == 'POST':
            request = requests.post(url = route.url,
                params = route.params,
                cookies = group.cookies)

        return request

    #
    # execute http request based on route name and print the response info
    #
    def execute(self, name):
        if len(name) == 0 or name not in self.short:
            return

        print 'Loading "' + name + '"...'

        route = self.short[name]
        group = self.groups[route.group]

        request = self.make_request(route, group)

        self.print_request(request, group)
        raw_input()

    #
    # column width line for division
    #
    def line(self):
        for i in range(int(self.columns)):
            sys.stdout.write('-')
            sys.stdout.flush()

    #
    # commonly used header
    #
    def text_header(self, text):
        self.line()
        print '\033[1m' + text + '\033[0;0m'
        self.line()

    #
    # print commands list
    #
    def show_cmds(self):
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
        print 'group remove <group> | remove group and all associated routes\n'
        print 'test | run test'

    #
    # accept command for editing a route, editing a group, executing a route,
    # or starting a test
    #
    def get_command(self, cmd):
        cmds = cmd.split(' ')

        if len(cmds) == 3 and cmds[0] == 'cookies' and cmds[1] == 'show':
            self.show_cookies(cmds[2])
        elif len(cmds) == 3 and cmds[0] == 'cookies' and cmds[1] == 'clear':
            self.clear_cookies(cmds[2])
        elif len(cmds) == 4 and cmds[0] == 'group' and cmds[1] == 'name':
            if cmds[2] in self.groups.iterkeys():
                self.groups[cmds[2]].set_name(cmds[3], self)
        elif len(cmds) == 3 and cmds[0] == 'group' and cmds[1] == 'remove':
            if cmds[2] in self.groups.iterkeys():
                self.groups[cmds[2]].remove_group(self)
        elif len(cmds) == 6 and cmds[0] == 'route' and cmds[1] == 'add':
            self.add_route(cmds)
        elif len(cmds) == 3 and cmds[0] == 'route'  and cmds[1] == 'remove':
            if cmds[2] in self.short:
                del self.short[cmds[2]]
                self.update_file()
        elif len(cmds) == 3:
            if cmds[0] in self.short:
                self.short[cmds[0]].edit(cmds[1], cmds[2], self)
        elif cmds[0] == 'cmds':
            self.show_cmds()
            raw_input()
        elif cmds[0] == 'test':
            test(self.TEST_FILE, self)
            raw_input()
        else:
            self.execute(cmd)

    #
    # update routes file after updating a route's value
    #
    def update_file(self):
        f = open(self.ROUTES_FILE, "w")

        for route in self.short:
            r = self.short[route]
            f.write((r.group + '|' + r.short + '|' + r.type + '|' +
                r.url + '|' + str(r.header) + '|' + str(r.params) + '\n'))

    #
    # append route file based on add route command
    #
    def add_route(self, cmds):
        group = cmds[2]
        sh = cmds[3]
        req_type = cmds[4]
        url = cmds[5]

        for value in cmds:
            if len(value) == 0:
                return

        if sh in self.short.iterkeys():
            print 'duplicate short found: "' + sh + '"'
            raw_input()
            return

        f = open(self.ROUTES_FILE, "a")
        f.write(group + '|' + sh + '|' + req_type + '|' + url + '|{}|{}\n')

    #
    # display cookies based on group name
    #
    def show_cookies(self, group):
        if group not in self.groups.iterkeys():
            return

        self.groups[group].show_cookies(self)

    #
    # call clear_cookies method for a group
    #
    def clear_cookies(self, group):
        self.line()

        if group not in self.groups.iterkeys():
            return

        print (str(self.groups[group].cookie_count) + ' cookies cleared for "' +
            group + '"')

        self.groups[group].clear_cookies()
        raw_input()
