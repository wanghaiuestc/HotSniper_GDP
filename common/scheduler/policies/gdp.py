import numpy as np

def gdp_map(A, temp_max, temp_amb, taskCoreRequirement, activeCores, availableCores, preferredCoresOrder, P_s):
    # The function to find the GDP optimized active core map
    # Inputs:
    # A: system thermal model matrix, usually A = B^T G^{-1} B according to the GDP paper
    # temp_max: temperature threshold scalar
    # temp_amb: ambient temperature scalar
    # taskCoreRequirement: the number of new active cores need to be mapped
    # activeCores: boolean vector of the existing active core map, indicating if each core is active (True) or inactive (False). If you want to override some existing active cores, set them to False.
    # availableCores: boolean vector of the current inactive cores that can be activated (active core candidates), indicating if each core can be activated (True) or cannot be activated (False)
    # preferredCoresOrder: the user specified activation order vector, -1 indicates the end of the preferred cores. These cores should be activated first (if available) before GDP computation. If user do not specify any activation order, simply set all elements to -1.
    # P_s: static power vector, each element is the static power value of each core, use an all zero vector if no static power
    # Output:
    # cores_to_activate: vector of the new active core indexes

    # total core number of the multi/many core system
    core_num = availableCores.shape[0]
    
    # find the user specified preferred cores that are still in available cores, they should be activated first without GDP computing
    inact_pref_cores = np.zeros(core_num) - 1 # initiate all elements to -1
    n_ipc = 0 # number of inactive preferred cores
    for core_id in preferredCoresOrder:
        if availableCores[core_id] == True and core_id != -1:
            inact_pref_cores[n_ipc] = core_id
            availableCores[core_id] = False
            activeCores[core_id] = True
            n_ipc = n_ipc+1

    # Initiate cores_to_activate using inact_pref_cores, becuase we need to activate the inactive preferred cores first. 
    cores_to_activate = inact_pref_cores[:taskCoreRequirement] # all the inactive preferred cores should be activated first

    # If taskCoreRequirement <= n_ipc, then we are simply done without GDP computation. Otherwise (if taskCoreRequirement > n_ipc), we need to determine the remaining active cores using GDP iterations.
    if taskCoreRequirement > n_ipc:
        # initiate GDP iterations
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
        for i in range(n_ipc, taskCoreRequirement):
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
            
            # update T_rm
            Ai = np.atleast_2d(A[activeCores][:,activeCores])
            T_th_i = T_th[activeCores]
            Pi = np.linalg.solve(Ai, T_th_i)
            T_rm = T_th[availableCores] - A[availableCores][:,activeCores]@Pi

    return cores_to_activate

def gdp_power(A, core_map, temp_max, temp_amb, P_s, P_k, T_c, gdp_mode):
    # The function to compute the GDP power budget for a given active core map
    # Inputs:
    # A: system matrix, usually A = B^T G^{-1} B according to the GDP paper
    # core_map: boolean vector of the active core map, indicating if each core is active (True) or inactive (False)
    # temp_max: temperature threshold scalar
    # temp_amb: ambient temperature scalar
    # P_s: static power vector, each element is the static power value of each core, use an all zero vector if no static power
    # P_k: power vector of all cores at the previous step (assume current time is t, power budgeting/DVFS step is h, P_k is the power from time t-h to t, and we want to compute the power budget P for time t to t+h)
    # T_c: temperature vector of all cores at the current time (at time t in the example of P_k)
    # gdp_mode: 'steady' for steady state GDP and 'transient' for transient GDP
    # Output:
    # P: power budget of the active cores according to core_map

    # Compute the static power's impact on temperature. If the static power is assumed to be constant (such as in HotSniper), this impact is constant and actually can be pre-computed only once outside
    T_s = A@P_s # static power's impact on temperature, should be substracted from T_th later
    
    # formulate the Ai matrix (a submatrix of A according to the active core mapping)
    Ai = np.atleast_2d(A[core_map][:,core_map])
    if gdp_mode == 'steady': # for steady state GDP
        T_th = np.full((Ai.shape[0],), temp_max - temp_amb) - T_s[core_map] # threshold temperature vector
    else: # for transient GDP
        T_th = np.full((Ai.shape[0],), temp_max) - T_c[core_map] + Ai@P_k[core_map] - T_s[core_map]
        
    # Compute power budget with current active core mapping, solve power budget P
    P = np.linalg.solve(Ai, T_th) + P_s[core_map]

    return P
