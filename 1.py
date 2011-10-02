# -*- coding: utf-8 -*-

def slownie(liczba):
    nom = [
        ["", "", ""],
        ["tysiąc", "tysiące", "tysięcy"],
        ["milion", "miliony", "milionów"],
    ]
    liczba = str(liczba)[::-1]
    dziwne = {
        10: "dziesięć",
        11: "jedenaście",
        14: "czternaście",
        15: "piętnaście",
        16: "szesnaście"
    }
    cyfry = [
        "zero", "jeden", "dwa",
        "trzy", "cztery", "pięć",
        "sześć", "siedem", "osiem", 
        "dziewięć"
    ]
    def duze(x, i):
        if x:
            t = int(x[0])
            if int(x) == 1:
                return nom[i][0]
            elif t == 1:
                return nom[i][2]
            elif t <= 4 and int(x[::-1]) > 20:
                return nom[i][1]
            else:
                return nom[i][2]
    podstawa = [
        lambda x : cyfry[x],
        lambda x : x == 4 and "czterdzieści" or podstawa[0](x) + (
            x == 2 and "dzieścia" or (
                x <= 4 and "dzieści" or "dziesiąt"
            )
        ),
        lambda x : x == 1 and "sto" or (
            x == 2 and "dwieście" or podstawa[0](x) + (
                x <= 4 and "sta" or "set"
            )
        ),
    ]
    slowo = ""
    for i, l in enumerate(
        [liczba[i:i + 3] for i in xrange(0, len(liczba), 3)]
    ):
        temp = ""
        if l[-1] == '-':
            temp = "minus " + temp
            l = l[:-1]
        if l:
            lt = int(l[:2][::-1])
            if lt >= 10 and lt < 20:
                try:
                    temp += dziwne[lt]
                except KeyError:
                    temp += podstawa[0](int(l[0])) + "naście "
                try:
                    temp = podstawa[2](int(l[2])) + " " + temp + " "
                except IndexError:
                    pass
            else:
                for j, ll in enumerate(l):
                    if len(l) == 1 or int(ll) > 0:
                        temp = podstawa[j](int(ll)) + " " + temp
        slowo = temp + (i >= 0 and duze(l, i) or "") + " " + slowo
    return slowo

print slownie(116456789)
print slownie(5371823)
print slownie(83472)
print slownie(2438382)
print slownie(11111)
print slownie(123456789)
print slownie(987654321)
print slownie(110)
print slownie(40)
print slownie(0)
print slownie(123456)
print slownie(-123)
print slownie(-11)
print slownie(-12346)
