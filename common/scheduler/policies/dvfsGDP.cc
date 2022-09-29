#include "dvfsGDP.h"
#include "powermodel.h"
#include <iomanip>
#include <iostream>

using namespace std;

DVFSGDP::DVFSGDP(ThermalModel *thermalModel, const PerformanceCounters *performanceCounters, int coreRows, int coreColumns, int minFrequency, int maxFrequency, int frequencyStepSize)
	: thermalModel(thermalModel), performanceCounters(performanceCounters), coreRows(coreRows), coreColumns(coreColumns), minFrequency(minFrequency), maxFrequency(maxFrequency), frequencyStepSize(frequencyStepSize){
	
}

std::vector<int> DVFSGDP::getFrequencies(const std::vector<int> &oldFrequencies, const std::vector<bool> &activeCores) {
	std::vector<int> frequencies(coreRows * coreColumns);
	
	/* GDP core code begin */
	
	unsigned int n_core = coreColumns * coreRows;
	std::vector<float> gdp(n_core, 0); // vector used to store the gdp power budget for each core
	
	// run execute_gdp_power.py in python to compute the power budgets of the active cores, the results are stored in benchmarks/system_sim_state/gdp_power.txt
	string filename = "../common/scheduler/policies/execute_gdp_power.py "+to_string(n_core);
	string command = "python3 "+filename;
	system(command.c_str());
	
	// load the power budget from file
	ifstream file_power("./system_sim_state/gdp_power.txt");
	for (unsigned int coreCounter = 0; coreCounter < n_core; coreCounter++)
	  {
	    if (activeCores.at(coreCounter))
	      file_power >> gdp.at(coreCounter);
	  }
	file_power.close();
	
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
