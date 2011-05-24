def restricted_cover(l, succsOf):
        """ Returns a restricted <succsOf> which only takes and yields
            values from <l> """
        fzl = frozenset(l)
        lut = dict()
        for i in l:
                lut[i] = fzl.intersection(succsOf(i))
        return lambda x: lut[x]

def dual_cover(l, succsOf):
        """ <succsOf> assigns to each element of <l> a list of successors.
            This function returns the dual, "predsOf" if you will. """ 
        lut = dict()
        for i in l:
                lut[i] = list()
        for i in l:
                for j in succsOf(i):
                        lut[j].append(i)
        return lambda x: lut[x]
                
def sort_by_successors(l, succsOf):
        """ Sorts a list, such that if l[b] in succsOf(l[a]) then a < b """
        rlut = dict()
        nret = 0
        todo = list()
        for i in l:
                rlut[i] = set()
        for i in l:
                for j in succsOf(i):
                        rlut[j].add(i)
        for i in l:
                if len(rlut[i]) == 0:
                        todo.append(i)
        while len(todo) > 0:
                i = todo.pop()
                nret += 1
                yield i
                for j in succsOf(i):
                        rlut[j].remove(i)
                        if len(rlut[j]) == 0:
                                todo.append(j)
        if nret != len(l):
                raise ValueError, "Cycle detected"
