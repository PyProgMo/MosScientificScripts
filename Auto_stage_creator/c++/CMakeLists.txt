cmake_minimum_required(VERSION 3.16)
project(AutoStageCoordCreator)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Tcl/Tk
find_package(TCL REQUIRED)
find_package(TK REQUIRED)

# Add executable
add_executable(AutoStageCoordCreator
    main.cpp
    AutoStageCoordCreator.cpp
    AutoStageGUI.cpp
)

# Link Tcl/Tk libraries
target_link_libraries(AutoStageCoordCreator ${TCL_LIBRARY} ${TK_LIBRARY})
target_include_directories(AutoStageCoordCreator PRIVATE ${TCL_INCLUDE_PATH} ${TK_INCLUDE_PATH})

# Set output directory
set_target_properties(AutoStageCoordCreator PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)
