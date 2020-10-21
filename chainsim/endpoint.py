from simpy import Store

from ipv8.test.mocking.endpoint import AutoMockEndpoint, internet


class PySimEndpoint(AutoMockEndpoint):

    def __init__(self, env):
        super().__init__()
        self.env = env
        self.msg_queue = Store(env)
        self.env.process(self.process_messages())

    def process_messages(self):
        while True:
            # Receive message
            from_address, packet = yield self.msg_queue.get()
            self.notify_listeners((from_address, packet))

    def send(self, socket_address, packet):
        if socket_address in internet:
            # For the unit tests we handle messages in separate asyncio tasks to prevent infinite recursion.
            ep = internet[socket_address]
            ep.msg_queue.put((self.wan_address, packet))
        else:
            raise AssertionError("Received data from unregistered address %s" % repr(socket_address))
