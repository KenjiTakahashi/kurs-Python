def doskonale_skladana(n):
    return [i for i in range(6, n + 1) if i == sum(
        [d for d in range(1, i) if i % d == 0])]

def doskonale_funkcyjna(n):
    return list(
        filter(
            lambda x : x == sum(
                filter(
                    lambda y : x % y == 0,
                    range(1, x)
                )
            ),
            range(6, n + 1)
        )
    )

print(doskonale_skladana(4096))

print(doskonale_funkcyjna(4096))

from timeit import Timer
t1 = Timer("doskonale_skladana(8192)", "from __main__ import doskonale_skladana")
print(t1.timeit(4))
t2 = Timer("doskonale_funkcyjna(8192)", "from __main__ import doskonale_funkcyjna")
print(t2.timeit(4))
