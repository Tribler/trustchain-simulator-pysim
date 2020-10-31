from dataclasses import dataclass


@dataclass
class SimulationSettings:
    peers = 100
    double_spend_probability = 0.1
    back_pointers = 10
    broadcast_fanout = 5
    crawl_batch_size = 2
    crawl_interval = 0.5
    max_duration = 600
    send_fail_probability = 0

    # We define different broadcast strategies
    # 0 = PULL
    # 1 = PULL + RAND
    # 2 = PULL + PUSH
    # 3 = PULL + RAND + PUSH
    exchange_strategy = 3

    # We define different workloads
    # 0 = every peer creates one tx per second
    # 1 = the time between two transactions is uniformly picked from [0, 2]
    # 2 = the time between two transactions is normally distributed with mean 1 and std. dev 0.3
    workload = 0
