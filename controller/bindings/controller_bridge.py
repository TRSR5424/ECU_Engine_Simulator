"""Python binding to the C++ controller via ctypes."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ControllerInput:
    """Structured input to a controller with all available state information.
    
    Controllers can use any subset of these fields. Future controllers may
    declare which fields they need, but all are available here.
    """

    time_seconds: float
    throttle_position: float
    target_air_fuel_ratio: float
    measured_air_fuel_ratio: float
    engine_speed_rpm: float
    torque: float
    air_mass: float
    fuel_mass: float


class ControllerBridge:
    """Wrapper around the C++ controller library loaded via ctypes."""

    FIXED_FUEL_INJECTION = 0.08

    def __init__(self, config: dict | None = None):
        self._lib: Optional[ctypes.CDLL] = None
        self._handle: Optional[ctypes.c_void_p] = None
        self._controller_type: str = "fixed"
        self._config: dict = config or {}

        # Allow overriding the fallback fixed fuel injection value via config
        if config:
            self._controller_type = config.get("type", "fixed").lower()
            if "fixed_fuel_injection" in config:
                try:
                    self.FIXED_FUEL_INJECTION = float(config["fixed_fuel_injection"])
                except Exception:
                    # keep default if parsing fails
                    pass

        self._load_library()
        self._create_controller()

    def _load_library(self) -> None:
        """Locate and load the compiled C++ shared library."""
        lib_dir = Path(__file__).parent
        project_root = lib_dir.parent.parent
        
        # Try common library names for different platforms
        lib_names = [
            lib_dir / "libcontroller_cpp.so",      # Linux
            lib_dir / "libcontroller_cpp.dylib",   # macOS
            lib_dir / "controller_cpp.dll",        # Windows
            lib_dir / "Release" / "controller_cpp.dll",
            lib_dir / "Debug" / "controller_cpp.dll",
            project_root / "build" / "Release" / "controller_cpp.dll",
            project_root / "build" / "Debug" / "controller_cpp.dll",
            project_root / "build" / "controller_cpp.dll",
        ]
        
        for lib_path in lib_names:
            if lib_path.exists():
                try:
                    self._lib = ctypes.CDLL(str(lib_path))
                    return
                except OSError:
                    # library present but failed to load; fall back to pure-Python
                    self._lib = None
                    return

        # If the shared library isn't available, don't fail — allow a Python fallback.
        self._lib = None

    def _create_controller(self) -> None:
        """Create a controller instance in C++ based on controller type."""
        # If C++ library wasn't loaded, skip creating the native controller and
        # rely on the Python fallback behavior in `compute()`.
        if not self._lib:
            self._handle = None
            return

        # Map controller type to the corresponding C function name
        create_func_name = f"create_{self._controller_type}_controller"

        # Check if the function exists in the library
        if not hasattr(self._lib, create_func_name):
            # Fall back to Python if the specific controller type isn't available
            self._handle = None
            return

        # Define function signature for the C++ create function
        create_func = getattr(self._lib, create_func_name)
        create_func.restype = ctypes.c_void_p

        # Call appropriate creator based on controller type
        if self._controller_type == "pid":
            # PID controller requires tuning parameters
            kp = float(self._config.get("kp", 0.1)) if hasattr(self, "_config") else 0.1
            ki = float(self._config.get("ki", 0.01)) if hasattr(self, "_config") else 0.01
            kd = float(self._config.get("kd", 0.01)) if hasattr(self, "_config") else 0.01
            min_out = float(self._config.get("min_out", 0.0)) if hasattr(self, "_config") else 0.0
            max_out = float(self._config.get("max_out", 0.5)) if hasattr(self, "_config") else 0.5
            
            create_func.argtypes = [
                ctypes.c_double,  # kp
                ctypes.c_double,  # ki
                ctypes.c_double,  # kd
                ctypes.c_double,  # min_out
                ctypes.c_double,  # max_out
            ]
            self._handle = create_func(
                ctypes.c_double(kp),
                ctypes.c_double(ki),
                ctypes.c_double(kd),
                ctypes.c_double(min_out),
                ctypes.c_double(max_out),
            )
        else:
            # Fixed controller and others take no parameters
            create_func.argtypes = []
            self._handle = create_func()

        if not self._handle:
            # Failed to create native controller: fall back to Python.
            self._handle = None

    def compute(self, input: ControllerInput) -> float:
        """Call the controller to compute fuel injection.
        
        Args:
            input: ControllerInput dataclass with all available state information.
                   Controllers use whatever fields they need.
        
        Returns:
            Fuel injection value.
        """
        # If the C++ library/controller isn't available, return the fixed
        # controller value. This keeps the simulator runnable in
        # environments where the native build hasn't been performed.
        if not self._lib or not self._handle:
            return float(self.FIXED_FUEL_INJECTION)

        # Define function signature for C++ controller_compute
        self._lib.controller_compute.argtypes = [
            ctypes.c_void_p,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
            ctypes.c_double,
        ]
        self._lib.controller_compute.restype = ctypes.c_double

        return float(
            self._lib.controller_compute(
                self._handle,
                ctypes.c_double(input.time_seconds),
                ctypes.c_double(input.throttle_position),
                ctypes.c_double(input.target_air_fuel_ratio),
                ctypes.c_double(input.measured_air_fuel_ratio),
                ctypes.c_double(input.engine_speed_rpm),
                ctypes.c_double(input.torque),
                ctypes.c_double(input.air_mass),
                ctypes.c_double(input.fuel_mass),
            )
        )

    def __del__(self):
        """Clean up the C++ controller on deletion."""
        if self._lib and self._handle:
            self._lib.destroy_controller.argtypes = [ctypes.c_void_p]
            self._lib.destroy_controller(self._handle)

