import socket


def Main():
    host = '128.138.145.145'  # client ip
    port = 62539

    server = ('10.201.82.132', 62539)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))

    message = input("-> ")
    while message != 'q':
        s.sendto(message.encode('utf-8'), server)
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print("Received from server: " + data)
        message = input("-> ")
    s.close()


if __name__ == '__main__':
    Main()