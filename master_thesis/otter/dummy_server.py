
import socket



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_address = ('localhost', 2009)
print ("[+] Server IP {} | Port {}".format(server_address[0],server_address[1]))
sock.bind(server_address)

sock.listen(1)

while True:
    print("[+] Waiting for a client connection")
    connection, client_address = sock.accept()

    try:
        print("[+] Connection from", client_address)

        while True:
            data = connection.recv(1024)
            print("Received", data)
            if data:
                print("Sending data back to client")
                connection.sendall(data)
            else:
                print("No more data from", client_address)
                break
    finally:
        connection.close()
