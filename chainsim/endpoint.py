import random

from simpy import Store

from ipv8.test.mocking.endpoint import AutoMockEndpoint, internet


class PySimEndpoint(AutoMockEndpoint):

    def __init__(self, env, settings):
        super().__init__()
        self.env = env
        self.msg_queue = Store(env)
        self.env.process(self.process_messages())
        self.bytes_up = 0
        self.bytes_down = 0
        self.settings = settings
        self.send_fail_probability = settings.send_fail_probability
        self.overlay = None

    def process_messages(self):
        while True:
            from_address, packet = yield self.msg_queue.get()
            self.bytes_down += len(packet)
            self.notify_listeners((from_address, packet))

    def pass_payload(self, from_peer, socket_address, msg_id, payload):
        endpoint = internet[socket_address]
        if random.random() <= self.send_fail_probability:
            return

        if msg_id == 1:  # Half block payload
            msg_len = 365 + 32 * len(payload.previous_hash_set)
            self.bytes_up += msg_len
            endpoint.bytes_down += msg_len
            endpoint.overlay.process_half_block_payload(from_peer, payload)
        elif msg_id == 2:  # Crawl request
            msg_len = 257
            self.bytes_up += msg_len
            endpoint.bytes_down += msg_len
            endpoint.overlay.process_crawl_request(from_peer, payload)
        elif msg_id == 3:  # Crawl response
            msg_len = 379 + 32 * len(payload.block.previous_hash_set)
            self.bytes_up += msg_len
            endpoint.bytes_down += msg_len
            endpoint.overlay.process_crawl_response_payload(from_peer, payload)
        elif msg_id == 4:  # Half block pair payload
            msg_len = 707 + 32 * len(payload.previous_hash_set1) + 32 * len(payload.previous_hash_set2)
            self.bytes_up += msg_len
            endpoint.bytes_down += msg_len
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
