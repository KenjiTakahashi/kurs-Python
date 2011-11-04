# -*- coding: utf-8 -*-

import html.parser
import os
import urllib.request
from urllib.error import URLError
from threading import Thread, RLock
from timeit import Timer

class ActivityBackend(html.parser.HTMLParser):
    def __init__(self, directory, rlock, results):
        self.directory = directory
        self.results = results
        self.rlock = rlock
        super(type(self), self).__init__(self)
    def handle_starttag(self, tag, attrs):
        if tag == 'a' or tag == 'img':
            for (attr, value) in attrs:
                if attr == 'href' or attr == 'src':
                    if '://' in value:
                        try:
                            urllib.request.urlopen(value)
                        except URLError:
                            with self.rlock:
                                self.results.add((value, False))
                        else:
                            with self.rlock:
                                self.results.add((value, True))
                    else:
                        try:
                            open(self.directory + value)
                        except IOError as e:
                            if e.errno == 21:
                                with self.rlock:
                                    self.results.add((value, True))
                            else:
                                with self.rlock:
                                    self.results.add((value, False))
                        else:
                            with self.rlock:
                                self.results.add((value, True))

class ActivityChecker(object):
    def __init__(self, directory):
        self.directory = directory
        self.rlock = RLock()
        self.results = set()
    def check(self):
        threads = list()
        for root, _, filenames in os.walk(self.directory):
            for filename in filenames:
                if os.path.splitext(filename)[1] == '.html':
                    with open(os.path.join(root, filename)) as data:
                        thread = Thread(
                            target = ActivityBackend(
                                self.directory,
                                self.rlock,
                                self.results
                            ).feed, 
                            args = (data.read(),)
                        )
                        threads.append(thread)
                        thread.start()
        for t in threads:
            t.join()
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
t = Timer(ac.check)
print(t.timeit(4))
ac.pretty_print()

class ReferenceBackend(html.parser.HTMLParser):
    def __init__(self, rlock, results, curfile):
        self.rlock = rlock
        self.results = results
        self.curfile = curfile
        super(type(self), self).__init__(self)
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attr, value) in attrs:
                if attr == 'href':
                    with self.rlock:
                        self.results.setdefault(
                            value, {self.curfile}
                        ).add(self.curfile)

class ReferenceChecker(object):
    def __init__(self):
        self.rlock = RLock()
        self.results = dict()
    def check(self, directory):
        threads = list()
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                curfile = os.path.join(
                    os.path.relpath(root, directory), filename
                )
                with open(os.path.join(root, filename)) as data:
                    thread = Thread(
                        target = ReferenceBackend(
                            self.rlock,
                            self.results,
                            curfile
                        ).feed,
                        args = (data.read(),)
                    )
                    threads.append(thread)
                    thread.start()
        for t in threads:
            t.join()
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
t = Timer(lambda : rc.check(os.path.expanduser('~/kenjitakahashi.github.com/_site')))
print(t.timeit(4))
rc.pretty_print()
