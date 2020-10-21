import argparse
import os
import random
import shutil
import sys
import time
from binascii import hexlify

import yappi
from simpy import Environment

import chainsim.globals as global_vars
from chainsim.ipv8 import SimulatedIPv8
from chainsim.parse import parse_data

nodes = []


env = Environment()
NUM_PEERS = 100


def setup_directories():
    shutil.rmtree("data", ignore_errors=True)
    shutil.rmtree("logs", ignore_errors=True)
    os.mkdir("data")
    os.mkdir("logs")


def start_ipv8_nodes():
    for peer_ind in range(1, NUM_PEERS + 1):
        if peer_ind % 100 == 0:
            print("Created %d peers..." % peer_ind)
        ipv8 = SimulatedIPv8(env)
        nodes.append(ipv8)


def ipv8_discover_peers():
    # Let nodes discover each other
    for node_a in nodes:
        connect_nodes = random.sample(nodes, min(100, len(nodes)))
        for node_b in connect_nodes:
            if node_a == node_b:
                continue

            node_a.network.add_verified_peer(node_b.my_peer)
            node_a.network.discover_services(node_b.my_peer, [node_a.overlay.master_peer.mid, ])


def start_simulation(run_yappi=False):
    # Start crawling and creating interactions
    for node in nodes:
        env.process(node.overlay.start_crawling())
        env.process(node.overlay.create_random_interactions())

    print("Starting simulation with %d peers..." % NUM_PEERS)

    if run_yappi:
        yappi.start(builtins=True)

    start_time = time.time()
    for second in range(1, 600 + 1):
        env.run(until=second * 1000)

        num_exposed = len(global_vars.exposed_peers)
        print("Simulated %d seconds... (peers that committed fraud: %d, exposed: %d)" % (second, global_vars.peers_committed_fraud, num_exposed))
        if num_exposed == NUM_PEERS:
            break

    # Write bandwidth statistics
    with open("data/bandwidth.csv", "w") as bw_file:
        bw_file.write("public_key,bytes_up,bytes_down\n")
        for node in nodes:
            bw_file.write("%s,%d,%d\n" % (hexlify(node.my_peer.public_key.key_to_bin()).decode(), node.endpoint.bytes_up, node.endpoint.bytes_down))

    print("Simulation took %f seconds" % (time.time() - start_time))

    if run_yappi:
        yappi.stop()
        yappi_stats = yappi.get_func_stats()
        yappi_stats.sort("tsub")
        yappi_stats.save("yappi.stats", type='callgrind')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TrustChain simulator')
    parser.add_argument('--peers', '-p', default=100, type=int, help='The number of peers')
    parser.add_argument('--yappi', '-y', action='store_const', default=False, const=True, help='Run the Yappi profiler')

    args = parser.parse_args(sys.argv[1:])
    NUM_PEERS = args.peers

    setup_directories()
    start_ipv8_nodes()
    ipv8_discover_peers()
    start_simulation(run_yappi=args.yappi)
    parse_data()
