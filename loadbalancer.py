"""
    Implemented the load balancer functionality to route the client request to appropriate servers and
    dynamically increase or decrease servers based on traffic
"""

import pickle
import socket
import sys
import threading
import time
from threading import *
from typing import List
from datetime import datetime
from model.ServerResponse import ServerResponse
from model.ClientRequest import ClientRequest
from model.ControllerRequest import ControllerRequest

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation


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


class LoadBalancer:
    """
    It is a load balancer data class to store all ports and list of servers
    """
    __slots__ = "server_port", "client_port", "controller_port", "max_queue_length", "lock", "servers"

    def __init__(self, client_port, server_port, controller_port, max_queue_length, lock):
        self.server_port = server_port
        self.client_port = client_port
        self.controller_port = controller_port
        self.max_queue_length = max_queue_length
        self.servers: List[ServerUtil] = []
        self.lock = lock

    def __str__(self):
        output = f"==================================\n"
        output += "        Server count  {}\n".format(len(self.servers))
        output += "----------------------------------\n"
        output += "{:15s} | {:15s}\n".format("Server Id", "Request Count")
        output += "----------------------------------\n"
        for server in self.servers:
            output += "{:15d} | {:15d}\n".format(server.identity, server.queue_length)
        output += "==================================\n"
        return output

    def accept_server_connection(self):
        """
         accepts the connection from the server and adds the server to the list.
        """
        lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lb_socket.bind(('localhost', self.server_port))
        lb_socket.listen(10)
        while True:
            server_socket, server_address = lb_socket.accept()
            server_response = self.parse_response(server_socket)
            server_util = ServerUtil(server_socket, server_response.identity, server_response.queue_length)
            self.servers.append(server_util)

    def parse_response(self, socket):
        """
        receives the response and parses it.
        :param socket: client or server socket
        :return: parsed response
        """
        response = None

        try:
            response = socket.recv(2048)
            response = pickle.loads(response)
        except ConnectionResetError:
            print("LOADBALANCER: Socket was closed")

        return response

    def receive_server_response(self):
        """
        updates the queue length of the server from server response.
        """
        while True:
            for server in self.servers:
                server_response = self.parse_response(server.server_socket)
                if server_response is not None:
                    server.queue_length = server_response.queue_length

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
        try:
            lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            lb_socket.bind(('localhost', self.client_port))
            lb_socket.listen(10)
            while True:
                if len(self.servers) > 0:
                    client_socket, client_address = lb_socket.accept()
                    client_response = self.parse_response(client_socket)
                    client_socket.close()
                    client_request = pickle.dumps(client_response)
                    self.lock.acquire()
                    server = self.apply_shortest_queue()
                    server.server_socket.sendall(client_request)
                    self.lock.release()
                    server.queue_length += 1
        except Exception as e:
            print("LOADBALANCER: Connection was closed")

    def send_controller_request(self):
        """
        Sends request to controller to increase or decrease the servers based on traffic
        """
        time.sleep(10)
        lb_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lb_socket.connect(("localhost", self.controller_port))

        while True:
            for server in self.servers:
                if server.queue_length > 0.9 * self.max_queue_length:
                    controller_request = ControllerRequest(0, None)
                    serialized_controller_request = pickle.dumps(controller_request)
                    lb_socket.sendall(serialized_controller_request)
                    break
                if server.queue_length == 0 and len(self.servers) > 1:
                    controller_request = ControllerRequest(1, server.identity)
                    controller_request = pickle.dumps(controller_request)
                    lb_socket.sendall(controller_request)
                    self.servers.remove(server)
                    break

            time.sleep(5)

    def display_info(self):
        """
        displays the server id's and their job count
        """
        while True:
            time.sleep(1)
            print(self)


def animate(frame, time_data, servers_data, load_balancer, ax):
    """
        plots the graph based on time and number of servers
    """
    time_data.append(datetime.now())
    servers_data.append(len(load_balancer.servers))
    ax.clear()
    ax.set_xlabel('Time')
    ax.set_ylabel("Servers count")
    ax.set_title("Servers count over time")
    line = ax.plot(time_data, servers_data)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    return line


def create_real_time_plot(load_balancer):
    """
        initializes the plot and calls funcanimation that calls animate function every 1 second
    """
    matplotlib.use('TkAgg')
    time_data = []
    servers_data = []
    fig, ax = plt.subplots()

    ani = FuncAnimation(fig, animate, interval=1000, cache_frame_data=False,
                        fargs=(time_data, servers_data, load_balancer, ax))
    plt.show()


def main():
    """
     Initializes 4 threads for client,controller,server and starts them.
    """
    print("LB started")
    if len(sys.argv) == 1:
        raise Exception("Expecting port argument")

    client_side_port = int(sys.argv[1])
    server_side_port = int(sys.argv[2])
    controller_port = int(sys.argv[3])
    max_queue_length = int(sys.argv[4])

    load_balancer = LoadBalancer(client_side_port, server_side_port, controller_port, max_queue_length,
                                 threading.Lock())
    accept_server_conn_thread = Thread(target=load_balancer.accept_server_connection)
    receive_server_data_thread = Thread(target=load_balancer.receive_server_response)
    send_client_request_thread = Thread(target=load_balancer.send_client_request)
    send_controller_request_thread = Thread(target=load_balancer.send_controller_request)
    display_info_thread = Thread(target=load_balancer.display_info)

    accept_server_conn_thread.start()
    receive_server_data_thread.start()
    send_client_request_thread.start()
    send_controller_request_thread.start()
    display_info_thread.start()

    create_real_time_plot(load_balancer)


if __name__ == "__main__":
    main()
