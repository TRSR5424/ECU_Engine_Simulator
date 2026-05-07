#include "ControllerFactory.h"
#include "Controller.h"

/**
 * C interface for Python ctypes binding.
 */
extern "C" {
    struct ControllerHandle {
        void* controller_ptr;
    };

    ControllerHandle* create_fixed_controller() {
        auto* handle = new ControllerHandle();
        handle->controller_ptr = ControllerFactory::createFixedController();
        return handle;
    }

    double controller_compute(
        ControllerHandle* handle,
        double time_seconds,
        double throttle_position,
        double target_air_fuel_ratio,
        double measured_air_fuel_ratio,
        double engine_speed_rpm,
        double torque,
        double air_mass,
        double fuel_mass
    ) {
        if (!handle || !handle->controller_ptr) return 0.0;
        auto* controller = static_cast<Controller*>(handle->controller_ptr);
        ControllerInput input{
            time_seconds,
            throttle_position,
            target_air_fuel_ratio,
            measured_air_fuel_ratio,
            engine_speed_rpm,
            torque,
            air_mass,
            fuel_mass,
        };
        return controller->compute(input);
    }

    void destroy_controller(ControllerHandle* handle) {
        if (!handle) return;
        auto* controller = static_cast<Controller*>(handle->controller_ptr);
        delete controller;
        delete handle;
    }
}

