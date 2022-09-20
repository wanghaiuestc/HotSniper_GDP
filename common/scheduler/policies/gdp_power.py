import sys
import scipy.io as spio
import numpy as np
import scipy.sparse.linalg
import re

def gdp_power(core_num):
    
    print('**gdp_power.py python function call begin')

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
        if line.startswith('gdp_mode'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            gdp_mode = line_words[1]
            print('gdp_mode: ', gdp_mode)
        if line.startswith('dvfs_epoch'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            dvfs_epoch = int(line_words[1])
            print('dvfs_epoch: ', dvfs_epoch)
        if line.startswith('inactive_power'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            inactive_power = float(line_words[1])
            print('inactive_power: ', inactive_power)
    file_config.close()
        
    # load the multi-core system's G C B thermal model matrices
    if core_num == '64':
        print('**load the 8x8 system matrices')
        if gdp_mode == 'steady':
            A = spio.loadmat('./gdp_thermal_matrices/8x8_A.mat')['A']
        elif gdp_mode == 'transient':
            if dvfs_epoch == 1000000:
                A = spio.loadmat('./gdp_thermal_matrices/8x8_A_1ms.mat')['A_bar']
            else:
                raise Exception("gdp current only supports dvfs_epoch = 1000000, please modify base.cfg")
        else:
            raise Exception("gdp mode can only be steady and transient, please modify base.cfg")
        n_row = 8
        n_col = 8
    else:
        raise Exception('There is no thermal matrices available for this core number yet. Please check the core number. Or generate the corresponding thermal matrices and put them in benchmarks/gdp_thermal_matrices')

    # load the current active core distribution in core_map. 'mapping.txt' is writen by SchedulerOpen::periodic in scheduler_open.cc for every DVFS cycle
    core_map = np.loadtxt('./system_sim_state/mapping.txt')
    core_map = np.asarray(core_map, dtype = bool) # use bool type to extract Ai matrix from A
    print('core_map: ', core_map)

    # load the current temperature/power from files, ingore the first line which contains core names
    T_c = np.loadtxt('./InstantaneousTemperature.log',skiprows=1) # current temperature
    P_k = np.loadtxt('./InstantaneousPower.log',skiprows=1) # previous power consumption
    print('Current temperature of cores: ', T_c)
    print('Previous power of cores: ', P_k)

    # Compute the static power's impact on temperature. If the static power is assumed to be constant (as in this experiment), this impact is constant and actually can be pre-computed only once outside
    P_s = np.full((A.shape[0],), inactive_power) # static power vector
    T_s = A@P_s # static power's impact on temperature, should be substracted from T_th later

    # formulate the Ai matrix (a submatrix of A according to the active core mapping)
    Ai = A[core_map][:,core_map]
    print('Ai shape: ', Ai.shape)
    if gdp_mode == 'steady': # for steady state GDP
        T_th = np.full((Ai.shape[0],), temp_max - temp_amb) - T_s[core_map] # threshold temperature vector
        print('T_th: ', T_th)
    else: # for transient GDP
        T_th = np.full((Ai.shape[0],), temp_max) - T_c[core_map] + Ai@P_k[core_map] - T_s[core_map]
        print('T_th: ', T_th)
        
    # # Compute power budget with current active core mapping, solve power budget P
    if Ai.shape[0] == 1:
        P = T_th[0]/Ai + inactive_power
    else:
        P = np.linalg.solve(Ai, T_th) + P_s[core_map]
    print('Power budget P: ', P)

    # Write power budget P into file
    file_power = open('./system_sim_state/gdp_power.txt', 'w')
    for power in P:
        file_power.write(str(np.asscalar(power))+' ')
    file_power.close()
    
if len(sys.argv) != 2:
    raise Exception('Please provide core number when calling gdp_power.py')

gdp_power(sys.argv[1])



