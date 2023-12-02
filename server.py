import socket
import pickle
import time
import threading


class ServerResponse:
    def __init__(self, identity, queue_length):
        self.identity = identity
        self.queue_length = queue_length
        # Can add more if we have time


class ClientResponse:
    def __init__(self, identity):
        self.identity = identity
        # Can add more if we have time


class CustomServer:
    def __init__(self, identity, port, balancer_port, wait_time):
        self.queue = []
        self.identity = identity
        self.port = port
        self.wait_time = wait_time
        self.socket_balancer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_clients = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.balancer_port = balancer_port
        self.socket_clients.listen(1)

    def client_response(self):
        while True:
            while len(self.queue) > 0:
                first = self.queue.pop(0)
                identity = first[1]
                self.socket_clients.connect(('localhost', first[0]))
                response = ClientResponse(identity)
                response = pickle.dumps(response)
                self.socket_clients.sendall(response)
                self.socket_clients.close()

    def receive_request(self):
        while True:
            client_socket, client_address = self.socket_clients.accept()
            request = client_socket.recv(self.port)
            request = pickle.loads(request)
            self.queue.append([request.port, request.identity])

    def balancer_response(self):
        while True:
            self.socket_balancer.connect(('localhost', self.balancer_port))
            response = ServerResponse(self.identity, len(self.queue))
            response = pickle.dumps(response)
            self.socket_balancer.sendall(response)
            self.socket_balancer.close()
            time.sleep(self.wait_time)


def main():
    server = CustomServer
    update_balancer_thread = threading.Thread(target=server.balancer_response)
    receive_thread = threading.Thread(target=server.receive_request)
    response_thread = threading.Thread(target=server.client_response)
    update_balancer_thread.start()
    receive_thread.start()
    response_thread.start()


if __name__ == '__main__':
    main()
