#ifndef CONTROLLER_FACTORY_H
#define CONTROLLER_FACTORY_H

class Controller;

/**
 * Factory for creating controller instances.
 */
class ControllerFactory {
public:
    static Controller* createFixedController();
};

#endif // CONTROLLER_FACTORY_H
