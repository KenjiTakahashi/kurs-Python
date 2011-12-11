# -*- coding: utf-8 -*-

class Doskonale(object):
    def __init__(self, n = None):
        self.val = 5
        self.max = n
    def __iter__(self):
        return self
    def __next__(self):
        while 1:
            self.val += 1
            if self.max and self.val > self.max:
                raise StopIteration
            if sum(
                [d for d in range(1, self.val) if self.val % d == 0]
            ) == self.val:
                break
        return self.val

def doskonale_iter(n):
    return list(Doskonale(n))

print(doskonale_iter(4096))

from timeit import Timer
t = Timer("doskonale_iter(8192)", "from __main__ import doskonale_iter")
print(t.timeit(4))

from io import StringIO

class Worder(object):
    def __init__(self, stream):
        self.stream = stream
        self.firstchar = ''
    def __iter__(self):
        return self
    def __next__(self):
        word = self.firstchar
        term = False
        split = False
        while True:
            char = self.stream.read(1)
            if char == '':
                if word == '':
                    raise StopIteration
                self.firstchar = ''
                break
            if char.isalnum():
                if term:
                    self.firstchar = char
                    break
                word += char
            else:
                if char == '-':
                    split = True
                elif not(char == '\n' and split):
                    term = True
                    self.firstchar = ''
        return word

from collections import Counter

def stats(string):
    stats = Counter()
    stream = StringIO(string)
    for word in Worder(stream):
        stats[len(word)] += 1
    stream.close()
    return stats

string = """Zaprogramuj iterator który przetwarza strumień tekstowy i zwraca
kolejne słowa z tekstu (dla utrudnienia uwzględnij dzielenie słów na końcach wier-
szy), pomijając białe znaki i znaki interpunkcyjne. Korzystając z tej implementacji
zaprogramuj obliczanie statystyki długości słów w tekście, tj. ile jest słów długości 1,
ile długości 2 etc."""

print(stats(string))
