#include "PIDController.h"
#include <algorithm>

PIDController::PIDController(double kp, double ki, double kd, double min_out, double max_out)
    : kp_(kp), ki_(ki), kd_(kd), integral_(0.0), last_error_(0.0), last_time_(-1.0),
      min_out_(min_out), max_out_(max_out) {}

double PIDController::compute(const ControllerInput& input) {
    double error = measuredValue(input, "air_fuel_ratio") - input.target_air_fuel_ratio;
    double current_time = input.time_seconds;

    if (last_time_ < 0) {
        last_time_ = current_time;
        last_error_ = error;
        return 0.0; // No control action on the first call
    }

    double delta_time = current_time - last_time_;
    integral_ += error * delta_time;
    double derivative = (error - last_error_) / delta_time;

    double output = kp_ * error + ki_ * integral_ + kd_ * derivative;
    output = std::clamp(output, min_out_, max_out_);

    last_error_ = error;
    last_time_ = current_time;

    return output;
}
