#include "ControllerFactory.h"
#include "FixedController.h"
#include "PIDController.h"

Controller* ControllerFactory::createFixedController() {
    return new FixedController();
}

Controller* ControllerFactory::createPIDController(double kp, double ki, double kd, double min_out, double max_out) {
    return new PIDController(kp, ki, kd, min_out, max_out);
}