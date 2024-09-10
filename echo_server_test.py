"""
Server functions that allow us to communicate over sockets to control devices

author: Teddy Tortorici
"""

import time
import socket
import get


class EchoServer:

    shutdown_command = b"shutdown"

    """ADDRESSES"""
    addr_bridge = {"AH": 28, "HP": 5}
    addr_ls = {331: 13, 340: 12}

    def __init__(self):
        self.host_port = ("10.201.82.132", 62539)
        self.running = False
        print("Creating server.\n")

    def handle(self, message: str) -> str:
        """Parse a message of the format
        [Instrument ID]::[command]::[optional message]"""
        # print("\nHandling message:")
        return message[::-1]

    def run(self):
        """Establishes a socket server which takes and handles commands"""
        self.running = True
        # open a new socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.host_port)

            # confirm the socket is bound
            print(f"Socket bound to port: {self.host_port[1]}")

            # put the socket into listening mode
            s.listen()

            # loop until a client requests the server shutdown
            while self.running:
                # establish a connection with a client
                conn, addr = s.accept()
                with conn:
                    print(f"\nConnected to: {addr[0]}:{addr[1]}  : {time.ctime(time.time())}")
                    while True:
                        msg_client = conn.recv(1024)
                        # print(repr(msg_client))
                        if not msg_client:
                            break
                        elif msg_client == EchoServer.shutdown_command:
                            print("Received shutdown command")
                            self.running = False
                            break
                        else:
                            msg_client = msg_client.decode()
                            print(f"Received message: {msg_client}")
                            msg_server = self.handle(msg_client)
                            print(f"Sending back message: {msg_server}")
                            conn.sendall(msg_server.encode())


if __name__ == "__main__":
    import sys

    server = EchoServer()
    server.run()
