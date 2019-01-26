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

class route:
    #
    # initiate route with group name, route string from file, and a reference to
    # the base's routes dict
    #
    def __init__(self, group, route_str, short):
        self.route_str = route_str
        self.group = group
        self.fix(short)

    #
    # edit the url, name, group, type, header dict, or params dict of a route
    #
    def edit(self, which, edit, base):
        if len(edit) == 0:
            return

        if which == 'url':
            self.url = edit
        elif which == 'name':
            if edit in base.short.iterkeys():
                print 'duplicate route found: "' + self.short + '"'
                raw_input()
                return

            self.short = edit
        elif which == 'group':
            self.group = edit
        elif which == 'type':
            self.type = edit

        if which == ('url' or 'name' or 'group' or 'type'):
            base.update_file()
        else:
            self.mod_dict(which, edit, base)

    #
    # modify headers or params of route from edit method
    #
    def mod_dict(self, which, edit, base):
        if edit == '{}':
            if which == 'header':
                self.header.clear()
            elif which == 'params':
                self.params.clear()
        else:
            new = edit.split(',')

            for n in new:
                a = n.split(':')

                if which == 'header':
                    if len(a[1]) == 0:
                        del self.header[a[0]]
                    else:
                        self.header[a[0]] = a[1]
                elif which == 'params':
                    if len(a[1]) == 0:
                        del self.params[a[0]]
                    else:
                        self.params[a[0]] = a[1]

        base.update_file()

    #
    # split route input from file and assign to route object
    #
    def fix(self, short):
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
            print 'duplicate route found: "' + self.short + '"'
            sys.exit()
