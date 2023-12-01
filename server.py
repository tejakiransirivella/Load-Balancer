import socket


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
    def __init__(self, id):
        self.queue = []
        self.id = id

    def client_response(self):
        print("temp")

    def balancer_response(self):
        print("temp")

    