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

    for fail_rate in range(0, 55, 5):
        settings = SimulationSettings()
        settings.peers = 1000
        settings.send_fail_probability = fail_rate / 100
        p = Process(target=run, args=(settings,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
