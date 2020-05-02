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
