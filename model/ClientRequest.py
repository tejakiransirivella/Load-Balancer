class ClientRequest:
    def __init__(self, identity, port_in_use):
        self.identity = identity
        self.port = port_in_use
        # Can add more if we have time

    def __str__(self):
        return "Client Id - {}, Client Port - {}".format(self.identity,self.port)