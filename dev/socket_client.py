#!/usr/bin/env python3

import socket

IP = '127.0.0.1' # socket.gethostbyname(socket.gethostname())
PORT = 9091
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 12582912

def main():
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """ Connecting to the server. """
    client.connect(ADDR)

    """ Opening and reading the file data. """
    file = open("/tmp/LNGS_1680689750_36.dat", "rb")
    data = file.read()

    """ Sending the filename to the server. """
    client.send("LNGS_1680689750_36.dat".encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {msg}")

    """ Sending the file data to the server. """
    client.sendall(data)
    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {msg}")

    """ Closing the file. """
    file.close()

    """ Closing the connection from the server. """
    client.close()


if __name__ == "__main__":
    main()