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

class test:
    #
    # initiate test with name of the test file and base object
    #
    def __init__(self, TEST_FILE, base):
        self.TEST_FILE = TEST_FILE
        self.routes = base.short
        self.run(base)

    #
    # handle cookies_clear command from the test file and clear the group's
    # cookies dict
    #
    def clear_cookies(self, split, base, c):
        if split[0] == 'cookies_clear':
            gr = split[1]
            sys.stdout.write(str(c) + ': ')

            if gr not in base.groups:
                self.bold_msg('[cookie]')
                print 'invalid group name: "' + gr + '"'
            else:
                base.groups[gr].clear_cookies()
                self.bold_msg('[cookie]')
                print 'cookies cleared for "' + gr + '"'

            return 1

        return 0

    #
    # split each line from the test file and handle test commands
    #
    def run(self, base):
        c = 1
        base.line()

        with open(self.TEST_FILE, 'r') as fl:
            for data in fl:
                data = data.replace('\n', '')
                split = data.split('|')

                if self.clear_cookies(split, base, c) == 1:
                    continue

                route_name = split[0]

                if route_name not in base.short:
                    sys.stdout.write(str(c) + ': ')
                    self.bold_msg('[error]')
                    print 'invalid route name: "' + route_name + '"'

                self.test_actions(base, route_name, split, c)
                c = c + 1

    #
    # check if the route has the assigned status code or output determined by
    # the test file input
    #
    def test_actions(self, base, route_name, split, c):
        route = base.short[route_name]
        group = base.groups[route.group]

        group.cookies.clear()
        group.get_cookies()

        request = base.make_request(route, group)

        group.write_cookies(request, 0)

        test_code = int(split[1])
        req_code = int(request.status_code)

        sys.stdout.write(str(c) + ': ')
        self.status_code(test_code, req_code, route_name)

        sys.stdout.write(str(c) + ': ')
        self.action(split, request, route_name)

    #
    # bold message for passed or failed tests
    #
    def bold_msg(self, msg):
        sys.stdout.write('\033[1m' + msg + '\033[0;0m ')

    def status_code(self, test_code, req_code, route):
        if test_code == req_code:
            self.bold_msg('[passed]')
            print ('route "' + route + '" has status code "' +
                str(test_code) + '"')
        else:
            self.bold_msg('[failed]')
            print ('route "' + route + '" does not have status code "' +
                str(test_code) + '"')

    #
    # check to see if an http response contains a string
    #
    def has_str(self, is_json, route, find, req):
        if is_json:
            self.bold_msg('[error]')
            print 'response for "' + route + '" is json'
            return

        if find in req:
            self.bold_msg('[passed]')
            print 'route "' + route + '" contains "' + find + '"'
        else:
            self.bold_msg('[failed]')
            print ('route "' + route + '" does not contain "' +
                find + '"')

    #
    # check to see if an http response contains a json key
    #
    def has_json(self, is_json, route, find, req):
        if not is_json:
            self.bold_msg('[error]')
            print 'response for "' + route + '" is not json'
            return

        goal = ast.literal_eval(find)
        valid = all((k in req and req[k]==v) for k,v in goal.iteritems())

        if valid:
            self.bold_msg('[passed]')
            print 'route "' + route + '" contains "' + str(goal) + '"'
        else:
            self.bold_msg('[failed]')
            print ('route "' + route + '" does not contain "' +
                str(goal) + '"')

    #
    # handle a test command other than clear_cookies
    #
    def action(self, spl, request, route):
        act = spl[2]
        find = spl[3]
        is_json = 0

        try:
            req = json.loads(request.text)
            is_json = 1
        except ValueError, e:
            req = request.text
            is_json = 0

        if act == 'has_str':
            self.has_str(is_json, route, find, req)
        else:
            self.has_json(is_json, route, find, req)
