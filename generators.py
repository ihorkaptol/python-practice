from itertools import count, islice


class Repeat:
    def __init__(self, value, times):
        self.value = value  # what to give out
        self.left = times   # how many values are left

    def __iter__(self):
        return self

    def __next__(self):
        if self.left <= 0:
            raise StopIteration
        self.left -= 1
        return self.value


def repeat_gen(value, times):
    for _ in range(times):
        yield value


def running_total(numbers):
    total = 0
    for number in numbers:
        total += number
        yield total


def unique(iterable):
    seen = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item


r = Repeat("ha", 3)
print(list(r))
print(list(r))
print("".join(repeat_gen("ha", 3)))
g = repeat_gen("ha", 2)
print(list(g), list(g))
print(list(running_total([3, 1, 4, 1, 5])))
print(list(running_total(x for x in range(1, 5))))
print(list(unique("abracadabra")))
print(list(unique([100, "M1", 100, "D1", "M1"])))
print(list(islice(unique(n % 4 for n in count()), 4)))