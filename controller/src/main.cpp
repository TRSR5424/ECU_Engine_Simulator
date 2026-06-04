#include "ControllerFactory.h"
#include "Controller.h"

#if defined(_WIN32)
#define CONTROLLER_API __declspec(dllexport)
#else
#define CONTROLLER_API
#endif

/**
 * C interface for Python ctypes binding.
 */
extern "C" {
    struct ControllerHandle {
        void* controller_ptr;
    };

    CONTROLLER_API ControllerHandle* create_fixed_controller() {
        auto* handle = new ControllerHandle();
        handle->controller_ptr = ControllerFactory::createFixedController();
        return handle;
    }

    CONTROLLER_API ControllerHandle* create_pid_controller(double kp, double ki, double kd, double min_out, double max_out) {
        auto* handle = new ControllerHandle();
        handle->controller_ptr = ControllerFactory::createPIDController(kp, ki, kd, min_out, max_out);
        return handle;
    }

    CONTROLLER_API double controller_compute(
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

    CONTROLLER_API void destroy_controller(ControllerHandle* handle) {
        if (!handle) return;
        auto* controller = static_cast<Controller*>(handle->controller_ptr);
        delete controller;
        delete handle;
    }
}

