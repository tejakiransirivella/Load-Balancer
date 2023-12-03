"""
    Implemented the load balancer functionality to route the client request to appropriate servers and
    dynamically increase or decrease servers based on traffic
"""

import pickle
import socket
import sys
import time
from threading import *
from typing import List


class ServerUtil:
    """
     It stores the details of the server instance like server socket, server id and queue length
    """
    __slots__ = "server_socket", "identity", "queue_length"

    def __init__(self, server_socket: socket.socket = None, identity=None, queue_length=None):
        self.server_socket: socket.socket = server_socket
        self.identity = identity
        self.queue_length = queue_length

    def __str__(self):
        return "server identity = {},  Queue length = {}".format(self.identity, self.queue_length)


class ControllerRequest:
    """
    It is the request to the controller to up or down servers
    """
    __slots__ = "type", "identity"

    def __init__(self, type, identity):
        self.type = type
        self.identity = identity

    def __str__(self):
        return "type = {}, server identity = {}".format(self.type, self.identity)


class LoadBalancer:
    """
    It is a load balancer data class to store all ports and list of servers
    """
    __slots__ = "server_port", "client_port", "controller_port", "max_queue_length", "servers"

    def __init__(self, client_port, server_port, controller_port, max_queue_length):
        self.server_port = server_port
        self.client_port = client_port
        self.controller_port = controller_port
        self.max_queue_length = max_queue_length
        self.servers: List[ServerUtil] = []

    def accept_server_connection(self):
        """
         accepts the connection from the server and adds the server to the list.
        """
        while True:
            lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            lb_socket.bind(('localhost', self.server_port))
            lb_socket.listen(10)
            server_socket, server_address = lb_socket.accept()
            server_response = self.parse_response(server_socket)
            server_util = ServerUtil(server_socket, server_response.identity, server_response.queue_length)
            print("============Received connection from Server=====================")
            print("============="+str(server_util)+"=============")
            self.servers.append(server_util)

    def parse_response(self, socket):
        """
        receives the response and parses it.
        :param socket: client or server socket
        :return: parsed response
        """
        response = socket.recv(2048)
        response = pickle.loads(response)
        return response

    def receive_server_response(self):
        """
        updates the queue length of the server from server response.
        """
        while True:
            for server in self.servers:
                server_response = self.parse_response(server.server_socket)
                server.queue_length = server_response.queue_length
                print("=================Updated Queue Length==============")
                print(str(server))

    def apply_shortest_queue(self):
        """
        finds the server that has the shortest queue length
        :return: server
        """
        shortest_server = ServerUtil(identity=sys.maxsize, queue_length=sys.maxsize)
        for server in self.servers:
            if server.queue_length < shortest_server.queue_length or \
                    (server.queue_length == shortest_server.queue_length and
                     server.identity < shortest_server.identity):
                shortest_server = server

        return shortest_server

    def send_client_request(self):
        """
         gets client request, finds the server to redirect to and sends the packet to appropriate server
        """
        while True:
            lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            lb_socket.bind(('localhost', self.client_port))
            lb_socket.listen(10)
            client_socket, client_address = lb_socket.accept()
            client_response = self.parse_response(client_socket)
            client_request = pickle.dumps(client_response)
            server = self.apply_shortest_queue()
            server.server_socket.sendall(client_request)
            server.queue_length += 1
            print("========= redirection ==================")
            print("Client Id - {} sent to Server id - {} Queue length - {}".
                  format(client_response.identity, server.identity, server.queue_length))
            lb_socket.close()

    def send_controller_request(self):
        """
        Sends request to controller to increase or decrease the servers based on traffic
        """
        lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lb_socket.connect(("localhost", self.controller_port))

        while True:
            for server in self.servers:
                if server.queue_length > 0.9 * self.max_queue_length:
                    controller_request = ControllerRequest(0, None)
                    controller_request = pickle.dumps(controller_request)
                    lb_socket.sendall(controller_request)
                    print("=========Request to increase the server===========")
                    print(str(controller_request))
                    break
                if server.queue_length == 0:
                    controller_request = ControllerRequest(1, server.identity)
                    controller_request = pickle.dumps(controller_request)
                    lb_socket.sendall(controller_request)
                    self.servers.remove(server)
                    print("=========Request to remove the server===========")
                    print("Removed Server Id - {}".format(server.identity))
                    break
            time.sleep(5)


def main():
    """
     Initializes 4 threads for client,controller,server and starts them.
    """
    if len(sys.argv) == 1:
        raise Exception("Expecting port argument")

    client_port = int(sys.argv[1])
    server_port = int(sys.argv[2])
    controller_port = int(sys.argv[3])
    max_queue_length = int(sys.argv[4])

    load_balancer = LoadBalancer(client_port, server_port, controller_port, max_queue_length)
    accept_server_conn_thread = Thread(target=load_balancer.accept_server_connection)
    receive_server_data_thread = Thread(target=load_balancer.receive_server_response)
    send_client_request_thread = Thread(target=load_balancer.send_client_request)
    send_controller_request_thread = Thread(target=load_balancer.send_controller_request)

    accept_server_conn_thread.start()
    receive_server_data_thread.start()
    send_client_request_thread.start()
    send_controller_request_thread.start()


main()
