/** @file FixedController.cpp
 *  @brief Native controller FixedController implementation.
 */

#include "FixedController.h"

double FixedController::compute(const ControllerInput& input) {
    (void)input;
    return kFixedFuelInjection;
}
