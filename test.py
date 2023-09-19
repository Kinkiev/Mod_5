def fib():
    first = 0
    second = 1

    while True:
        yield first
        first, second = second, first + second
        # print(first)
        print(second)


def multiply_by_five():
    x = None
    while x := (yield x):
        x *= 5


if __name__ == "__main__":
    g = multiply_by_five()
    next(g)
    print(g.send(4))
    print(g.send("text "))
