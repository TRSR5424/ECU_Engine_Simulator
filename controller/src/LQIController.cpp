#include "LQIController.h"
#include <algorithm>

LQIController::LQIController(double q1, double q2, double r, double min_out, double max_out)
    : q1_(q1), q2_(q2), r_(r), min_out_(min_out), max_out_(max_out) { }

double LQIController::compute(const ControllerInput& input) {
    // Placeholder for LQI control logic
}