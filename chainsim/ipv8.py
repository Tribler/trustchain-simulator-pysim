from chainsim.endpoint import PySimEndpoint
from chainsim.trustchain_mem_db import TrustchainMemoryDatabase

from ipv8.attestation.trustchain.community import TrustChainCommunity
from ipv8.attestation.trustchain.settings import TrustChainSettings
from ipv8.keyvault.crypto import default_eccrypto
from ipv8.peer import Peer
from ipv8.peerdiscovery.network import Network


class SimulatedIPv8(object):

    def __init__(self, sim_settings, env, data_dir):
        keypair = default_eccrypto.generate_key("curve25519")
        self.network = Network()

        self.endpoint = PySimEndpoint(env, sim_settings.send_fail_probability)
        self.endpoint.open()

        self.my_peer = Peer(keypair, self.endpoint.wan_address)

        database = TrustchainMemoryDatabase(env)
        settings = TrustChainSettings()
        settings.broadcast_fanout = sim_settings.broadcast_fanout
        settings.crawl_batch_size = sim_settings.crawl_batch_size
        self.overlay = TrustChainCommunity(self.my_peer, self.endpoint, self.network,
                                           persistence=database, settings=settings, env=env,
                                           sim_settings=sim_settings, data_dir=data_dir)
