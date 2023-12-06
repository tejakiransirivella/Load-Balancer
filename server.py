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
        self.file = open(f'logs\\servers\\server_{identity}.txt', 'w')

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
                print(f"Sending response to Client Id - {identity}", file=self.file, flush=True)
                self.socket_clients.close()

    def receive_request(self):
        time.sleep(5)
        while True:
            try:
                request = self.socket_balancer.recv(2048)
                request = pickle.loads(request)
                print(f"Received request from Client id - {request.identity}", file=self.file, flush=True)
                self.queue.append([request.port, request.identity])
                print(f"Queue size - {len(self.queue)}", file=self.file, flush=True)
            except Exception as e:
                print()

    def balancer_response(self):
        self.socket_balancer.connect(('localhost', self.balancer_port))
        while True:
            response = ServerResponse(self.identity, len(self.queue))
            print(f"Status update {str(response)} sent to the Load Balancer", file=self.file, flush=True)
            response = pickle.dumps(response)
            self.socket_balancer.sendall(response)
            time.sleep(self.wait_time)


def main():
    if len(sys.argv) != 5:
        print("Insufficient arguments")
        print("Usage: server.py <id> <port> <load-balancer port> <queue update interval>")
        return

    server = CustomServer(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    update_balancer_thread = threading.Thread(target=server.balancer_response, name=f"SERVER_{sys.argv[1]}-update_balancer")
    receive_thread = threading.Thread(target=server.receive_request, name=f"SERVER_{sys.argv[1]}-receive_cl_req")
    response_thread = threading.Thread(target=server.client_response, name=f"SERVER_{sys.argv[1]}-respond_cl")
    update_balancer_thread.start()
    receive_thread.start()
    response_thread.start()


if __name__ == '__main__':
    main()
