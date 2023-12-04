import socket
import pickle
import sys
import time
import threading
from model.ClientRequest import ClientRequest
from model.ClientResponse import ClientResponse
from model.ServerResponse import ServerResponse

class CustomServer:
    def __init__(self, identity, port, balancer_port, wait_time):
        self.queue = []
        self.identity = identity
        self.port = port
        self.wait_time = wait_time
        self.socket_balancer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_clients = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.balancer_port = balancer_port
        # self.socket_clients.listen()  # was 1

    def client_response(self):
        while True:
            while len(self.queue) > 0:
                self.socket_clients = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                first = self.queue.pop(0)
                identity = first[1]
                self.socket_clients.connect(('localhost', first[0]))
                response = ClientResponse(identity)
                response = pickle.dumps(response)
                self.socket_clients.sendall(response)
                print("Server | ===============Sent Response to Client==================")
                print("Server | From Server Id - {} to Client Id - {}".format(self.identity, identity))
                self.socket_clients.close()

    def receive_request(self):
        # client_socket, client_address = self.socket_clients.accept()
        time.sleep(5)
        print("server port - {}", self.port)
        # self.socket_balancer.bind(('localhost', self.port))
        # self.socket_balancer.listen(10)
        print("==========waiting for request from load balancer")
       # load_balancer_socket, address = self.socket_balancer.accept()
        while True:
            # client_socket, client_address = self.socket_clients.accept()
            request = self.socket_balancer.recv(2048)  # TODO need to check the passing of port here
            request = pickle.loads(request)
            print("Server | ==========Received Client Request from Load Balancer to Server Id - {} =============="
                  .format(self.identity))
            print(str(request))
            self.queue.append([request.port, request.identity])

    def balancer_response(self):
        self.socket_balancer.connect(('localhost', self.balancer_port))
        while True:
            # self.socket_balancer.connect(('localhost', self.balancer_port))
            response = ServerResponse(self.identity, len(self.queue))
            print("Server | =============Sending Updates to  Load Balancer==============")
            print("Server | {}".format(str(response)))
            response = pickle.dumps(response)
            self.socket_balancer.sendall(response)
            # self.socket_balancer.close()
            time.sleep(self.wait_time)


def main():
    if len(sys.argv) != 5:
        print("Insufficient arguments")
        print("Usage: server.py <id> <port> <load-balancer port> <queue update interval>")
        return

    server = CustomServer(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    update_balancer_thread = threading.Thread(target=server.balancer_response)
    receive_thread = threading.Thread(target=server.receive_request)
    response_thread = threading.Thread(target=server.client_response)
    update_balancer_thread.start()
    receive_thread.start()
    response_thread.start()


if __name__ == '__main__':
    main()
