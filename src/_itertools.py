
def pick(iterable):
    return next(iter(iterable))


def iter_by_n(iterable, n):
    ret = []
    it = iter(iterable)
    while True:
        while len(ret) < n:
            try:
                ret.append(next(it))
            except StopIteration:
                if ret:
                    yield ret
                return
        yield ret
        ret = []
# vim: et:sta:bs=2:sw=4:
