# -*- coding: utf-8 -*-

class Doskonale(object):
    """Perfect number generator.

    >>> d = Doskonale()
    >>> for dd in d:
    ...     print(dd)
    ...     if dd > 50:
    ...         break
    6
    28
    496
    """
    def __init__(self, n = None):
        """Constructs new Doskonale instance.
        
        Args:
        n -- optional upper bound.

        >>> d = Doskonale()
        >>> d.val
        5
        >>> d.max
        >>> e = Doskonale(20)
        >>> e.val
        5
        >>> e.max
        20
        """
        self.val = 5
        self.max = n
    def __iter__(self):
        """Returns iterator.

        >>> d = Doskonale()
        >>> iter(d)
        <10.Doskonale object at ...>
        >>> d = Doskonale()
        >>> iter(d) == d
        True
        """
        return self
    def __next__(self):
        """Returns next element of the iterator.

        >>> d = Doskonale()
        >>> d.__next__()
        6
        >>> d.__next__()
        28
        >>> d.__next__()
        496
        >>> e = Doskonale(4096)
        >>> list(e)
        [6, 28, 496]
        """
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
    """Prints perfect numbers from 6 to n. Iterator based version.

    Examples:
    >>> doskonale_iter(6)
    [6]
    >>> doskonale_iter(40)
    [6, 28]
    >>> doskonale_iter(4096)
    [6, 28, 496]
    >>> doskonale_iter("AAA")
    Traceback (most recent call last):
        ...
    TypeError: unorderable types: int() > str()
    """
    return list(Doskonale(n))

from io import StringIO

string = """Zaprogramuj iterator który przetwarza strumień tekstowy i zwraca
kolejne słowa z tekstu (dla utrudnienia uwzględnij dzielenie słów na końcach wier-
szy), pomijając białe znaki i znaki interpunkcyjne. Korzystając z tej implementacji
zaprogramuj obliczanie statystyki długości słów w tekście, tj. ile jest słów długości 1,
ile długości 2 etc."""

class Worder(object):
    """String to words splitter.

    Example:
    >>> w = Worder(StringIO(string))
    >>> for i, ww in enumerate(w):
    ...     print(ww)
    ...     if i > 3:
    ...         break
    Zaprogramuj
    iterator
    który
    przetwarza
    strumień
    """
    def __init__(self, stream):
        """Contructs new Worder instance.

        >>> stream = StringIO(string)
        >>> w = Worder(stream)
        >>> w.stream == stream
        True
        >>> w.firstchar
        ''
        """
        self.stream = stream
        self.firstchar = ''
    def __iter__(self):
        """Returns iterator.

        >>> w = Worder(StringIO(""))
        >>> iter(w) == w
        True
        """
        return self
    def __next__(self):
        """Returns next word from the given string.

        >>> w = Worder(StringIO(string))
        >>> w.__next__()
        'Zaprogramuj'
        >>> w.__next__()
        'iterator'
        >>> w.__next__()
        'który'
        >>> stream = StringIO("Zaprogramuj iterator, który coś tam zrobi")
        >>> w = Worder(stream)
        >>> list(w)
        ['Zaprogramuj', 'iterator', 'który', 'coś', 'tam', 'zrobi']
        """
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
    """Gives us some stats for the given string.

    Example:
    >>> stats(string)
    Counter({1: 7, 8: 6, 3: 5, 5: 5, 4: 4, 7: 4, 10: 4, 11: 4, 2: 2, 6: 2, 9: 2, 13: 1, 14: 1})
    """
    stats = Counter()
    stream = StringIO(string)
    for word in Worder(stream):
        stats[len(word)] += 1
    stream.close()
    return stats
