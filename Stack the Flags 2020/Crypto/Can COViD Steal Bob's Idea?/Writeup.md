# Description

Bob wants Alice to help him design the stream cipher's keystream generator base on his rough idea. Can COViD steal Bob's "protected" idea?

# Files

[crypto-challenge-1.pcapng](crypto-challenge-1.pcapng)

# Method

To handle the `pcapng` file, we open it in WireShark. We can extract the following text:

> `p = 298161833288328455288826827978944092433`\
> `g = 216590906870332474191827756801961881648`\
> `g^a = 181553548982634226931709548695881171814`\
> `g^b = 64889049934231151703132324484506000958`\
> `Hi Alice, could you please help me to design a keystream generator according to the file I share in the file server so that I can use it to encrypt my 500-bytes secret message? Please make sure it run with maximum period without repeating the keystream. The password to protect the file is our shared Diffie-Hellman key in digits. Thanks.`

As stated in the message, this is the usual set-up for a Diffie-Hellman key exchange, and we are given the publically-known parameters. The challenge also mentions that the flag is just a number wrapped in the flag format `govtech-csg{numeric-string}`, so we can safely take it that the shared key, `g^(ab)`, is required.

The most efficient way to solve the Diffie-Hellman problem is to take the discrete logarithm, in particular to find what the private exponents, `a` and `b` are. To do this we utilise the `discrete_log` function in the [SageMath](https://www.sagemath.org/) software. As the given parameters do not have too large an order of magnitude, it would not take too long to execute the program.

Since the modulus, `p` is prime, we take the parameters as elements on the Galois Field of order `p`.

```py
p = 298161833288328455288826827978944092433
g = 216590906870332474191827756801961881648
g_a = 181553548982634226931709548695881171814
g_b = 64889049934231151703132324484506000958

F = GF(p)
a = discrete_log(F(g_a), F(g))
b = discrete_log(F(g_b), F(g))
pow(g, a*b, p)
```

After several seconds of running the above in SageMath, we get the shared key pop out, `246544130863363089867058587807471986686`. Simply wrap it in the required flag format.

# Flag

> `govtech-csg{246544130863363089867058587807471986686}`
