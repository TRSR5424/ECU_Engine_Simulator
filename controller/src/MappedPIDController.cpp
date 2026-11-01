/** @file MappedPIDController.cpp
 *  @brief Native controller MappedPIDController implementation.
 */

#include "MappedPIDController.h"
#include <algorithm>

MappedPIDController::MappedPIDController(double kp, double ki, double kd, double min_out, double max_out)
    : kp_(kp), ki_(ki), kd_(kd), integral_(0.0), last_error_(0.0), last_time_(-1.0),
      min_out_(min_out), max_out_(max_out) {}

double MappedPIDController::compute(const ControllerInput& input)
{
    // Feedforward component
    double fuel_map_value = fuelMapLookup(input);

    // PID correction component
    double error = measuredValue(input, "air_fuel_ratio") - input.target_air_fuel_ratio;
    double current_time = input.time_seconds;

    if (last_time_ < 0)
    {
        last_time_ = current_time;
        last_error_ = error;

        return fuel_map_value; // Use base fuel, no correction initially
    }

    double delta_time = current_time - last_time_;

    if (delta_time <= 0.0)
    {
        return fuel_map_value;
    }

    integral_ += error * delta_time;

    double derivative = (error - last_error_) / delta_time;

    double correction =
        kp_ * error +
        ki_ * integral_ +
        kd_ * derivative;

    correction = std::clamp(correction, min_out_, max_out_);

    last_error_ = error;
    last_time_ = current_time;

    // Feedforward + feedback
    return fuel_map_value + correction;
}