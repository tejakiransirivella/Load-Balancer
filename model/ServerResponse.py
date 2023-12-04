class ServerResponse:
    def __init__(self, identity, queue_length):
        self.identity = identity
        self.queue_length = queue_length
        # Can add more if we have time

    def __str__(self):
        return "Server id - {}, Queue length - {}".format(self.identity, self.queue_length)