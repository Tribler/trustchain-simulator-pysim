import argparse
import sys

from simpy import Environment

from chainsim.settings import SimulationSettings
from chainsim.simulation import TrustChainSimulation


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TrustChain simulator')
    parser.add_argument('--peers', '-p', default=100, type=int, help='The number of peers')
    parser.add_argument('--send_fail_probability', default=0, type=float, help='The probability of message send failure')
    parser.add_argument('--scenario_file', '-s', default=None, type=str, help='A scenario file containing interactions')
    parser.add_argument('--yappi', '-y', action='store_const', default=False, const=True, help='Run the Yappi profiler')

    args = parser.parse_args(sys.argv[1:])
    env = Environment()

    sim_settings = SimulationSettings()
    sim_settings.peers = args.peers
    sim_settings.exchange_strategy = 0
    sim_settings.send_fail_probability = args.send_fail_probability
    sim_settings.scenario_file = args.scenario_file
    simulation = TrustChainSimulation(sim_settings, env)
    simulation.run(yappi=args.yappi)
