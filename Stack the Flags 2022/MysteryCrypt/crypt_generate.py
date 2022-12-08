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
