pl = {}


def add(key, plurals):
    pl.update({key: plurals})


def t(key, count):
    return pl.get(key).get(count_pick(count))


def count_pick(count):
    if count == 0:
        return "zero"
    count_many = count % 100
    if 10 < count_many < 15:
        return "many"

    last_digit = count % 10

    if last_digit == 1:
        return "one"
    elif last_digit > 1 and last_digit < 5:
        return "few"
    else:
        return "many"
