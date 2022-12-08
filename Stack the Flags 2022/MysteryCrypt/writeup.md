## MysteryCrypt

We found this encryption algorithm being used after the key exchange. We suspect that it is very weak and can be cracked in a short amount of time. Bonus flag if less than 1000 queries are used.

We are given [crypt_generate.py]:
```py
import random
import os
import signal

key = random.randint(2, 2**32-1)
delta = 0x9E37 ^ 0x79B9
FLAG = os.getenv('FLAG')
FLAG2 = os.getenv('FLAG2')
def mod(x):
    return x % (2**16)

k1 = mod(key >> 16)
k2 = mod(key)
def ror(n, k):
    return (n << k) | (n >> (16 - k))
def rol(n, k):
    return (n >> k) | (n << (16 - k))
def round(l, r, k1, k2):
    res = mod((ror(r,4) ^ rol(r,5) ^ k1) + r) ^ mod(k2 + r + delta)
    return (r, l ^ res)

def encrypt(num):
    l, r = mod(num >> 16), mod(num)
    for i in range(128):
        l, r = round(l, r, k1, k2)
    return (l << 16) + r

signal.alarm(30)
for i in range(100000):
    print("1 = encrypt, 2 = submit key")
    choice = int(input())
    if choice == 1:
        print("input 32 bit integer: ")
        num = int(input())
        print(f"encrypted = {encrypt(num)}")
    elif choice == 2:
        print("key = ?")
        inputkey = int(input())
        if inputkey == key:
            print(open(FLAG).read())
            if i < 1000:
                print(open(FLAG2).read())
        else:
            print('Wrong!')
        break

```

The `encrypt()` function consists of 128 iterations of `round()`, using the same key `(k1, k2)` every time. Any such cipher consisting of several rounds, that reuses the same sequence of keys in a fixed cyclic order, is vulnerable to an exploit called a Slide attack. This includes the case here of a single key. Given a relatively large collection of plaintext-ciphertext pairs, a Slide attack searches for two pairs, `(P1, C1)` and `(P2, C2)`, satisfying the properties that `round(P1) == P2` and `round(C1) == C2`. Such pairs are called a **slid pair**. The idea is that since the cipher encrypting `P1` to `C1` consists of multiple rounds, the entire plaintext-ciphertext pair is **slid** by one round, shifting the pair to `P2` encrypted to `C2`.

The Wikipedia article [https://en.wikipedia.org/wiki/Slide_attack#The_actual_attack] and a paper by Biryukov and Wagner [https://link.springer.com/content/pdf/10.1007/3-540-48519-8_18.pdf] sections 2 and 3 explain the attack in further detail. Both sources point out specifically that when Feistel ciphers are involved, the exploit can be optimised to be more efficient. We wonder if that is what we have here?

Given a key `ka<<16|kb`, each call to the `round()` function maps an input pair `l<<16|r` to `r<<16 | (l^val)`, where `val` is a value depending only on `r` (and the key which is fixed). This fits exactly the definition of a Feistel cipher, since passing the input pair `(l^val) << 16 | r` would give the output `((l^val)^val) << 16 | r == l<<16|r` which is the same as the original input pair. Since the plaintexts and ciphertexts come from a space of 32 bits, we expect to require around the order of `2**(32/4) == 256` pairs, to find a _slid pair_.

The reason why a Slide attack is much more effective on Feistel ciphers, is because one round keeps half of the message identical. We can encrypt several plaintexts of the form `x<<16 | 1` and `1<<16 | y` (here the value of `1` is an arbitrary but fixed constant). Among these two collections of ciphertexts, if we find one from each where the right half of the first is the same as the left half of the second, we are likely to have found a _slid pair_. The chance of this happening in any two such ciphertexts is 1 in `2**16 == 65536`, and the chance of coincidence among these is a further 1 in `2**16 == 65536`.

```py

def feistel(l, r, k1, k2, num):
    for _ in range(num):
        val = ((r<<4 ^ r>>12 ^ r>>5 ^ r<<11 ^ k1) + r) & 0xffff ^ (k2 + r + 59278) & 0xffff
        l, r = r, l ^ val
    return l, r

def encrypt(sh, l, r):
    sh.recvline()
    sh.sendline(b'1')
    sh.recvline()
    s.sendline(str(l<<16|r).encode())
    return int(sh.recvline()[12:])

enc_x1, enc_1y = [], []
sh = remote('167.99.77.149', 31042)
for i in range(490):
    x = randrange(65536)
    enc = encrypt(sh, x, 1)
    enc_x1.append((x, enc>>16, enc&0xffff))
    y = randrange(65536)
    enc = encrypt(sh, 1, y)
    enc_1y.append((y, enc>>16, enc&0xffff))

keys = set()
for (x, lx1, rx1), (y, l1y, r1y) in zip(enc_x1, enc_1y):
    if rx1 != l1y: continue
    pval, cval = x ^ y, lx1 ^ r1y
    for ka in range(65536):
        pside = ((16 ^ 2048 ^ ka) + 1) % 65536
        cside = ((rx1<<4 ^ rx1>>12 ^ rx1>>5 ^ rx1<<11 ^ ka) + rx1) % 65536
        pkb = ((pval ^ pside) - 59279) % 65536
        ckb = ((cval ^ cside) - rx1 - 59278) % 65536
        if pkb == ckb:
            keys.add((ka, pkb | ckb))

for ka, kb in keys:
    if not all([feistel(x, 1, ka, kb, 128) == (l, r) for (x, l, r) in enc_x1]): continue
    if not all([feistel(1, y, ka, kb, 128) == (l, r) for (y, l, r) in enc_1y]): continue
    sh.recvline()
    sh.sendline(b'2')
    sh.recvline()
    sh.sendline(str(ka<<16|kb).encode())
    print(sh.recvline())
    break
```

Since the challenge description suggests using less than 100 queries, we retrieve 490 plaintext-ciphertext pairs of each kind. We then proceed with a standard Slide attack. Compare the two plaintexts, and the two ciphertexts, to enumerate all possible keys, by reverse engineering the simple `round()` Feistel cipher. This is computationally efficient since we are only considering one round at a time. Then, check that the encryption determined by each of these keys match the plaintext-ciphertext pairs, for further filtering of keys. With a low probability of failure, just a few attempts gets the flag `STF22{mc1_8c7d5b1b2a503822}`.