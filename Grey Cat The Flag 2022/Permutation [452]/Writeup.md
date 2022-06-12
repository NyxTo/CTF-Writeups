## Files
[main.py](main.py) \
[perm.py](perm.py) \
[out.txt](out.txt)

## Method
Looking at [perm.py](perm.py), a permutation can be associated with a function, mapping each index to its respective element. For example the permutation `p = [3,4,1,0,2]` has an associated function `f()` such that `f(0) = 3`, `f(1) = 4`, `f(2) = 1`, `f(3) = 0`, `f(4) = 2`. \
Then, multiplication of permuatations can be represented as composition of the associated functions, since `self.__mul__(other)` evaluates `self.internal[other.internal[i]]` for each index `i`. Accordingly, a power of a permutation is an iteration of its associated function.

Considering iterations of a permutation motivates breaking it down as a disjoint union of cycles. Using the same example above, this would translate as `0 -> 3 -> 0` together with `1 -> 4 -> 2 -> 1`. Rather than its representation as an array, we can more quickly see whwt iteration does. For each cycle, the `k`-th iteration jumps `k` steps at a time through the cycle, wrapping back around.

First we decompose the base generator permutation `g`:
```py
cycles, done = [], set()
for i,e in enumerate(g):
    if i in done: continue
    loop = [i,e]
    while e != i:
    e = g[e]
    loop.append(e)
    cycles.append(loop)
    done |= set(loop)
```
The `done` set is used to avoid repetition of cycles, an index is skipped if already in a previous cycle.
Next for each `loop`, just find where `something` and `B[something]` are to determine the number of steps jumped. Note that this number could also be increased by the loop length or any multiple of it, i.e. `b % len(loop)` must be the difference between the indices of `something` and `B[something]`, not necessarily `b` itself.
```py
for loop in cycles:
    print(loop.index(B[loop[0]]), len(loop))
# 3740 4294
# 456 482
# 13 35
# 5 51
# 17 73
# 20 36
# 20 27
# 0 2
```
Now we have a few pairs of numbers: the residues of a fixed integer `b` across different moduli. Sounds familiar? It's the exact setup for the Chinese Remainder Theorem. The numbers are small, we can feed them into any online CRT calculator to get `b` (the smallest of infinitely many values): `261895623968`.

Nearly done, follow along with the `encrypt` function to decrypt `c`:
```py
from Crypto.Util.number import long_to_bytes
from hashlib import shake_256
key = str(Perm(A) ** 261895623968).encode()
otp = shake_256(key).digest(len(key))
c = long_to_bytes(c)
print(xor(otp, c))
```
**Flag**: grey{DLP_Is_Not_Hard_In_Symmetric_group_nzDwH49jGbdJz5NU}
