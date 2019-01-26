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

class group:
    #
    # initialize group with name and location cookie root directory
    #
    def __init__(self, name, COOKIE_ROOT):
        self.name = name
        self.routes = []
        self.cookies = {}
        self.COOKIE_ROOT = COOKIE_ROOT
        self.cookie_dir = self.COOKIE_ROOT + '/' + self.name + '/'
        self.get_cookies()

    #
    # remove every route from base's short dict (routes) and remove cookies
    # from the appropriate directory and update the routes file
    #
    def remove_group(self, base):
        temp = base.short.copy()

        for route in temp.iterkeys():
            if base.short[route].group == self.name:
                del base.short[route]

        self.clear_cookies()
        base.update_file()

    #
    # set the name of the current group and update the routes file
    #
    def set_name(self, new_name, base):
        for route in base.short.iterkeys():
            if base.short[route].group == self.name:
                base.short[route].group = new_name

        try:
            dr = self.COOKIE_ROOT + '/'
            os.rename(dr + self.name, dr + new_name)
        except OSError, e:
            print ('cookies from "' + self.name + '" will not be ' +
                'transferred to "' + new_name + '"')
            raw_input()

        base.update_file()

    #
    # write cookies to the group's cookie directory after an http request
    #
    def write_cookies(self, request, show_msg):
        cookies = request.cookies.get_dict()

        for key in cookies:
            if show_msg:
                print '"' + key + '" added to "' + self.name + '"'

            f = open(self.cookie_dir + key, 'w')
            f.write(cookies[key])

    #
    # display the group's cookie keys and values
    #
    def show_cookies(self, base):
        if len(self.cookies) == 0:
            return

        base.line()

        for key in self.cookies.iterkeys():
            print key + ': ' + self.cookies[key] + '\n'

        raw_input()

    #
    # remove group's cookie files
    #
    def clear_cookies(self):
        for f in glob.glob(self.cookie_dir + '*'):
            os.remove(f)

    #
    # get group's cookie files from the directoy under the group's name and
    # update count
    #
    def get_cookies(self):
        cookie_count = 0

        if not os.path.exists(self.cookie_dir):
            os.makedirs(self.cookie_dir)

        for cookie_name in os.listdir(self.cookie_dir):
            cookie = open(self.cookie_dir + cookie_name, 'r').read()

            if cookie_name not in self.cookies.iterkeys():
                self.cookies[cookie_name] = cookie
                cookie_count = cookie_count + 1

        self.cookie_count = cookie_count
