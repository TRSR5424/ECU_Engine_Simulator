/** @file ControllerFactory.h
 *  @brief Native controller ControllerFactory implementation.
 */

#ifndef CONTROLLER_FACTORY_H
#define CONTROLLER_FACTORY_H

class Controller;

/**
 * Factory for creating controller instances.
 */
class ControllerFactory {
public:
    static Controller* createFixedController();
    static Controller* createPIDController(double kp, double ki, double kd, double min_out, double max_out);
    static Controller* createMappedPIDController(double kp, double ki, double kd, double min_out, double max_out);
    static Controller* createTrueMappedController(); // High fidelity Map suggested
};

#endif // CONTROLLER_FACTORY_H
