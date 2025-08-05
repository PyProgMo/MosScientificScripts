Auto Stage Coordinate Creator
===========================

This tool helps create coordinate files for automated microscope stage positioning.

Usage
-----
1. Run autostage_coord_creator.py
2. Select your reference points on the stage
3. The program will generate a coordinates file in the required format

Requirements
------------
- Python 3.x
- numpy
- tkinter (usually comes with Python)

Steps
-----
1. Launch the program:
    python autostage_coord_creator.py

2. Click points on the stage visualization to mark your desired positions
    - Left click to add a point
    - Right click to remove the last point
    - Middle click or 'Enter' key to finish

3. The program will save the coordinates in a text file named 'stage_coordinates.txt'

Output Format
------------
The coordinates file will contain:
- One position per line
- Each line has X and Y coordinates separated by a tab
- Coordinates are in stage motor units

Notes
-----
- Make sure to calibrate your microscope stage before using the generated coordinates
- Keep the points within the valid range of your stage movement
- The coordinate system origin is at the top-left corner

For questions or issues, contact the microscopy facility staff.