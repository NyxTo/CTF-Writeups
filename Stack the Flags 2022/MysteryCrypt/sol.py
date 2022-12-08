from pwn import remote
from random import randrange

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
sh = remote(SERVER, PORT)
for i in range(490):
    x = randrange(65536)
    enc = encrypt(sh, x, 1)
    enc_x1.append((x, enc>>16, enc&0xffff))
    y = randrange(65536)
    enc = encrypt(sh, 1, y)
    e1y.append((y, enc>>16, enc&0xffff))

keys = set()
for (x, lx1, rx1), (y, l1y, r1y) in zip(enc_x1, enc_1y):
    if rx1 != l1y: continue
    pval, cval = x ^ y, lx1 ^ r1y
    for ka in range(65536):
        pside = ((16 ^ 2048 ^ ka) + 1) % 65536
        cside = ((rx1<<4 ^ rx1>>12 ^ rx1>>5 ^ rx1<<11 ^ ka) + rx1) % 65536
        pkb = ((pval ^ pside) - 59279) % 65536
        ckb = ((cval ^ cside) - rx1 - 59278) % 65536
        if pkb == ckb and feistel(x, 1, ka, pkb, 128) == (lx1, rx1) and feistel(1, y, ka, ckb, 128) == (l1y, r1y):
            keys.add(ka<<16 | pkb | ckb)

for ka, kb in keys:
    if not all([feistel(x, 1, ka, kb, 128) == (l, r) for (x, l, r) in enc_x1]): continue
    if not all([feistel(1, y, ka, kb, 128) == (l, r) for (y, l, r) in enc_1y]): continue
    sh.recvline()
    sh.sendline(b'2')
    sh.recvline()
    sh.sendline(str(ka<<16|kb).encode())
    print(sh.recvline())
    break
