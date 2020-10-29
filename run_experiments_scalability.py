from multiprocessing.context import Process

from simpy import Environment

from chainsim.settings import SimulationSettings
from chainsim.simulation import TrustChainSimulation


def run(settings):
    env = Environment()
    simulation = TrustChainSimulation(settings, env)
    simulation.run()


if __name__ == "__main__":

    for strategy in [0, 1, 2, 3]:
        # Batch 1
        processes = []
        for num_peers in [1000, 2000, 3000, 4000, 5000, 6000]:
            settings = SimulationSettings()
            settings.peers = num_peers
            settings.exchange_strategy = strategy
            p = Process(target=run, args=(settings,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print("Evaluated batch 1")

        # Batch 2
        processes = []
        for num_peers in [7000, 8000]:
            settings = SimulationSettings()
            settings.peers = num_peers
            settings.exchange_strategy = strategy
            p = Process(target=run, args=(settings,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print("Evaluated batch 2")

        # Batch 3
        processes = []
        for num_peers in [9000, 10000]:
            settings = SimulationSettings()
            settings.peers = num_peers
            settings.exchange_strategy = strategy
            p = Process(target=run, args=(settings,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print("Fully evaluated strategy %d!" % strategy)
