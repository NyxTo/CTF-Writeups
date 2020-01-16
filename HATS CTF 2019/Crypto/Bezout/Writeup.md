# Task
You have found an interesting modification to RSA and gotten the encryption with different exponents, could you recover the message?\
Files: [chal.py](chal.py), [data.txt](data.txt)

# Source Code
Important parts of `chal.py`:
```python
p, q = next_prime(randint(0, 2**1024)), next_prime(randint(0, 2**1024))
n = p * q

ep = [next_prime(randint(1,2**20)) for _ in range(20)]
em = reduce(lambda x, y: x*y, ep)
e = [em//i for i in ep]
c = [pow(flag, i, n) for i in e]

f.write(str(n) + '\n')
for i in range(len(e)):
    f.write(str(e[i]) + '\n' + str(c[i]) + '\n')
```
- `ep` contains 20 distinct primes, `em` is their product.
- `e` contains the product of all the primes except each one (in turn).
- `data.txt` contains `e` and `c`, the encrypted flag using `e` as moduli.

# Method
Given some integers `a[i]`, a [generalised Bezout's Identity](https://en.wikipedia.org/wiki/B%C3%A9zout%27s_identity#For_three_or_more_integers) lets us find integers `x[i]` such that the sum of `a[i] * x[i]` is the GCD of all `a[i]`.
- Let `g[k]` represent the GCD of `a[0]` through `a[k-1]`.
- Set `a[0]` and `a[1]` so that `a[0]*x[0] + a[1]*x[1] == gcd(x[0], x[1]) == g[2]`, using the [Extended Euclidean Algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm#Pseudocode).
- As `g[k+1] == gcd(g[k], x[k])`, find `b` and `c` so that `g[k+1] == b*g[k] + c*x[k]`.
- Substituting the current `x[i]` into `g[k]`, we have new values of `x[i]` so that the sum of `a[i]*x[i]` is `g[k+1]`.
- Repeating this until the end of `a` gives us the `x[i]` we need.
```python
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
```
In standard RSA, for a message `m`, we have `m**e` modulo `n`, with no _direct_ way to "make" the exponent become 1. But now, there are multiple exponents `e[i]`, and the GCD of all of them is 1. With `gen_bezout()`, we can find corresponding decryption keys `d[i]` so that the sum of `e[i] * d[i]` is 1.\
For each `c[i]`, compute `c[i] ** d[i] == (m**e[i]) ** d[i] == m ** (e[i]*d[i])`. Negative `d[i]` indicates finding the modular inverse, which we do with `ext_euclid()`. Then multiplying them together gives `m**1`, so we have decrypted the message.

# Solution
[soln.py](soln.py)
```python
f = open('data.txt', 'r')
n = int(f.readline())
e, c = [], []
for _ in range(20):
    e.append(int(f.readline()))
    c.append(int(f.readline()))

d = gen_bezout(e)
m = 1
for i in range(20):
    if d[i] < 0: c[i], _, _ = ext_euclid(c[i], n)
    m = m * pow(c[i], abs(d[i]), n) % n
print hex(m)[2:].decode('hex')
```
> `HATS{m4ny_3xp0n3n75_w17h_6cd_1_15_vuln3r4bl3}`
