#include "mapGDP.h"
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <fstream>

using namespace std;

// Just do initiation. Note that unlike the firstunused method, preferredCoresOrder do not contain the cores not specified by user, because their order should be computed at runtime by MapGDP::map
MapGDP::MapGDP(unsigned int coreRows, unsigned int coreColumns, std::vector<int> preferredCoresOrder)
	: coreRows(coreRows), coreColumns(coreColumns), preferredCoresOrder(preferredCoresOrder) {
	for (unsigned int i = 0; i < coreRows * coreColumns; i++) {
		if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), i) == this->preferredCoresOrder.end()) {
			this->preferredCoresOrder.push_back(-1); // put "-1", meaning the order has not been determined yet, should be determined by MapGDP::map
		}
	}
}

std::vector<int> MapGDP::map(String taskName, int taskCoreRequirement, const std::vector<bool> &availableCores, const std::vector<bool> &activeCores) {
	std::vector<int> cores;

	/* GDP mapping core code begin */

	// write availableCores and activeCores in info_for_mapping.txt as inputs to gdp_mapping.py
	ofstream mapping_info_file("./system_sim_state/info_for_mapping.txt");
	for (unsigned int i=0; i<availableCores.size();i++){
	  mapping_info_file << availableCores[i] << "\t";
	}
	mapping_info_file << endl;
	for (unsigned int i=0; i<activeCores.size();i++){
	  mapping_info_file << activeCores[i] << "\t";
	}
	mapping_info_file << endl;
	for (unsigned int i=0; i<preferredCoresOrder.size();i++){
	    mapping_info_file << preferredCoresOrder[i] << "\t";
	}
	mapping_info_file << endl;

	// execute execute_gdp_mapping.py to compute the active core mapping, the outputs are written in file gdp_map.txt
	string filename = "../common/scheduler/policies/execute_gdp_mapping.py "+to_string(taskCoreRequirement);
	string command = "python3 "+filename;
	system(command.c_str());

	// load the gdp mapping from file, and activate the cores according to the gdp mapping
	int core_to_activate;
	ifstream file_gdp_map("./system_sim_state/gdp_map.txt");
	for (int coreCounter = 0; coreCounter < taskCoreRequirement; coreCounter++)
	  {
	    file_gdp_map >> core_to_activate;
	    cores.push_back(core_to_activate);
	  }
	file_gdp_map.close();
	return cores;

	/* GDP mapping core code end */

	std::vector<int> empty;
	return empty;
}
