#include "AutoStageCoordCreator.h"
#include <iostream>
#include <vector>
#include <string>
#include <limits>

class SimpleConsoleGUI {
private:
    AutoStageCoordCreator coordCreator;
    
public:
    void run() {
        std::cout << "=== AutoStage Coordinate Creator ===" << std::endl;
        std::cout << "Console Version" << std::endl;
        std::cout << "====================================" << std::endl;
        
        while (true) {
            std::cout << "\nOptions:" << std::endl;
            std::cout << "1. Create coordinates" << std::endl;
            std::cout << "2. Exit" << std::endl;
            std::cout << "Choice: ";
            
            int choice;
            std::cin >> choice;
            
            if (choice == 1) {
                createCoordinates();
            } else if (choice == 2) {
                break;
            } else {
                std::cout << "Invalid choice!" << std::endl;
            }
        }
    }
    
private:
    void createCoordinates() {
        std::cout << "\n--- Enter Coordinate Parameters ---" << std::endl;
        
        double x_start, y_start, z_start;
        double x_end, y_end, z_end;
        int nx, ny, nz;
        
        std::cout << "X Start: ";
        std::cin >> x_start;
        
        std::cout << "Y Start: ";
        std::cin >> y_start;
        
        std::cout << "Z Start: ";
        std::cin >> z_start;
        
        std::cout << "X End: ";
        std::cin >> x_end;
        
        std::cout << "Y End: ";
        std::cin >> y_end;
        
        std::cout << "Z End: ";
        std::cin >> z_end;
        
        std::cout << "X Steps: ";
        std::cin >> nx;
        
        std::cout << "Y Steps: ";
        std::cin >> ny;
        
        std::cout << "Z Steps: ";
        std::cin >> nz;
        
        try {
            std::vector<double> params = {x_start, y_start, z_start, x_end, y_end, z_end, 
                                        static_cast<double>(nx), static_cast<double>(ny), static_cast<double>(nz)};
            
            coordCreator.createCoordinates(params);
            
            std::cout << "\nSuccess! Created " << coordCreator.getCoordinateCount() << " coordinates." << std::endl;
            
            std::cout << "Enter filename to save (e.g., coordinates.txt): ";
            std::string filename;
            std::cin >> filename;
            
            coordCreator.writeCoordinates(filename);
            std::cout << "Coordinates saved to: " << filename << std::endl;
            
        } catch (const std::exception& e) {
            std::cout << "Error: " << e.what() << std::endl;
        }
        
        // Clear input buffer
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    }
};

int main() {
    SimpleConsoleGUI gui;
    gui.run();
    return 0;
}
