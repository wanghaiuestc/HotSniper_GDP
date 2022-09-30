# Greedy Dynamic Power (GDP)

We release the open source code for GDP written in Python 3.

Greedy dynamic power (GDP) is a dynamic power budgeting policy which
provides a high power budget for the multi/many-core systems. It
contains an optimized active core mapping strategy as well as a
transient temperature aware power budget computing methodology. 

Here, the GDP code is integrated into the HotSniper simulator. With
the similar strategy, one can easily integrate GDP into other performance-thermal
simulators or his/her own simulation tool chain. 

The main
GDP code is in ```gdp.py```.

## Publication

### GDP: A Greedy Based Dynamic Power Budgeting Method for Multi/Many-Core Systems in Dark Silicon

For more details, please see our GDP paper published in TC 2019.
Please also cite this paper if this code is useful.

> H. Wang, D. Tang, M. Zhang, et al., **"GDP: A Greedy Based Dynamic
> Power Budgeting Method for Multi/Many-Core Systems in Dark
> Silicon."** *IEEE Transactions on Computers*, vol. 68, no. 4, April
> 2019, pp. 526-541.

[IEEE Xplore](https://ieeexplore.ieee.org/document/8493277) 

## Introduction of the GDP code
The main GDP code is in ```gdp.py```. When integrated with HotSniper
(as in this repository), ```gdp.py``` is located at
```common/scheduler/policies/gdp.py```.

It mainly contains two functions: ```gdp_map```, which finds the GDP
optimized active core map, and ```gdp_power```, which compute the GDP
power budget for a given active core map.

To integrate GDP in your own performance-thermal simulation tool
chain (other than HotSniper), simply write a connection python script to handle the input and
output for GDP and add ```import gdp``` to use the GDP functions. Take
```common/scheduler/policies/execute_gdp_mapping.py``` and
```common/scheduler/policies/execute_gdp_power.py``` as examples which
are such scripts for the HotSniper simulator. 

## How to install the HotSniper integrated with GDP

GDP is integrated into the HotSniper simulator. The installation of
HotSniper_GDP is 
Please refer to [HotSniper User Manual](https://github.com/anujpathania/HotSniper/blob/master/The%20HotSniper%20User%20Manual.pdf) to learn how to write custom scheduling policies that perform thermal-aware Dynamic Voltage Frequency Scaling (DVFS), Task Mapping, and Task Migration.


## Configuration Checklist

- [ ] select technology node
  - `config/base.cfg`: `power/technology_node`
- [ ] V/f-levels
  - check `scripts/energystats.py`: `build_dvfs_table` (keep in mind that V/f-levels are specified at 22nm)
- [ ] power scaling (if technology node < 22nm)
  - check `tools/mcpat.py`: `scale_power`
- [ ] select high-level architecture
  - `simulationcontrol/config.py`: `SNIPER_CONFIG` and `NUMBER_CORES`
- [ ] set architectural parameters
  - `config/base.cfg` and other config files as specified in the previous step
- [ ] set scheduling and DVFS parameters
  - `config/base.cfg`: `scheduler/open/*` and `scheduler/open/dvfs/*`
- [ ] set `perf_model/core/frequency`
- [ ] start trial run to extract estimations from McPAT
  - start a simulation based on `simulationcontrol/run.py`: `test_static_power`, kill it after ~5ms simulated time
  - extract static power at low/high V/f levels from the command line output: take power of last / second-to-last core
  - extract area of a core from `benchmarks/energystats-temp.txt`: take processor area (including L3 cache etc.), divide by number of cores, and scale it to your technology node. If file is empty, start simulation again, kill it, and check again.
- [ ] configure static power consumption
  - `config/base.cfg`: `power/*`
  - `inactive_power` must be set to static power consumption at min V/f level
- [ ] create floorplan (`*.flp`) and corresponding thermal model (`*.bin`)
  - Option 1: use your own floorplan
    - use [MatEX] to create the thermal model (`-eigen_out`) from your floorplan
  - Option 2: use [thermallib] to create a simple regular floorplan (only per-core temperature, no finer granularity) and the corresponding thermal model
    - core width is `sqrt(core area)` from McPAT area estimations
    - example: `python3 create_thermal_model.py --amb 45 --crit 80 --core_naming sniper --core_width [core width] model [cores]x[cores]`
    - NOTE: McPAT area estimations are high, i.e., observed temperatures are too low. Therefore, using a smaller core size should be considered as an option.
- [ ] specify floorplan, thermal model and other thermal settings in config
  - `config/base.cfg`: `periodic_thermal`
  - `tdp` is defined by the floorplan, temperature limits and cooling parameters
- [ ] create your scenarios
  - `simulationcontrol/run.py` (e.g., similar to `def example`)
- [ ] set your output folder for traces
  - `simulationcontrol/config.py`: `RESULTS_FOLDER`
  - This folder usually is outside of the HotSniper folder because we don't want to commit results (large files) to the simulator repo.
- [ ] verify all configurations in `sim.cfg` of a finished run


## HOWTO

### A- Implement your own mapping / DVFS policy
These policies are implemented in `common/scheduler/policies`.
Mapping policies derive from `MappingPolicy`, DVFS policies derive from `DVFSPolicy`.
After implementing your policy, instantiate it in `SchedulerOpen::initMappingPolicy` / `SchedulerOpen::initDVFSPolicy`.


## Common Errors
```UnicodeEncodeError: 'ascii' codec can't encode character '\xb0' in position 61: ordinal not in range(128)```
```sh
export PYTHONIOENCODING="UTF-8"
```

## Code Acknowledgements

  Sniper: <http://snipersim.org>
  
  McPat: https://www.hpl.hp.com/research/mcpat/
  
  HotSpot: <http://lava.cs.virginia.edu/HotSpot/>
  
  MatEx: http://ces.itec.kit.edu/846.php
  
  thermallib: https://github.com/ma-rapp/thermallib

