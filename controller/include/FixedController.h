/** @file FixedController.h
 *  @brief Native controller FixedController implementation.
 */

#ifndef FIXED_CONTROLLER_H
#define FIXED_CONTROLLER_H

#include "Controller.h"

/**
 * Fixed output controller for MVP.
 * Always returns a constant fuel injection value.
 */
class FixedController : public Controller {
private:
    static constexpr double kFixedFuelInjection = 0.08;

public:
    FixedController() = default;
    double compute(const ControllerInput& input) override;
};

#endif // FIXED_CONTROLLER_H