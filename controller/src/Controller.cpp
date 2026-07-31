#include "Controller.h"
#include <algorithm>
#include <string>
#include <fstream>
#include <sstream>

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