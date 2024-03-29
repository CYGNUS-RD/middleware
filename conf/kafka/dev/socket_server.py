#!/usr/bin/env python3

import socket

IP = '127.0.0.1' # socket.gethostbyname(socket.gethostname())
PORT = 9091
ADDR = (IP, PORT)
SIZE = 12582912
FORMAT = "utf-8"

def main():
    print("[STARTING] Server is starting.")
    """ Staring a TCP socket. """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """ Bind the IP and PORT to the server. """
    server.bind(ADDR)

    """ Server is listening, i.e., server is now waiting for the client to connected. """
    server.listen()
    print("[LISTENING] Server is listening.")
 
    while True:
        """ Server has accepted the connection from the client. """
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")

        """ Receiving the filename from the client. """
        filename = conn.recv(SIZE).decode(FORMAT)
        print(f"[RECV] Receiving the filename.")
        # file = open(filename, "w")
        conn.send("Filename received.".encode(FORMAT))

        """ Receiving the file data from the client. """
        #data = conn.recv(SIZE).decode(FORMAT)
        data = conn.recv(SIZE)
        print(f"[RECV] Receiving the file data.")
        # file.write(data)
        with open(filename, 'wb') as f:
            while True:
                data = s.recv(1024)
                if not data:
                    break
                f.write(data)
        
        # with open(filename, "wb") as f:
        #         f.write(data)
        conn.send("File data received".encode(FORMAT))

        """ Closing the file. """
        # file.close()
        f.close()

        """ Closing the connection from the client. """
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")

if __name__ == "__main__":
    main()
