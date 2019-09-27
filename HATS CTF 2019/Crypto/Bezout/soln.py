def ext_euclid(a, b):
    x, y, v = 0, 1, []
    while a > 0:
        v.append(b // a)
        a, b = b % a, a
    g = b
    for i in range(len(v)-1, -1, -1):
        x, y = y - v[i] * x, x
    return x, y, g

def gen_bezout(a):
    x = [0, 0]
    x[0], x[1], g = ext_euclid(a[0], a[1])
    for k in range(2, len(a)):
        b, c, g = ext_euclid(g, a[k])
        x = [y * b for y in x] + [c]
    return x

f = open('data.txt', 'r')
n = int(f.readline())
e, c = [], []
for _ in range(20):
    e.append(int(f.readline()))
    c.append(int(f.readline()))

d = gen_bezout(e)
m = 1
for i in range(20):
    if d[i] < 0:
        c[i], _, _ = ext_euclid(c[i], n)
    m = m * pow(c[i], abs(d[i]), n) % n

print hex(m)[2:].decode('hex')
