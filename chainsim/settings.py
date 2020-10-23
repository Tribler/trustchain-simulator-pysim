from dataclasses import dataclass


@dataclass
class SimulationSettings:
    peers = 100
    double_spend_probability = 0.1
    back_pointers = 10
    broadcast_fanout = 10
    crawl_batch_size = 5
    crawl_interval = 0.5
    max_duration = 600
    send_fail_probability = 0
