import sys
import scipy.io as spio
import numpy as np
import re

def gdp_mapping(taskCoreRequirement):
    
    print('**gdp_mapping.py python function call begin')

    taskCoreRequirement = int(taskCoreRequirement)

    # read configurations from base.cfg, including max_temperature (threshold temperature), ambient_temperature, etc
    file_config = open('../config/base.cfg')
    for line in file_config:
        if line.startswith('max_temperature'):
            line_words = re.split('=|#|\s', line) # split the line into words with splitor '=', '#', and whitespaces
            line_words = list(filter(None, line_words)) # filt out the whitespaces
            temp_max = float(line_words[1])
            print('max_temperature: ', temp_max)
        if line.startswith('ambient_temperature'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            temp_amb = float(line_words[1])
            print('ambient_temperature: ', temp_amb)
        if line.startswith('inactive_power'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            inactive_power = float(line_words[1])
            print('inactive_power: ', inactive_power)
    file_config.close()

    # load the mapping information from file info_for_mapping.txt, saved in mapGDP::map in mapGDP.cc
    mapping_info = np.loadtxt('./system_sim_state/info_for_mapping.txt', dtype=int)
    availableCores = mapping_info[0,:].astype('bool');
    activeCores = mapping_info[1,:].astype('bool');
    preferredCoresOrder = mapping_info[2,:]
    print('taskCoreRequirement: ', taskCoreRequirement)
    print('availableCores: ', availableCores)
    print('activeCores: ', activeCores)
    print('preferredCoresOrder: ', preferredCoresOrder)

    if np.sum(availableCores) < taskCoreRequirement:
        raise Exception('There are not enough available cores to meet the required core number of this task.')
    
    # load the multi-core system's thermal model matrices
    core_num = availableCores.shape[0]
    if core_num == 64:
        print('**load the 8x8 system matrices')
        A = spio.loadmat('./gdp_thermal_matrices/8x8_A.mat')['A']
        n_row = 8
        n_col = 8
    else:
        raise Exception('There is no thermal matrices available for this core number yet. Please check the core number. Or generate the corresponding thermal matrices and put them in benchmarks/gdp_thermal_matrices')

    # find the user specified preferred cores that are still in available cores, they should be activated first without GDP computing
    inact_pref_cores = np.zeros(core_num) - 1 # initiate all elements to -1
    n_ipc = 0 # number of inactive preferred cores
    for core_id in preferredCoresOrder:
        if availableCores[core_id] == True and core_id != -1:
            inact_pref_cores[n_ipc] = core_id
            availableCores[core_id] = False
            activeCores[core_id] = True
            n_ipc = n_ipc+1
    print('inact_pref_cores: ', inact_pref_cores)
    print('availableCores: ', availableCores)

    # activate the inactive preferred cores first. If taskCoreRequirement <= n_ipc, then we are simply done without GDP computation. Otherwise, we need to determine the remaining active cores using GDP iterations
    cores_to_activate = np.zeros(core_num) - 1 # initiate all elements to -1
    cores_to_activate[:taskCoreRequirement] = inact_pref_cores[:taskCoreRequirement] # all the inactive preferred cores should be activated first

    # if taskCoreRequirement > n_ipc, we need to perform GDP to find the remaining active cores
    if taskCoreRequirement > n_ipc:
        # initiate GDP iterations
        P_s = np.full((A.shape[0],), inactive_power) # static power vector
        T_s = A@P_s # static power's impact on temperature, should be substracted from T_th later
        T_th = np.full((core_num,), temp_max - temp_amb) - T_s # threshold temperature vector
        if np.sum(activeCores) > 0:
            Ai = np.atleast_2d(A[activeCores][:,activeCores])
            T_th_i = T_th[activeCores]
            Pi = np.linalg.solve(Ai, T_th_i) # power budget of the existing active cores
            T_rm = T_th[availableCores] - A[availableCores][:,activeCores]@Pi # temperature threshold headroom of the available cores (candidates) by substracting the existing active cores' thermal impact
        else: # when there is no existing active core and no user preferred core
            T_rm = T_th[availableCores]
            
        Aa = np.atleast_2d(A[availableCores][:,availableCores])
        idx_available_cores = np.flatnonzero(availableCores)
        print('idx_available_cores: ', idx_available_cores)
        for i in range(n_ipc, taskCoreRequirement-n_ipc):
            # find the core in available cores (candidates) which leads to the largest power budget (indicated by the largest inner product with T_rm)
            idx = 0
            for j in range(1,idx_available_cores.shape[0]): 
                if np.inner(Aa[:][j],T_rm) > np.inner(Aa[:][idx],T_rm):
                    idx = j
            # add the new active core (idx) to the exsiting active cores
            cores_to_activate[i] = idx_available_cores[idx] # add the new active core (idx) to the list of cores to activate as the final output
            availableCores[idx_available_cores[idx]] = False
            activeCores[idx_available_cores[idx]] = True
            Aa = np.atleast_2d(A[availableCores][:,availableCores])
            idx_available_cores = np.flatnonzero(availableCores)
            print('idx_available_cores: ', idx_available_cores)
            
            # update T_rm
            Ai = np.atleast_2d(A[activeCores][:,activeCores])
            T_th_i = T_th[activeCores]
            Pi = np.linalg.solve(Ai, T_th_i)
            T_rm = T_th[availableCores] - A[availableCores][:,activeCores]@Pi

    print('cores_to_activate: ', cores_to_activate)
    
    # write the GDP mapping results to file
    file_gdp_map = open('./system_sim_state/gdp_map.txt', 'w')
    for core in cores_to_activate:
        file_gdp_map.write(str(int(core))+' ')
    file_gdp_map.close()
    
gdp_mapping(sys.argv[1])
