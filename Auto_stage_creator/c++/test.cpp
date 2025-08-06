#include "AutoStageCoordCreator.h"
#include <iostream>
#include <vector>

// Test function equivalent to asctest() in the Python version
void testCoordCreator() {
    std::cout << "=== Testing AutoStageCoordCreator ===" << std::endl;
    
    AutoStageCoordCreator asc;
    asc.setRounding(2, 2, 2);
    
    // Test with parameters from Python version: [121, 101.3, 150, 126.32, 132.23, 150, 43, 86, 0]
    std::vector<double> params = {121, 101.3, 150, 126.32, 132.23, 150, 43, 86, 0};
    
    try {
        asc.createCoordinates(params);
        
        std::string filename = "test_coordinates.txt";
        asc.writeCoordinates(filename);
        
        std::cout << "Coordinates created and written to " << filename << std::endl;
        std::cout << "Total coordinates generated: " << asc.getCoordinateCount() << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

int main() {
    testCoordCreator();
    return 0;
}
