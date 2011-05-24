def unpack_int(s):
        """ Reads a packed integer from string <s> """
        ret = 0
        i = 0
        while True:
                b = ord(s[i])
                ret |= (b & 127) << (i*7)
                i += 1
                if b & 128 == 0:
                        break
        return ret

def pack_int(v):
        """ Returns <v> as packed string. """
        if v == 0:
                return "\0"
        ret = ''
        while v > 0:
                c = v & 127
                v >>= 7
                if v != 0:
                        c = c | 128
                ret += chr(c)
        return ret

def read_packed_int(f):
        """ Reads a packed integer from the fileobj <f>. """
        ret = 0
        s = 0
        while True:
                b = ord(f.read(1))
                ret |= (b & 127) << s
                s += 7
                if b & 128 == 0:
                        break
        return ret
        
def write_packed_int(f, v):
        """ Writes the integer <v> packed to <f>. """
        if v == 0:
                f.write("\0")
        while v > 0:
                c = v & 127
                v >>= 7
                if v != 0:
                        c = c | 128
                f.write(chr(c))
