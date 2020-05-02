# Task
ShoppingBaba uses a chat server to interact with their suppliers.\
Their suppliers connects to this chat server by using a client python script. Upon connecting, the server usually will provide the supplier with a random username with password for login purposes.\
However, suppliers now complain that the connection ends too quickly and they can no longer login!

Investigate the client script and connect to p7ju6oidw6ayykt9zeglwyxired60yct.ctf.sg:21011 to get to the bottom of this!

**Files:** [client.py](client.py)

# Source Code
Important parts of `client.py` (edited):
```py
# usage: $ python client.py <server_address> <server_port>
server_address = (sys.argv[1], int(sys.argv[2]))
sock.connect(server_address)

data = sock.recv(1024) # Welcome to ShoppingBaba Supplier's Chat Server!
sock.sendall("shake_baba")

data = sock.recv(1024) # random English word
sock.sendall(str(hash(data)))

data = sock.recv(1024) # random English word
sock.sendall("Hello!")

data = sock.recv(1024)
```

# Method
When I combed through to condense what `client.py` _actually_ does, I found out that... it does nothing much at all. It first sends `"shake_baba"`. After playing around with directly calling netcat on the server and port `nc p7ju6oidw6ayykt9zeglwyxired60yct.ctf.sg 21011`, I discovered the exact string doesn't matter at all - it just needs an initial response.

The next thing I noticed from running `client.py` was that it receives some English word, sends the numerical `hash()` of the word (as a string), and then received another English word. On the netcat, entering any string other than the `hash()` terminated the connection (with a `"Wrong hash!"` response if I entered a number). Only sending the `hash()` would keep the connection up, and that led to receiving another English word. This piques my curiosity, so I tried again to send the hash, receiving another English word, for a couple more iterations.

From there, what I had to do was clear. Make the client send the `hash()` every time it receives a word, and - hopefully - after enough iterations something would change. To my surprise, what changed was that the flag popped out.

# Solution
[soln.py](soln.py)
```py
import socket, sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (sys.argv[1], int(sys.argv[2]))
sock.connect(server_address)

sock.recv(1024)
sock.sendall("shake_baba or actually really any string")

for _ in range(500): # sufficient, usually around 1<<8 == 2**8 == 256
    data = sock.recv(1024)
    if data == "":
        break
    print data # bunch of English words, then flag
    sock.sendall(str(hash(data)))

sock.close()
```
