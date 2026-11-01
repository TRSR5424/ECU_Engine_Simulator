/** @file Controller.h
 *  @brief Native controller Controller implementation.
 */

#ifndef CONTROLLER_H
#define CONTROLLER_H

#include <cstddef>

/**
 * A single measured signal passed from Python.
 */
struct MeasuredSignal {
    const char* name;
    double value;
};

/**
 * Inputs shared by all controller implementations.
 *
 * Fixed controllers can ignore fields they do not need, while future
 * feedback controllers can use the full engine/sensor/reference context.
 */
struct MeasuredValues {
    std::size_t count;
    const MeasuredSignal* items;
};

struct ControllerInput {
    double time_seconds;
    double throttle_position;
    double target_air_fuel_ratio;
    MeasuredValues measured_values;
    double engine_speed_rpm;
    double torque;
    double air_mass;
    double fuel_mass;
    char engine_map[]; // Path to the fuel map file
};

/**
 * Base controller interface.
 * Computes fuel injection from the current control context.
 */
class Controller {
public:
    virtual ~Controller() = default;
    virtual double compute(const ControllerInput& input) = 0;
    virtual double fuelMapLookup(const ControllerInput& input);
    double measuredValue(const ControllerInput& input, const char* name, double default_value = 0.0);
};

#endif // CONTROLLER_H
