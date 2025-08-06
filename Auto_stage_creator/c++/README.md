# AutoStage Coordinate Creator - C++ Version

This C++ application provides the same functionality as the Python `autostage_coord_creator.py` script but with a Tcl/Tk-based GUI, making it very similar to the original Tkinter implementation.

## Features

- **Coordinate Generation**: Creates a 3D grid of coordinates based on start/end positions and step counts
- **Boundary Validation**: Applies configurable min/max bounds for each axis
- **Flexible Output**: Saves coordinates to a text file in CSV format
- **Familiar GUI**: Built with Tcl/Tk for similarity to the original Tkinter interface
- **Input Validation**: Error handling and user feedback

## Requirements

- C++17 compatible compiler
- Tcl/Tk development libraries
- CMake 3.16 or higher

## Installing Tcl/Tk

### Windows
1. Download ActiveTcl from https://www.tcl.tk/software/tcltk/download.html
2. Install and make sure it's in your system PATH
3. Alternatively, install through vcpkg: `vcpkg install tcl tk`

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install tcl-dev tk-dev
```

### Linux (CentOS/RHEL)
```bash
sudo yum install tcl-devel tk-devel
```

## Building

### Windows with Visual Studio

1. Install Tcl/Tk as described above
2. Create build directory and run CMake:

```bash
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

### Linux/macOS

```bash
mkdir build
cd build
cmake ..
make
```

## Usage

1. **Input Parameters**:
   - Enter start and end coordinates for X, Y, Z axes
   - Specify the number of steps for each axis
   - Click "Create Coordinates"

2. **Save Results**:
   - After creating coordinates, use "Save to File" button
   - Choose location and filename for the output

3. **Output Format**:
   The generated file contains coordinates in CSV format:
   ```
   x1,y1,z1
   x2,y2,z2
   x3,y3,z3
   ...
   ```

## Core Classes

### AutoStageCoordCreator
- Handles coordinate generation logic
- Configurable rounding precision
- Boundary checking
- File I/O operations

### AutoStageGUI
- Tcl/Tk-based user interface (similar to Tkinter)
- Grid layout matching Python version
- File dialog integration
- Status feedback

## Advantages of Tcl/Tk over Qt

- **Closer to Original**: Tcl/Tk is very similar to Tkinter, maintaining the same look and feel
- **Lightweight**: Smaller footprint compared to Qt
- **Native Widgets**: Uses system-native widgets like Tkinter
- **Familiar Layout**: Grid-based layout system identical to Tkinter

## Configuration

The coordinate creator uses default bounds of 0-300 for all axes, which can be modified in the `AutoStageCoordCreator` constructor if needed.

Default rounding precision is 2 decimal places for all coordinates.
