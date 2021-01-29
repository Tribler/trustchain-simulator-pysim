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
        settings = SimulationSettings()
        settings.exchange_strategy = strategy
        settings.scenario_file = "1.txt"
        settings.crawl_interval = 10
        p = Process(target=run, args=(settings,))
        p.start()
        p.join()

        print("Fully evaluated strategy %d!" % strategy)
