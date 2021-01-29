import os


class Scenario:
    """
    This class represents a scenario, which is optionally provided when starting the simulation.
    """

    def __init__(self, scenario_file_path):
        self.scenario_file_path = scenario_file_path
        self.actions = {}
        self.num_peers = -1
        self.max_timestamp = -1

    def parse(self):
        if not os.path.exists(self.scenario_file_path):
            raise RuntimeError("Scenario file %s does not exist!" % self.scenario_file_path)

        num_actions = 0
        with open(self.scenario_file_path) as scenario_file:
            for line in scenario_file.readlines():
                parts = line.strip().split(",")
                initiator_id = int(parts[0])
                counterparty_id = int(parts[1])
                timestamp = int(parts[2])

                if timestamp > self.max_timestamp:
                    self.max_timestamp = timestamp
                if initiator_id > self.num_peers:
                    self.num_peers = initiator_id
                if counterparty_id > self.num_peers:
                    self.num_peers = counterparty_id

                if initiator_id not in self.actions:
                    self.actions[initiator_id] = []

                self.actions[initiator_id].append((timestamp, counterparty_id, False))
                num_actions += 1

        print("Parsed %d scenario actions!" % num_actions)
