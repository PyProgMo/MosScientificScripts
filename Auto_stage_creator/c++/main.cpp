#include "AutoStageGUI.h"
#include <iostream>

int main(int argc, char *argv[]) {
    try {
        // Create and run the GUI
        AutoStageGUI gui;
        gui.run();
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
