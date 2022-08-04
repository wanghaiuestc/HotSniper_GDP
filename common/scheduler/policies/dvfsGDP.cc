#include <Python.h>
#include "dvfsGDP.h"
#include "powermodel.h"
#include <iomanip>
#include <iostream>
// #include <pyhelper.hpp>

using namespace std;

DVFSGDP::DVFSGDP(ThermalModel *thermalModel, const PerformanceCounters *performanceCounters, int coreRows, int coreColumns, int minFrequency, int maxFrequency, int frequencyStepSize)
	: thermalModel(thermalModel), performanceCounters(performanceCounters), coreRows(coreRows), coreColumns(coreColumns), minFrequency(minFrequency), maxFrequency(maxFrequency), frequencyStepSize(frequencyStepSize){
	
}

std::vector<int> DVFSGDP::getFrequencies(const std::vector<int> &oldFrequencies, const std::vector<bool> &activeCores) {
	std::vector<int> frequencies(coreRows * coreColumns);
	
	/* GDP core code begin */
	
	unsigned int n_core = coreColumns * coreRows;
	std::vector<float> gdp(n_core, 0); // vector used to store the gdp power budget for each core
	// char gdp_budget_filename = "gdp_budget.py";
	// FILE* gdp_budget_file;
	
	// CPyInstance pyInstance;
	// gdp_budget_file = Py_fopen(gdp_budget_filename, "r");
	// PyRun_SimpleString("print('Hello World from Python')");
	string filename = "../common/scheduler/policies/gdp_power.py "+to_string(n_core);
	string command = "python3 "+filename;
	// cout<<"***The current directory is: ";
	// string command = "pwd";
	system(command.c_str());
	

	for (unsigned int coreCounter = 0; coreCounter < n_core; coreCounter++)
	  {
	    gdp.at(coreCounter) = 10.0;
	  }
	
	/* GDP core code end */
	

	for (unsigned int coreCounter = 0; coreCounter < coreRows * coreColumns; coreCounter++) {
		if (activeCores.at(coreCounter)) {
			float power = performanceCounters->getPowerOfCore(coreCounter);
			float temperature = performanceCounters->getTemperatureOfCore(coreCounter);
			int frequency = oldFrequencies.at(coreCounter);
			float utilization = performanceCounters->getUtilizationOfCore(coreCounter);

			cout << "[Scheduler][DVFSGDP]: Core " << setw(2) << coreCounter << ":";
			cout << " P=" << fixed << setprecision(3) << power << " W";
			cout << " f=" << frequency << " MHz";
			cout << " T=" << fixed << setprecision(1) << temperature << " °C";
			cout << " utilization=" << fixed << setprecision(3) << utilization << endl;
			cout<<"GDP_power_budget = "<<gdp.at(coreCounter)<<endl;

			int expectedGoodFrequency = PowerModel::getExpectedGoodFrequency(frequency, power, gdp.at(coreCounter), minFrequency, maxFrequency, frequencyStepSize);
			frequencies.at(coreCounter) = expectedGoodFrequency;
		} else {
			frequencies.at(coreCounter) = minFrequency;
		}
	}

	return frequencies;
}
