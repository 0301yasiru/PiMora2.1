import socket
import threading


def sending_function(conn):
    while True:
        data = input().strip().encode('utf-8')
        conn.send(data)


def receving_function(conn):
    while True:
        data = conn.recv(1024)
        print("RECEVED > " + data.decode('utf-8'))

HOST = "192.168.8.102"
PORT = 4545

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))

    server.listen()

    conn, addr = server.accept()

    print(f"Connection from -> {addr[0]} | {addr[1]}")

    sending_thread = threading.Thread(target=sending_function, args=(conn,))
    receving_thread = threading.Thread(target=receving_function, args=(conn,))

    sending_thread.start()
    receving_thread.start()

    sending_thread.join()
    receving_thread.join()

if __name__ == '__main__':
    main()