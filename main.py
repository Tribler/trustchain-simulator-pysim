import argparse
import sys

from simpy import Environment

from chainsim.settings import SimulationSettings
from chainsim.simulation import TrustChainSimulation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TrustChain simulator')
    parser.add_argument('--peers', '-p', default=100, type=int, help='The number of peers')
    parser.add_argument('--send_fail_probability', default=0, type=float, help='The probability of message send failure')
    parser.add_argument('--yappi', '-y', action='store_const', default=False, const=True, help='Run the Yappi profiler')

    args = parser.parse_args(sys.argv[1:])
    env = Environment()

    sim_settings = SimulationSettings()
    sim_settings.peers = 1000
    sim_settings.exchange_strategy = 0
    sim_settings.send_fail_probability = args.send_fail_probability
    simulation = TrustChainSimulation(sim_settings, env)
    simulation.run(yappi=args.yappi)
