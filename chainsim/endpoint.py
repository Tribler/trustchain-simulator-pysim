from simpy import Store

from ipv8.test.mocking.endpoint import AutoMockEndpoint, internet


class PySimEndpoint(AutoMockEndpoint):

    def __init__(self, env):
        super().__init__()
        self.env = env
        self.msg_queue = Store(env)
        self.env.process(self.process_messages())
        self.bytes_up = 0
        self.bytes_down = 0

    def process_messages(self):
        while True:
            from_address, packet = yield self.msg_queue.get()
            self.bytes_down += len(packet)
            self.notify_listeners((from_address, packet))

    def send(self, socket_address, packet):
        if socket_address in internet:
            # For the unit tests we handle messages in separate asyncio tasks to prevent infinite recursion.
            ep = internet[socket_address]
            self.bytes_up += len(packet)
            ep.msg_queue.put((self.wan_address, packet))
        else:
            raise AssertionError("Received data from unregistered address %s" % repr(socket_address))
