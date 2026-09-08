// High fidelity Map suggested

#include "TrueMapped.h"

TrueMapped::TrueMapped() : Controller() {}

double TrueMapped::compute(const ControllerInput& input) {
    double fuel_map_value = fuelMapLookup(input);

    // No PID correction, just return the fuel map value
    return fuel_map_value;
}