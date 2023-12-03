import socket
import pickle
import sys
import threading


class ClientRequest:
    def __init__(self, identity, port_in_use):
        self.identity = identity
        self.port = port_in_use
        # Can add more if we have time


class CustomClient:
    def __init__(self, identity, port, balancer_port):
        self.port = port
        self.identity = identity
        self.balancer_port = balancer_port
        self.socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket_receive.listen(1)

    def receive_response(self):
        while True:
            self.socket_receive.bind(('localhost', self.port))
            self.socket_receive.listen()
            server_socket, server_address = self.socket_receive.accept()
            response = server_socket.recv()
            response = pickle.loads(response)
            if response.identity == self.identity:
                print("Correct response received")

    def send_request(self):
        while True:
            request = ClientRequest(self.identity, self.port)
            request = pickle.dumps(request)
            self.socket_send.connect(('localhost', self.balancer_port))
            self.socket_send.sendall(request)
            self.socket_send.close()


def main():

    if len(sys.argv) != 4:
        print("Insufficient arguments")
        print("Usage: client.py <id> <port> <load-balancer port>")
        return

    client = CustomClient(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    send_thread = threading.Thread(target=client.send_request)
    receive_thread = threading.Thread(target=client.receive_response)
    send_thread.start()
    receive_thread.start()


if __name__ == '__main__':
    main()
