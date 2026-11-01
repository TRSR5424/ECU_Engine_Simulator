/** @file LQIController.h
 *  @brief Native controller LQIController implementation.
 */

#ifndef LQI_CONTROLLER_h
#define LQI_CONTROLLER_h

#include "Controller.h"

class LQIController : public Controller {
public:
    LQIController(double q1 = 1.0, double q2 = 1.0, double r = 1.0,
                  double min_out = 0.0, double max_out = 1.0);
    double compute(const ControllerInput& input) override;

private:
    double q1_, q2_, r_;
    double min_out_, max_out_;
};

#endif // LQI_CONTROLLER_h