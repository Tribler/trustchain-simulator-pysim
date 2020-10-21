import os
import random
import time

from simpy import Environment, Store

from chainsim.trustchain_mem_db import TrustchainMemoryDatabase
from ipv8.attestation.trustchain.community import TrustChainCommunity
from ipv8.attestation.trustchain.settings import TrustChainSettings
from ipv8.keyvault.crypto import default_eccrypto
from ipv8.peer import Peer
from ipv8.peerdiscovery.network import Network
from ipv8.test.mocking.endpoint import AutoMockEndpoint, internet

nodes = []


env = Environment()
NUM_PEERS = 100


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


class SimulatedIPv8(object):

    def __init__(self, env):
        keypair = default_eccrypto.generate_key("curve25519")
        self.network = Network()

        self.endpoint = PySimEndpoint(env)
        self.endpoint.open()

        self.my_peer = Peer(keypair, self.endpoint.wan_address)

        database = TrustchainMemoryDatabase(env)
        settings = TrustChainSettings()
        settings.broadcast_fanout = 10
        self.overlay = TrustChainCommunity(self.my_peer, self.endpoint, self.network, persistence=database, settings=settings, env=env)


for peer_ind in range(1, NUM_PEERS + 1):
    if peer_ind % 100 == 0:
        print("Created %d peers..." % peer_ind)
    ipv8 = SimulatedIPv8(env)
    nodes.append(ipv8)


# Let nodes discover each other
for node_a in nodes:
    connect_nodes = random.sample(nodes, 20)
    for node_b in connect_nodes:
        if node_a == node_b:
            continue

        node_a.network.add_verified_peer(node_b.my_peer)
        node_a.network.discover_services(node_b.my_peer, [node_a.overlay.master_peer.mid, ])


# Start crawling and creating interactions
for node in nodes:
    env.process(node.overlay.start_crawling())
    env.process(node.overlay.create_random_interactions())


if not os.path.exists("data"):
    os.mkdir("data")


if os.path.exists("data/detection_time.txt"):
    os.remove("data/detection_time.txt")

start_time = time.time()
for second in range(1, 10):
    env.run(until=second * 1000)
    print("Simulated %d seconds..." % second)

print("Simulation took %f seconds" % (time.time() - start_time))
