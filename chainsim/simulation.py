import os
import random
import shutil
import time
from binascii import hexlify

import yappi

import chainsim.globals as global_vars
from chainsim.ipv8 import SimulatedIPv8
from chainsim.parse import parse_data


class TrustChainSimulation:
    """
    Represents a simulation with some settings.
    """

    def __init__(self, settings, env):
        self.settings = settings
        self.env = env
        self.nodes = []
        self.data_dir = os.path.join("data", "n_%d_b_%d_link_%.1f_f_%d" % (self.settings.peers,
                                                                           self.settings.back_pointers,
                                                                           self.settings.send_fail_probability,
                                                                           self.settings.broadcast_fanout))

    def start_ipv8_nodes(self):
        for peer_ind in range(1, self.settings.peers + 1):
            if peer_ind % 100 == 0:
                print("Created %d peers..." % peer_ind)
            ipv8 = SimulatedIPv8(self.settings, self.env, self.data_dir)
            self.nodes.append(ipv8)

    def setup_directories(self):
        if os.path.exists(self.data_dir):
            shutil.rmtree(self.data_dir)
        os.makedirs(self.data_dir, exist_ok=True)

    def ipv8_discover_peers(self):
        # Let nodes discover each other
        for node_a in self.nodes:
            connect_nodes = random.sample(self.nodes, min(100, len(self.nodes)))
            for node_b in connect_nodes:
                if node_a == node_b:
                    continue

                node_a.network.add_verified_peer(node_b.my_peer)
                node_a.network.discover_services(node_b.my_peer, [node_a.overlay.master_peer.mid, ])

    def write_bandwidth_statistics(self):
        # Write bandwidth statistics
        total_bytes_up = 0
        total_bytes_down = 0
        with open(os.path.join(self.data_dir, "bandwidth.csv"), "w") as bw_file:
            bw_file.write("public_key,bytes_up,bytes_down\n")
            for node in self.nodes:
                total_bytes_up += node.endpoint.bytes_up
                total_bytes_down += node.endpoint.bytes_down
                bw_file.write("%s,%d,%d\n" % (
                    hexlify(node.my_peer.public_key.key_to_bin()).decode(), node.endpoint.bytes_up,
                    node.endpoint.bytes_down))

        with open(os.path.join(self.data_dir, "total_bandwidth.csv"), "w") as bw_file:
            bw_file.write("%d,%d" % (total_bytes_up, total_bytes_down))

    def start_simulation(self, run_yappi=False):
        # Start crawling and creating interactions
        for node in self.nodes:
            self.env.process(node.overlay.start_crawling())
            self.env.process(node.overlay.create_random_interactions())

        print("Starting simulation with %d peers..." % self.settings.peers)

        if run_yappi:
            yappi.start(builtins=True)

        start_time = time.time()
        for second in range(1, self.settings.max_duration + 1):
            self.env.run(until=second * 1000)

            num_exposed = len(global_vars.exposed_peers)
            print("Simulated %d seconds... (peers that committed fraud: %d, exposed: %d)" % (
            second, global_vars.peers_committed_fraud, num_exposed))
            if num_exposed == self.settings.peers:
                break

        self.write_bandwidth_statistics()

        # Write total experiment duration
        with open(os.path.join(self.data_dir, "duration.txt"), "w") as out_file:
            out_file.write("%d" % self.env.now)

        print("Simulation took %f seconds" % (time.time() - start_time))

        if run_yappi:
            yappi.stop()
            yappi_stats = yappi.get_func_stats()
            yappi_stats.sort("tsub")
            yappi_stats.save("yappi.stats", type='callgrind')

    def run(self, yappi=False):
        self.setup_directories()
        self.start_ipv8_nodes()
        self.ipv8_discover_peers()
        self.start_simulation(run_yappi=yappi)
        parse_data(self.data_dir)
