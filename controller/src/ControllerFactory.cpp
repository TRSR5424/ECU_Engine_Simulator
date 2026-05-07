#include "ControllerFactory.h"
#include "FixedController.h"

Controller* ControllerFactory::createFixedController() {
    return new FixedController();
}
