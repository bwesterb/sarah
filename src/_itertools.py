
def pick(iterable):
        return iter(iterable).next()

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
