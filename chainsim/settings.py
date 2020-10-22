from dataclasses import dataclass


@dataclass
class SimulationSettings:
    peers = 100
    double_spend_probability = 0.1
    back_pointers = 10
    broadcast_fanout = 0
    crawl_batch_size = 5
    crawl_interval = 0.5
