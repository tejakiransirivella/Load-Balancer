import random
import socket
import pickle
import sys
import threading
import time

from model.ClientRequest import ClientRequest


class CustomClient:
    def __init__(self, identity, port, balancer_port):
        self.port = port
        self.identity = identity
        self.balancer_port = balancer_port
        self.socket_send = None
        self.socket_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file = open(f'logs\\clients\\client_{identity}.txt', 'w')
        self.request_count = 0

    def receive_response(self):
        self.socket_receive.bind(('localhost', self.port))
        self.socket_receive.listen(10)
        while True:
            server_socket, server_address = self.socket_receive.accept()
            response = server_socket.recv(2048)
            response = pickle.loads(response)
            if response.identity == self.identity:
                print("Response received", file=self.file, flush=True)

    def send_request(self):
        time.sleep(2)
        while True:
            try:
                self.socket_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_send.connect(('localhost', self.balancer_port))
                request = ClientRequest(self.identity, self.port)
                request = pickle.dumps(request)
                self.socket_send.sendall(request)

                self.request_count += 1
                print(f"Sent request {self.request_count} to the server", file=self.file, flush=True)
                # lock.release()
                self.socket_send.close()
                time.sleep(random.randint(1, 10))
            except Exception as e:
                print()

def main():
    if len(sys.argv) != 4:
        print("Insufficient arguments")
        print("Usage: client.py <id> <port> <load-balancer port>")
        return

    client = CustomClient(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    f = open(f'logs\\clients\\client_{sys.argv[1]}.txt', 'w')

    send_thread = threading.Thread(target=client.send_request)
    receive_thread = threading.Thread(target=client.receive_response)
    send_thread.start()
    receive_thread.start()


if __name__ == '__main__':
    main()
