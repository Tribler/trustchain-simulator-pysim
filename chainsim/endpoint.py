import random

from simpy import Store

from ipv8.test.mocking.endpoint import AutoMockEndpoint, internet


class PySimEndpoint(AutoMockEndpoint):

    def __init__(self, env, send_fail_probability):
        super().__init__()
        self.env = env
        self.msg_queue = Store(env)
        self.env.process(self.process_messages())
        self.bytes_up = 0
        self.bytes_down = 0
        self.send_fail_probability = send_fail_probability
        self.overlay = None

    def process_messages(self):
        while True:
            from_address, packet = yield self.msg_queue.get()
            self.bytes_down += len(packet)
            self.notify_listeners((from_address, packet))

    def pass_payload(self, from_peer, socket_address, msg_id, payload):
        endpoint = internet[socket_address]
        if msg_id == 1:  # Half block payload
            # TODO bytes up!
            endpoint.overlay.process_half_block_payload(from_peer, payload)
        elif msg_id == 2:  # Crawl request
            self.bytes_up += 257
            endpoint.overlay.process_crawl_request(from_peer, payload)
        elif msg_id == 3:  # Crawl response
            # TODO bytes up!
            endpoint.overlay.process_crawl_response_payload(from_peer, payload)
        elif msg_id == 4:  # Half block pair payload
            # TODO bytes up!
            endpoint.overlay.process_half_block_pair_payload(payload)
        elif msg_id == 5:  # Half block broadcast payload
            # TODO bytes up!
            endpoint.overlay.process_half_block_broadcast_payload(payload)
        elif msg_id == 6:  # Half block pair broadcast payload
            # TODO bytes up!
            endpoint.overlay.process_half_block_pair_payload(payload)

    def send(self, socket_address, packet):
        if socket_address in internet:
            # For the unit tests we handle messages in separate asyncio tasks to prevent infinite recursion.
            ep = internet[socket_address]
            self.bytes_up += len(packet)
            if random.random() > self.send_fail_probability:
                ep.msg_queue.put((self.wan_address, packet))
        else:
            raise AssertionError("Received data from unregistered address %s" % repr(socket_address))
