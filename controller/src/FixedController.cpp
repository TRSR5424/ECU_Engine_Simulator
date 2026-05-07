#include "FixedController.h"

double FixedController::compute(const ControllerInput& input) {
    (void)input;
    return kFixedFuelInjection;
}
