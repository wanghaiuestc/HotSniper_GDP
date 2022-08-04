import sys
import scipy.io as spio
import numpy as np

def gdp_power(core_num):
    
    print('**gdp_power.py python function call begin')

    # load the multi-core system's G C B thermal model matrices
    if core_num == '64':
        print('**load the 8x8 system matrices')
        B = spio.loadmat('./gcb_model/8x8_B.mat')['B']
        C = spio.loadmat('./gcb_model/8x8_C.mat')['C']
        G = spio.loadmat('./gcb_model/8x8_G.mat')['G']
    else:
        raise Exception('There is no GCB thermal model available for this core number. Please check the core number. Or generate the corresponding GCB matrices and put them in benchmarks/gcb_model')

    # load the current active core distribution in core_map
    core_map = np.loadtxt('./system_sim_state/mapping.txt')
    print('core_map: ', core_map)

    
if len(sys.argv) != 2:
    raise Exception('Please provide core number when calling gdp_power.py')

gdp_power(sys.argv[1])



