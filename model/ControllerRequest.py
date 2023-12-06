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