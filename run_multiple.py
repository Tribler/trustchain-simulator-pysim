from multiprocessing.context import Process

from simpy import Environment

from chainsim.settings import SimulationSettings
from chainsim.simulation import TrustChainSimulation


def run(settings):
    env = Environment()
    simulation = TrustChainSimulation(settings, env)
    simulation.run()


if __name__ == "__main__":

    processes = []

    for num_backpointers in range(0, 11):
        settings = SimulationSettings()
        settings.peers = 1000
        settings.back_pointers = num_backpointers
        p = Process(target=run, args=(settings,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
