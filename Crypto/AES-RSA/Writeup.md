# Task
I've made a combination of AES and RSA for my new crypto scheme. I may have forgotten how to decode RSA, could you help me retrieve the flag?\
`nc challs.hats.sg 1401`\
Files: [chal.py](chal.py)

# Source Code
Important parts of `chal.py`:
```python
key = urandom(16)
p, q = getPrime(512), getPrime(512)
n = p * q
e = 3

def encrypt(m):
    m = int(m.encode('hex'), 16)
    c = hex(pow(m, e, n))[2:].rstrip('L').decode('hex')
    iv = urandom(16)
    c = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(c, 16))
    return iv + c

def decrypt(c):
    iv, c = c[:16], c[16:]
    try:
        unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(c))
    except:
        return -1
    return 0

def main():
    print 'Encrypted flag: ' + encrypt(flag).encode('hex')
    for _ in xrange(2**13):
        print '1. Encrypt service'
        print '2. Decrypt service'
        inp = raw_input()
        if inp == '2':
            inp = raw_input().decode('hex')
            print decrypt(inp)
```
- An RSA cipher is generated, with encryption key `e = 3` and 512-bit primes `p` and `q`. Also an AES key is generated.
- `encrypt()` encrypts a message with this RSA, then with AES CBC, using padding scheme PKCS7.
- `decrypt()` decrypts a cipher with AES CBC, then checks if the padding is correct. It returns 0 if correct and -1 if not.
- When `main()` is called, ciphers can be checked if they are valid ciphers from AES CBC.

# Method
The AES CBC, along with the decryption validation service, is the standard [padding oracle attack](https://en.wikipedia.org/wiki/Padding_oracle_attack#Padding_oracle_attack_on_CBC_encryption) ([more detailed description and method](https://robertheaton.com/2013/07/29/padding-oracle-attack/)).
```python
def oracle(iv, c_blks):
    con.sendlines(['2', ''.join(iv_c_blks).encode('hex')])
    return con.recvlines(8)[7] == '0'

def set_ch(s, pos, ch):
    return s[:pos] + ch + s[pos+1:]

def attack(iv, cipher):
    num_blks = len(cipher) // 16
    c_blks = [cipher[i:i+16] for i in range(0, len(cipher), 16)]
    iv_c_blks = [iv] + c_blks
    p_blks = ['-' * 16] * num_blks
    for blk in range(num_blks, 0, -1):
        orig_c_blk = iv_c_blks[blk-1]
        i_blk = '-' * 16
        for pos in range(15, -1, -1):
            if pos == 15:
                iv_c_blks[blk-1] = set_ch(iv_c_blks[blk-1], pos-1, chr(ord(iv_c_blks[blk-1][pos-1]) ^ 1))
            for qos in range(pos+1, 16): iv_c_blks[blk-1] = set_ch(iv_c_blks[blk-1], qos, chr((16 - pos) ^ ord(i_blk[qos])))
            found = False
            for byte in range(256):
                iv_c_blks[blk-1] = set_ch(iv_c_blks[blk-1], pos, chr(byte))
                if oracle(iv_c_blks[0], iv_c_blks[1:blk+1]): # change according to chal
                    found = True
                    i_blk = set_ch(i_blk, pos, chr(byte ^ (16 - pos)))
                    p_blks[blk-1] = set_ch(p_blks[blk-1], pos, chr(ord(orig_c_blk[pos]) ^ ord(i_blk[pos])))
                    break
            if not found:
                return
            iv_c_blks[blk-1] = orig_c_blk
    return ''.join(p_blks)
```
Only the RSA is left. After attacking a few times, we realise that the AES-decrypted text (still RSA-encrypted), `flag**3`, is still the same, even for different moduli. This tells us that it is the actual value of `flag**3` (after unpadding), without having to take modulo `n`. We use Newton's method to find the cube root (analogous to [integer square root](https://en.wikipedia.org/wiki/Integer_square_root#Using_only_integer_division) for [Residues](../Residues/Writeup.md#Method)). The value of `flag**3` is roughly `2**474`, so set the initial estimate to r = 2**158`.

# Solution
[soln.py](soln.py)
```python
from pwn import *

con = remote('challs.hats.sg', 1401)
cflag = con.recvlines(5)[3].decode('hex')
iv, cipher = cflag[:16], cflag[16:]
flag3 = attack(iv, cipher).encode('hex') # 05c18ed821a2930f6284119af9122dad7ebbe709e5b1580983fbb0edc0b558fb309e9a02618621c4fe9399df6b866973cd1034dcfcd4140f5c0c096504040404

flag3 = int(flag3[:-8], 16)
print len(bin(flag3)[2:]) # 475
r = 2**158
while r**3 != flag3:
    r = (r*2 + flag3//(r*r)) // 3
print hex(r)[2:].decode('hex') # HATS{f14g_t00_sh0rt}
```
Decoding the cube root through hex gives the flag: `HATS{f14g_t00_sh0rt}`.
