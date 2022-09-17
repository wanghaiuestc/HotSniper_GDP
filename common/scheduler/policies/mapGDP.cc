#include "mapGDP.h"
#include <algorithm>
#include <iostream>
#include <map>
#include <set>

// Just do initiation. Note that unlike the firstunused method, preferredCoresOrder do not contain the cores not specified by user, because their order should be computed at runtime by MapGDP::map
MapGDP::MapGDP(unsigned int coreRows, unsigned int coreColumns, std::vector<int> preferredCoresOrder)
	: coreRows(coreRows), coreColumns(coreColumns), preferredCoresOrder(preferredCoresOrder) {
	for (unsigned int i = 0; i < coreRows * coreColumns; i++) {
		if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), i) == this->preferredCoresOrder.end()) {
			this->preferredCoresOrder.push_back(i);
		}
	}
}

std::vector<int> MapGDP::map(String taskName, int taskCoreRequirement, const std::vector<bool> &availableCores, const std::vector<bool> &activeCores) {
	std::vector<int> cores;
	std::cout << "taskCoreRequirement: " << taskCoreRequirement << std::endl;
	std::cout << "availableCores: ";
	for (int i=0; i<availableCores.size();i++){
	  std::cout << availableCores[i];
	}
	std::cout << std::endl;
	std::cout << "activeCores: ";
	for (int i=0; i<activeCores.size();i++){
	  std::cout << activeCores[i];
	}
	std::cout << std::endl;
	// try to fill with preferred cores
	for (const int &c : preferredCoresOrder) {
		if (availableCores.at(c)) {
			cores.push_back(c);
			if ((int)cores.size() == taskCoreRequirement) {
				return cores;
			}
		}
	}

	std::vector<int> empty;
	return empty;
}
