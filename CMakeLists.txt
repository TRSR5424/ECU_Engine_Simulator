# Minimal CMake for controller C++ components
cmake_minimum_required(VERSION 3.10)
project(controller)

# Compiler flags
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Shared library for Python binding via ctypes
add_library(controller_cpp SHARED
    controller/src/main.cpp
    controller/src/PIDController.cpp
    controller/src/ControllerFactory.cpp
    controller/src/FixedController.cpp
)

target_include_directories(controller_cpp PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/controller/include
)

# Output to a predictable location
set_target_properties(controller_cpp PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/controller/bindings"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/controller/bindings"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/controller/bindings"
)
