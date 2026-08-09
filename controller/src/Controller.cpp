#include "Controller.h"
#include <algorithm>
#include <cstddef>
#include <fstream>
#include <sstream>
#include <string>

double Controller::fuelMapLookup(const ControllerInput& input) {
    std::string fuel_map_file = input.engine_map;
    std::string target;

    std::fstream filein("file.txt", std::ios::in);

    std::string line; 
    int col = 0;

    getline(filein, line); // Read the first line (header)
    
    std::stringstream header(line);

    std::string colName;

    while (getline(header, colName, ',')) {
        if (std::stod(colName) == input.engine_speed_rpm) {
            break;
        }
        col++;
    }

    while (getline(filein, line)) {
        std::stringstream ss(line);
        std::string value;
        int currentCol = 0;

        getline(ss, value, ','); // Read the first column (throttle position)

        if (std::stod(value) == input.throttle_position) {
            while (getline(ss, value, ',')) {
                if (currentCol == col) {
                    target = value;
                    break;
                }
                currentCol++;
            }
        }

        if (!target.empty()) {
            break;
        }
    }

    filein.close();

    return std::stod(target); // Convert the string to double and return
}

double Controller::measuredValue(const ControllerInput& input, const char* name, double default_value) {
    if (!name || !input.measured_values.items) {
        return default_value;
    }

    for (std::size_t index = 0; index < input.measured_values.count; ++index) {
        const MeasuredSignal& signal = input.measured_values.items[index];
        if (signal.name && std::string(signal.name) == name) {
            return signal.value;
        }
    }

    return default_value;
}