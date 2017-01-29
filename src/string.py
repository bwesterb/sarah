from six.moves import range

try:
    import carah.string as _string
except ImportError:
    _string = None

if _string:
    to_hex = _string.to_hex
else:
    def to_hex(s):
        return ''.join((hex(ord(c))[2:].zfill(2) for c in s))


def from_hex(s):
    return ''.join((chr(int(s[2 * i:2 * (i + 1)], 16))
                    for i in range(len(s) / 2)))

# vim: et:sta:bs=2:sw=4:
