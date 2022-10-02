# Greedy Dynamic Power (GDP)

Greedy dynamic power (GDP) is a dynamic power budgeting method which
provides a high power budget for the multi/many-core systems. It
contains an optimized active core mapping strategy as well as a
transient temperature-aware power budget computing methodology. 

Here, the GDP code is written in Python 3. It can
be easily integrated into a performance-thermal simulator or one's own
simulation tool chain. 

To illustrate how to integrate GDP into a performance-thermal simulator,
we provide the HotSniper simulator integrated with GDP, which is ready
to run as an example. 

The main GDP code is in ```gdp.py```.

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
(as in this repository), ```gdp.py``` is located at ```common/scheduler/policies/gdp.py```.

It mainly contains two functions: ```gdp_map```, which finds the GDP
optimized active core map, and ```gdp_power```, which computes the GDP
power budget for a given active core map.

To integrate GDP in your own performance-thermal simulation tool
chain (other than HotSniper), simply write a connection python script to handle the input and
output for GDP and add ```import gdp``` to use the GDP functions. 
Take ```common/scheduler/policies/execute_gdp_mapping.py``` and ```common/scheduler/policies/execute_gdp_power.py``` as examples, which
are such scripts written for the HotSniper simulator. 

## How to install the HotSniper integrated with GDP

In this repository, GDP is integrated into the HotSniper simulator as an example. The installation of
HotSniper with GDP is exactly the same as the original HotSniper, so
please refer to [HotSniper](https://github.com/anujpathania/HotSniper)
for the installation steps.


## How to run HotSniper with GDP

1. Install HotSniper with GDP by following the installation steps of
   the original HotSniper described in the [HotSniper User Manual](https://github.com/anujpathania/HotSniper#the-hotsniper-user-manual).
2. Set the HotSniper related configurations by following the
   [HotSniper Configuration Checklist](https://github.com/anujpathania/HotSniper#configuration-checklist).
3. Set the GDP related configurations:
   - In ```config/base.cfg```:
	 - Set ```scheduler/open/logic``` to ```gdp``` to use GDP as
       the active core mapping method.
	 - Set ```scheduler/open/dvfs``` to ```gdp``` to use GDP to
       compute the power budget dynamically for each DVFS cycle. 
	 - Set ```scheduler/open/gdp_mode``` to ```steady``` or  ```transient```
4. If you want to change the multi-core system to be simulated, set
   the floorplan, thermal model, and core number settings at several
   locations (take the provided 100-core manycore system with
   floorplan ```10x10_manycore.flp``` as an example): 
   - In ```config/base.cfg```: 
	 - Set ```periodic_thermal/floorplan``` to ```../benchmarks/10x10_manycore.flp```
	 - Set ```periodic_thermal/thermal_model``` to ```../benchmarks/10x10_eigendata.bin```
	 - Set ```general/total_cores``` to ```100```
   - In ```simulationcontrol/config.py```: 
	 - Set ```NUMBER_CORES``` to ```100```
5. Run HotSniper by following the [HotSniper User Manual](https://github.com/anujpathania/HotSniper#the-hotsniper-user-manual).

HotSniper with GDP can run directly with the provided two many-core
systems, using the PARSEC benchmarks: 

1. 8x8\_manycore: floorplan (```benchmarks/8x8_manycore.flp```)
2. 10x10\_manycore: floorplan (```benchmarks/10x10_manycore.flp```)

## Code Acknowledgements

  HotSniper: <https://github.com/anujpathania/HotSniper>
  
  Sniper: <http://snipersim.org>
  
  McPat: https://www.hpl.hp.com/research/mcpat/
  
  HotSpot: <http://lava.cs.virginia.edu/HotSpot/>
  
  MatEx: http://ces.itec.kit.edu/846.php
  
  thermallib: https://github.com/ma-rapp/thermallib

