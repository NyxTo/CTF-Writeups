from functools import reduce

def ext_euclid(a, b):
    c, d, x, y, v = a, b, 0, 1, []
    while c > 0:
        v.append(d // c)
        c, d = d % c, c
    for i in range(len(v)-1, -1, -1):
        x, y = y - v[i] * x, x
    if x < 0:
        x += b
        y -= a
    return x, y

def crt(resids, mods):
    prod = reduce(lambda a, b: a*b, mods)
    x = 0
    for i in range(len(mods)):
        y = prod // mods[i]
        z, _ = ext_euclid(y, mods[i])
        x += resids[i] * y * z
    return x % prod

dataf = open('data.txt', 'r')
c, n = [], []
for _ in range(81):
    c.append(int(dataf.readline()))
    n.append(int(dataf.readline()))
    dataf.readline()
flag733 = crt(c, n)

print (len(str(flag733)), len(str(reduce(lambda a, b: a*b, n)))) # 47259 49685
print (len(hex(flag733)[2:]), hex(flag733)[2:12]) # 39248 4e9a9ca877

flag_min, flag_max = 0x484154537b << 176, 0x484154537c << 176
while flag_min < flag_max:
    mid = (flag_min + flag_max) // 2
    mid733 = mid**733
    if flag733 < mid733:
        flag_max = mid
    elif flag733 > mid733:
        flag_min = mid
    else:
        print hex(mid)[2:].decode('hex') # HATS{3xp0n3n7_700_5m41l!!!}
        break
