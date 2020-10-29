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

        self.endpoint = PySimEndpoint(env, sim_settings)
        self.endpoint.open()

        self.my_peer = Peer(keypair, self.endpoint.wan_address)

        database = TrustchainMemoryDatabase(env)
        settings = TrustChainSettings()
        settings.crawl_batch_size = sim_settings.crawl_batch_size

        # Adjust settings based on the strategy
        if sim_settings.exchange_strategy == 0:
            settings.broadcast_fanout = 0
            settings.crawl_send_random_blocks = 0
        elif sim_settings.exchange_strategy == 1:
            settings.crawl_send_random_blocks = 5
            settings.broadcast_fanout = 0
        elif sim_settings.exchange_strategy == 2:
            settings.crawl_send_random_blocks = 0
            settings.broadcast_fanout = sim_settings.broadcast_fanout
        elif sim_settings.exchange_strategy == 3:
            settings.crawl_send_random_blocks = 5
            settings.broadcast_fanout = sim_settings.broadcast_fanout

        self.overlay = TrustChainCommunity(self.my_peer, self.endpoint, self.network,
                                           persistence=database, settings=settings, env=env,
                                           sim_settings=sim_settings, data_dir=data_dir)
        self.endpoint.overlay = self.overlay
