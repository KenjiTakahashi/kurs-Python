# -*- coding: utf-8 -*-

import html.parser
import os
import urllib.request
from urllib.error import URLError

class ActivityChecker(html.parser.HTMLParser):
    def __init__(self, directory):
        self.directory = directory
        self.results = set()
        super(ActivityChecker, self).__init__(self)
    def handle_starttag(self, tag, attrs):
        if tag == 'a' or tag == 'img':
            for (attr, value) in attrs:
                if attr == 'href' or attr == 'src':
                    if '://' in value:
                        try:
                            urllib.request.urlopen(value)
                        except URLError:
                            self.results.add((value, False))
                        else:
                            self.results.add((value, True))
                    else:
                        try:
                            open(self.directory + value)
                        except IOError as e:
                            if e.errno == 21:
                                self.results.add((value, True))
                            else:
                                self.results.add((value, False))
                        else:
                            self.results.add((value, True))
    def check(self):
        for root, _, filenames in os.walk(self.directory):
            for filename in filenames:
                if os.path.splitext(filename)[1] == '.html':
                    with open(os.path.join(root, filename)) as data:
                        self.feed(data.read())
        return self.results
    def pretty_print(self):
        const = 0
        for (lnk, _) in self.results:
            if len(lnk) > const:
                const = len(lnk)
        const += 10
        print("<link>{0}".format("<status>".rjust(const + 2)))
        for (lnk, status) in self.results:
            print("{0}{1}".format(
                lnk, str(status).rjust(const - len(lnk) + len(str(status)))
            ))

ac = ActivityChecker(os.path.expanduser('~/kenjitakahashi.github.com/_site'))
ac.check()
ac.pretty_print()

class ReferenceChecker(html.parser.HTMLParser):
    def __init__(self):
        self.results = dict()
        self.curfile = ''
        super(ReferenceChecker, self).__init__(self)
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attr, value) in attrs:
                if attr == 'href':
                    self.results.setdefault(
                        value, set([self.curfile])
                    ).add(self.curfile)
    def check(self, directory):
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                self.curfile = os.path.join(
                    os.path.relpath(root, directory), filename
                )
                with open(os.path.join(root, filename)) as data:
                    self.feed(data.read())
        return self.results
    def pretty_print(self):
        const = 0
        for k in self.results.keys():
            if len(k) > const:
                const = len(k)
        const += 10
        print("<link>{0}".format("<references>".rjust(const + 6)))
        for k, v in self.results.items():
            item = v.pop()
            print("{0}{1}".format(k, item.rjust(const - len(k) + len(item))))
            while v:
                item = v.pop()
                print(item.rjust(const + len(item)))

rc = ReferenceChecker()
rc.check(os.path.expanduser('~/kenjitakahashi.github.com/_site'))
rc.pretty_print()
