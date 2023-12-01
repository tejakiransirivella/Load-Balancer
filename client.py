import socket
import pickle


class CustomClient:
    def __init__(self, port, identity):
        self.port = port
        self.identity = identity
