def command(a, n):
    x = len(a)
    if x == n:
        return a
    else:
        p = a[::-1]
        # i=0
        for y in range(0, n-x):
            p = p + '0'
        p = p[::-1]
        return p
class Memory:
    data = {}
    text = []
    stack = []
    pointer = 268435456

    def add_details(s, add, val):
        # add = hex(add).zfill(8)
        add = '0x'+(hex(add)[2::].zfill(8))
        s.data[add] = hex(int(val, 2)).replace('0x', '').zfill(2)
        

