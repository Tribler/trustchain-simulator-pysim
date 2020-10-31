import sys
from multiprocessing.context import Process

from simpy import Environment

from chainsim.settings import SimulationSettings
from chainsim.simulation import TrustChainSimulation


def run(settings):
    env = Environment()
    simulation = TrustChainSimulation(settings, env)
    simulation.run()


if __name__ == "__main__":
    strategy = int(sys.argv[1])

    print("Going to evaluate strategy %d" % strategy)

    # Batch 1
    processes = []
    for num_peers in range(1000, 11000, 1000):
        print("Evaluating %d peers..." % num_peers)
        settings = SimulationSettings()
        settings.peers = num_peers
        settings.exchange_strategy = strategy
        p = Process(target=run, args=(settings,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("Fully evaluated strategy %d!" % strategy)
