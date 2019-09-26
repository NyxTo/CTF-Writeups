from pwn import *

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
