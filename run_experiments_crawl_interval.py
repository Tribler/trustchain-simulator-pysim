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
        processes = []
        for crawl_interval_ms in range(500, 5500, 500):
            settings = SimulationSettings()
            settings.peers = 1000
            settings.crawl_interval = crawl_interval_ms / 1000
            settings.exchange_strategy = strategy
            p = Process(target=run, args=(settings,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print("Fully evaluated strategy %d!" % strategy)
