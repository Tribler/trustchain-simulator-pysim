# TrustChain simulator

This repository provides a simple simulator for TrustChain. It uses the TrustChain source code, the [IPv8](https://github.com/tribler/py-ipv8) networking library and the discrete event simulator [PySim](https://pythonhosted.org/pysim/). The experiments are particularly focussed on fraud detection.

Our default attack model has every peer fork its chain with a probability of 10%. Each peer commits this fraud once during the experiment. Our simulator keeps track of the time at which the fraud has been committed, and the time at which the fraud has been detected. The results are written to the `data` directory. The experiment settings are reflected in the directory names, e.g., `n_4000_b_10_link_0.00_f_5_s_0_w_0`. As such, results of experiments with differing parameters are written to different directories. 

## Usage

You can run a simple experiment with 100 peers as follows:

```
python3 main.py
```

The experiment output can be found in `data/n_100_b_10_link_0.00_f_5_s_0_w_0`.

By default, each experiment runs until all fraud instances have been detected, or when 600 seconds have elapsed. You can setup a custom experiment by creating an instance of `SimulationSettings` and by applying the custom experiment parameters. Note that our simulator also supports profiling with the [Yappi](https://github.com/sumerc/yappi) framework.

We also provide a few scripts to run targeted experiments, e.g., by varying the number of back-pointers in each record.
