#ifndef PID_CONTROLLER_H
#define PID_CONTROLLER_H

#include "Controller.h"

class PIDController : public Controller {
public:
    PIDController(double kp = 0.5, double ki = 0.1, double kd = 0.01,
                  double min_out = 0.0, double max_out = 1.0);
    double compute(const ControllerInput& input) override;

private:
    double kp_, ki_, kd_;
    double integral_;
    double last_error_;
    double last_time_;
    double min_out_, max_out_;
};

#endif // PID_CONTROLLER_H