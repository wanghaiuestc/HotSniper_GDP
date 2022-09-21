import sys
import scipy.io as spio
import numpy as np

def gdp_mapping(taskCoreRequirement):
    
    print('**gdp_mapping.py python function call begin')

    # load the mapping information from file info_for_mapping.txt, saved in mapGDP::map in mapGDP.cc
    mapping_info = np.loadtxt('./system_sim_state/info_for_mapping.txt', dtype=int)
    availableCores = mapping_info[0,:];
    activeCores = mapping_info[1,:];
    print('taskCoreRequirement: ', taskCoreRequirement)
    print('availableCores: ', availableCores)
    print('activeCores: ', activeCores)

    # load the multi-core system's thermal model matrices
    core_num = availableCores.shape[0]
    if core_num == 64:
        print('**load the 8x8 system matrices')
        A = spio.loadmat('./gdp_thermal_matrices/8x8_A.mat')['A']
        n_row = 8
        n_col = 8
    else:
        raise Exception('There is no thermal matrices available for this core number yet. Please check the core number. Or generate the corresponding thermal matrices and put them in benchmarks/gdp_thermal_matrices')
    
gdp_mapping(sys.argv[1])
