import socket
import pickle


class ClientRequest:
    def __init__(self, identity):
        self.identity = identity
        # Can add more if we have time


class CustomClient:
    def __init__(self, port, identity, balancer_port):
        self.port = port
        self.identity = identity
        self.balancer_port = balancer_port
        self.socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_receive.listen(1)

    def receive_response(self):
        while True:
            server_socket, server_address = self.socket_receive.accept()
            response = server_socket.recv(self.port)
            response = pickle.loads(response)
            if response.identity == self.identity:
                print("Correct response received")

    def send_request(self):
        while True:
            request = ClientRequest(self.identity)
            request = pickle.dumps(request)
            self.socket_send.connect(('localhost', self.balancer_port))
            self.socket_send.sendall(request)
            self.socket_send.close()
