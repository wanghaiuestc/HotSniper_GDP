import sys
import scipy.io as spio
import numpy as np
import scipy.sparse.linalg

def gdp_power(core_num):
    
    print('**gdp_power.py python function call begin')

    # load the multi-core system's G C B thermal model matrices
    if core_num == '64':
        print('**load the 8x8 system matrices')
        B = spio.loadmat('./gcb_model/8x8_B.mat')['B']
        C = spio.loadmat('./gcb_model/8x8_C.mat')['C']
        G = spio.loadmat('./gcb_model/8x8_G.mat')['G']
        n_row = 8
        n_col = 8
    else:
        raise Exception('There is no GCB thermal model available for this core number. Please check the core number. Or generate the corresponding GCB matrices and put them in benchmarks/gcb_model')

    # load the current active core distribution in core_map. 'mapping.txt' is writen by SchedulerOpen::periodic in scheduler_open.cc for every DVFS cycle
    core_map = np.loadtxt('./system_sim_state/mapping.txt')
    core_map = np.asarray(core_map, dtype = bool) # use bool type to extract Ai matrix from B.T@G@B
    print('core_map: ', core_map)

    # load the current temperature from InstantaneousTemperature.log, ingore the first line which contains core names
    T_c = np.loadtxt('./InstantaneousTemperature.log',skiprows=1)
    print('Current temperature of cores: ', T_c)

    # read configurations from base.cfg, including max_temperature (threshold temperature), ambient_temperature
    file_config = open('../config/base.cfg')
    key_max_temp = 'max_temperature'
    for line in file_config:
        if 'max_temperature' in line:
            line_words = line.split(" ")
            temp_max = float(line_words[2])
            print('max_temperature: ', temp_max)
        if 'ambient_temperature' in line:
            line_words = line.split(" ")
            temp_amb = float(line_words[2])
            print('ambient_temperature: ', temp_amb)
    file_config.close()

    # formulate the Ai matrix (a submatrix of A according to the active core mapping)
    A = (B.T@scipy.sparse.linalg.spsolve(G, B)).todense() # should be pre-computed and stored outside in the future
    Ai = A[core_map][:,core_map]
    print('Ai shape: ', Ai.shape)
    # Compute power budget with current active core mapping
    T_th = np.full((Ai.shape[0],), temp_max - temp_amb) # threshold temperature vector
    print('T_th: ', T_th)
    # solve power budget P
    if Ai.shape[0] == 1:
        P = T_th/(Ai[0][0])
    else:
        P = np.linalg.solve(Ai, T_th)
    print('Power budget P: ', P)

    # Write power budget P into file
    
    
if len(sys.argv) != 2:
    raise Exception('Please provide core number when calling gdp_power.py')

gdp_power(sys.argv[1])



