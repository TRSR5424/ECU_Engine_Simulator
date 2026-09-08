#include "ControllerFactory.h"
#include "FixedController.h"
#include "PIDController.h"
#include "MappedPIDController.h"
#include "TrueMapped.h"

Controller* ControllerFactory::createFixedController() {
    return new FixedController();
}

Controller* ControllerFactory::createPIDController(double kp, double ki, double kd, double min_out, double max_out) {
    return new PIDController(kp, ki, kd, min_out, max_out);
}

Controller* ControllerFactory::createMappedPIDController(double kp, double ki, double kd, double min_out, double max_out) {
    return new MappedPIDController(kp, ki, kd, min_out, max_out);
}

Controller* ControllerFactory::createTrueMappedController() {
    // High fidelity Map suggested
    return new TrueMapped();
}