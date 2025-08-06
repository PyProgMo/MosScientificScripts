# AutoStage Coordinate Creator - C++ Version

This C++ application provides the same functionality as the Python `autostage_coord_creator.py` script but with improved GUI interfaces and enhanced user experience.

## Features

- **Coordinate Generation**: Creates a 3D grid of coordinates based on start/end positions and step counts
- **Micrometer Precision**: Designed for micrometer coordinates with nanometer precision (0.001 step size)
- **Boundary Validation**: Applies configurable min/max bounds (0-300 μm) for each axis
- **Flexible Output**: Saves coordinates to a text file in CSV format
- **Multiple GUI Options**: Windows native GUI and Tcl/Tk interface
- **Enhanced Input Validation**: Error handling with fallback to sensible defaults
- **Keyboard Navigation**: Full tab navigation support between input fields
- **Pre-filled Defaults**: Ready-to-use default values for quick setup

## Available Versions

### 1. Windows Native GUI (Recommended)
- **File**: `build_wingui\AutoStageGUI_Updated.exe`
- **Features**: Native Windows interface, no external dependencies
- **Tab Navigation**: ✅ Full keyboard navigation support
- **Default Values**: ✅ Pre-filled with boundary values

### 2. Console Version  
- **File**: `build_vs\AutoStageConsole.exe`
- **Features**: Text-based interface, good for testing and automation

### 3. Tcl/Tk GUI
- **Requires**: ActiveTcl installation
- **Features**: Cross-platform GUI similar to original Tkinter

## Requirements

- C++17 compatible compiler
- Visual Studio 2019/2022 (for Windows)
- CMake 3.16 or higher (optional)

## Quick Start (Windows)

1. **Run the pre-built executable**:
   ```
   build_wingui\AutoStageGUI_Updated.exe
   ```

2. **Use default values or enter your coordinates**:
   - All fields are pre-filled with sensible defaults
   - Units are in micrometers (μm)
   - Minimum step size is 1 nm (0.001)

3. **Navigate with keyboard**:
   - Press `Tab` to move between fields
   - Press `Shift+Tab` to move backwards
   - Order: X Start → X End → Y Start → Y End → Z Start → Z End → X Steps → Y Steps → Z Steps

4. **Generate and save**:
   - Click "Create Coordinates" or press Enter
   - Click "Save to File" to export as CSV

## Building from Source

### Windows with Visual Studio

Use the provided build scripts:

```bash
# For Windows native GUI (recommended)
.\build_updated_gui.bat

# For console version
.\compile_vs.bat

# For Tcl/Tk version (requires ActiveTcl)
.\build_tclgui_smart.ps1
```

### Manual Compilation

```bash
# Navigate to build directory
cd build_wingui

# Compile with Visual Studio tools
cl /EHsc /std:c++17 ..\windows_gui_main.cpp ..\AutoStageCoordCreator.cpp /Fe:AutoStageGUI.exe /link user32.lib gdi32.lib comctl32.lib comdlg32.lib
```

## Usage Guide

### Default Configuration
- **Boundaries**: 0.000 to 300.000 μm for all axes
- **Precision**: 3 decimal places (nanometer precision)
- **Default Steps**: 0.001 (1 nanometer)
- **Output Format**: CSV with x,y,z coordinates

### Input Fields
- **Start Values**: Lower bounds for each axis (default: 0.000)
- **End Values**: Upper bounds for each axis (default: 300.000)  
- **Step Values**: Number of steps or step size (default: 0.001)

### Keyboard Navigation
- `Tab`: Move to next field
- `Shift+Tab`: Move to previous field
- `Enter`: Activate focused button
- Auto-focus starts on X Start field

### Output Format
```
x1,y1,z1
x2,y2,z2
x3,y3,z3
...
```

## Core Classes

### AutoStageCoordCreator
- Handles coordinate generation logic
- 3 decimal place precision for micrometer coordinates
- Boundary checking with user input preservation
- File I/O operations

### WindowsGUI (Native)
- Windows API-based interface
- Tab navigation support
- Input validation with default fallbacks
- Native file dialogs

### AutoStageGUI (Tcl/Tk)
- Cross-platform Tcl/Tk interface
- Grid layout matching Python version
- Similar keyboard navigation

## Improvements Over Python Version

- **Enhanced Input Validation**: Automatic fallback to defaults for invalid input
- **Keyboard Navigation**: Full tab support for efficient data entry
- **Pre-filled Defaults**: No need to enter boundary values manually
- **Native Performance**: Faster coordinate generation for large datasets
- **Multiple Interfaces**: Choose between console, Windows native, or Tcl/Tk
- **Improved Precision**: 3 decimal places for nanometer accuracy

## Configuration

- **Default Bounds**: 0-300 μm (modifiable in `AutoStageCoordCreator` constructor)
- **Default Precision**: 3 decimal places (0.001 μm = 1 nm)
- **Tab Order**: Logical flow through coordinate entry fields

## Troubleshooting

- **Build Issues**: Ensure Visual Studio 2019/2022 is installed
- **Tab Navigation**: Use the updated executable (`AutoStageGUI_Updated.exe`)
- **File Permissions**: Run as administrator if file save fails
- **Large Datasets**: Use console version for very large coordinate sets
