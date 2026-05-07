"""Python binding to the C++ controller via ctypes."""

from __future__ import annotations

import ctypes
from pathlib import Path
from typing import Optional


class ControllerBridge:
    """Wrapper around the C++ controller library loaded via ctypes."""

    FIXED_FUEL_INJECTION = 0.08

    def __init__(self):
        self._lib: Optional[ctypes.CDLL] = None
        self._handle: Optional[ctypes.c_void_p] = None
        self._load_library()
        self._create_controller()

    def _load_library(self) -> None:
        """Locate and load the compiled C++ shared library."""
        lib_dir = Path(__file__).parent
        
        # Try common library names for different platforms
        lib_names = [
            lib_dir / "libcontroller_cpp.so",      # Linux
            lib_dir / "libcontroller_cpp.dylib",   # macOS
            lib_dir / "controller_cpp.dll",        # Windows
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
        """Create a fixed controller instance in C++."""
        # If C++ library wasn't loaded, skip creating the native controller and
        # rely on the Python fallback behavior in `compute()`.
        if not self._lib:
            self._handle = None
            return

        # Define function signature for C++ create_fixed_controller
        self._lib.create_fixed_controller.argtypes = []
        self._lib.create_fixed_controller.restype = ctypes.c_void_p

        self._handle = self._lib.create_fixed_controller()

        if not self._handle:
            # Failed to create native controller: fall back to Python.
            self._handle = None

    def compute(
        self,
        *,
        time_seconds: float,
        throttle_position: float,
        target_air_fuel_ratio: float,
        measured_air_fuel_ratio: float,
        engine_speed_rpm: float,
        torque: float,
        air_mass: float,
        fuel_mass: float,
    ) -> float:
        """Call the C++ controller to compute fuel injection."""
        # If the C++ library/controller isn't available, return the fixed
        # fixed controller value. This keeps the simulator runnable in
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
                ctypes.c_double(time_seconds),
                ctypes.c_double(throttle_position),
                ctypes.c_double(target_air_fuel_ratio),
                ctypes.c_double(measured_air_fuel_ratio),
                ctypes.c_double(engine_speed_rpm),
                ctypes.c_double(torque),
                ctypes.c_double(air_mass),
                ctypes.c_double(fuel_mass),
            )
        )

    def __del__(self):
        """Clean up the C++ controller on deletion."""
        if self._lib and self._handle:
            self._lib.destroy_controller.argtypes = [ctypes.c_void_p]
            self._lib.destroy_controller(self._handle)

