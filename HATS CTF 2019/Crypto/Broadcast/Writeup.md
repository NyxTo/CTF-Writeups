# Task
You have managed to force Alice to resend her ciphertext multiple times. Can you recover the message?\
Files: [chal.py](chal.py), [data.txt](data.txt)

# Source Code
Important parts of `chal.py`:
```python
def genrsa(m, e, s):
    p, q = next_prime(randint(0, 2**s)), next_prime(randint(0, 2**s))
    n = p * q
    return pow(m, e, n), n

e = 733
for _ in range(9**2):
    c, n = genrsa(flag, e, 1024)
    dataf.write("%d\n%d\n\n" % (c, n))
```
Using a fixed message `m` and encryption key `e = 733`, `data.txt` contains the ciphers `c` for different moduli `n`.

# Method
We have the residues of a fixed value, `m**e`, across different moduli. The moduli are products of primes less than `2**1024`, so it is unlikely that any of the primes are equal (this should be checked by the challenge setter). This lets us use the [Chinese Remainder Theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem#General_case) (CRT) to find `m**e` modulo the product of all `n`. Within CRT, the [Extended Euclidean Algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm#Pseudocode) is needed.
```python
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
```
As the product of the moduli, `prod` is very large, we can assume that the result of the CRT is the actual value of `flag**733`, without needing to take modulo `prod`.\
If the flag has `k` characters after `HATS{`, then:
- The flag is between `0x484154537b00...00` and `0x484154537c00...00`, each has `k*2` trailing zeroes in hex.
- Taking 733rd powers, `0x4e9a9ca7d7...00..00` and `0x4e9a9cbaf4...00...00`, each has 6996 hex digits then `k*2*733` zeroes.

Now, `flag**733` starts with `0x4e9a9ca877...` and has 39248 hex digits, which should equal `6996 + k * 1466`, so `k = 22`. With bounds on the flag, we can do a binary search to find the flag with the correct value of `flag**733` (it will take at most `k * 8 == 176` iterations).

# Solution
[soln.py](soln.py)
```python
from functools import reduce

dataf = open('data.txt', 'r')
c, n = [], []
for _ in range(81):
    c.append(int(dataf.readline()))
    n.append(int(dataf.readline()))
    dataf.readline()
flag733 = crt(c, n)

print len(hex(flag733)[2:]), hex(flag733)[2:12]
print len(str(flag733)), len(str(reduce(lambda a, b: a*b, n)))

flag_min, flag_max = 0x484154537b << 176, 0x484154537c << 176
while flag_min < flag_max:
    mid = (flag_min + flag_max) // 2
    mid733 = mid**733
    if flag733 < mid733:
        flag_max = mid
    elif flag733 > mid733:
        flag_min = mid
    else:
        print hex(mid)[2:].decode('hex')
        break
```
We see that `flag733` (47259 digits) is much smaller than `prod` (49685 digits), so it is on the right track.
> `39248 4e9a9ca877`\
> `47259 49685`\
> `HATS{3xp0n3n7_700_5m41l!!!}`.
