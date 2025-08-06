#include "AutoStageGUI.h"
#include <iostream>
#include <sstream>
#include <fstream>

AutoStageGUI::AutoStageGUI() : interp(nullptr) {
    coordCreator = std::make_unique<AutoStageCoordCreator>();
    
    // Create Tcl interpreter
    interp = Tcl_CreateInterp();
    if (Tcl_Init(interp) != TCL_OK) {
        std::cerr << "Failed to initialize Tcl: " << Tcl_GetStringResult(interp) << std::endl;
        return;
    }
    
    // Initialize Tk
    if (Tk_Init(interp) != TCL_OK) {
        std::cerr << "Failed to initialize Tk: " << Tcl_GetStringResult(interp) << std::endl;
        return;
    }
    
    setupUI();
}

AutoStageGUI::~AutoStageGUI() {
    if (interp) {
        Tcl_DeleteInterp(interp);
    }
}

void AutoStageGUI::setupUI() {
    // Set window title
    Tcl_Eval(interp, "wm title . \"AutoStage Coordinate Creator\"");
    
    // Set window size
    Tcl_Eval(interp, "wm geometry . 500x400");
    
    createWidgets();
    setupCallbacks();
}

void AutoStageGUI::createWidgets() {
    // Create main frame
    Tcl_Eval(interp, "frame .main -padx 10 -pady 10");
    Tcl_Eval(interp, "pack .main -fill both -expand true");
    
    // Create input frame
    Tcl_Eval(interp, "labelframe .main.input -text \"Coordinate Parameters\" -padx 5 -pady 5");
    Tcl_Eval(interp, "pack .main.input -fill x -pady 5");
    
    // Create grid of input fields (similar to Python tkinter layout)
    const char* inputScript = R"(
        # Row 0: X Start and X End
        label .main.input.lbl_x_start -text "X Start:"
        entry .main.input.x_start -width 15
        label .main.input.lbl_x_end -text "X End:"
        entry .main.input.x_end -width 15
        
        grid .main.input.lbl_x_start -row 0 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.x_start -row 0 -column 1 -padx 2 -pady 2
        grid .main.input.lbl_x_end -row 0 -column 2 -sticky w -padx 2 -pady 2
        grid .main.input.x_end -row 0 -column 3 -padx 2 -pady 2
        
        # Row 1: Y Start and Y End
        label .main.input.lbl_y_start -text "Y Start:"
        entry .main.input.y_start -width 15
        label .main.input.lbl_y_end -text "Y End:"
        entry .main.input.y_end -width 15
        
        grid .main.input.lbl_y_start -row 1 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.y_start -row 1 -column 1 -padx 2 -pady 2
        grid .main.input.lbl_y_end -row 1 -column 2 -sticky w -padx 2 -pady 2
        grid .main.input.y_end -row 1 -column 3 -padx 2 -pady 2
        
        # Row 2: Z Start and Z End
        label .main.input.lbl_z_start -text "Z Start:"
        entry .main.input.z_start -width 15
        label .main.input.lbl_z_end -text "Z End:"
        entry .main.input.z_end -width 15
        
        grid .main.input.lbl_z_start -row 2 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.z_start -row 2 -column 1 -padx 2 -pady 2
        grid .main.input.lbl_z_end -row 2 -column 2 -sticky w -padx 2 -pady 2
        grid .main.input.z_end -row 2 -column 3 -padx 2 -pady 2
        
        # Row 3: X Steps and Y Steps
        label .main.input.lbl_nx -text "X Steps:"
        entry .main.input.nx -width 15
        label .main.input.lbl_ny -text "Y Steps:"
        entry .main.input.ny -width 15
        
        grid .main.input.lbl_nx -row 3 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.nx -row 3 -column 1 -padx 2 -pady 2
        grid .main.input.lbl_ny -row 3 -column 2 -sticky w -padx 2 -pady 2
        grid .main.input.ny -row 3 -column 3 -padx 2 -pady 2
        
        # Row 4: Z Steps
        label .main.input.lbl_nz -text "Z Steps:"
        entry .main.input.nz -width 15
        
        grid .main.input.lbl_nz -row 4 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.nz -row 4 -column 1 -padx 2 -pady 2
    )";
    
    Tcl_Eval(interp, inputScript);
    
    // Create button frame
    Tcl_Eval(interp, "frame .main.buttons");
    Tcl_Eval(interp, "pack .main.buttons -fill x -pady 10");
    
    // Create buttons (matching Python layout)
    Tcl_Eval(interp, "button .main.buttons.create -text \"Create Coordinates\" -command create_coords");
    Tcl_Eval(interp, "button .main.buttons.save -text \"Save to File\" -command save_file -state disabled");
    
    Tcl_Eval(interp, "pack .main.buttons.create -side left -padx 5");
    Tcl_Eval(interp, "pack .main.buttons.save -side left -padx 5");
    
    // Create status label
    Tcl_Eval(interp, "label .main.status -text \"Ready to create coordinates...\" -fg blue");
    Tcl_Eval(interp, "pack .main.status -fill x -pady 5");
}

void AutoStageGUI::setupCallbacks() {
    // Register C++ callback functions with Tcl
    Tcl_CreateCommand(interp, "create_coords", createCoordinatesCallback, this, nullptr);
    Tcl_CreateCommand(interp, "save_file", saveToFileCallback, this, nullptr);
}

int AutoStageGUI::createCoordinatesCallback(ClientData clientData, Tcl_Interp *interp, int argc, const char *argv[]) {
    AutoStageGUI* gui = static_cast<AutoStageGUI*>(clientData);
    
    try {
        // Get values from entry widgets with validation
        std::vector<double> params(9);
        
        // Default values to use if conversion fails
        std::vector<double> defaults = {0.0, 0.0, 0.0, 300.0, 300.0, 300.0, 10.0, 10.0, 1.0};
        std::vector<std::string> fieldNames = {
            ".main.input.x_start", ".main.input.y_start", ".main.input.z_start",
            ".main.input.x_end", ".main.input.y_end", ".main.input.z_end",
            ".main.input.nx", ".main.input.ny", ".main.input.nz"
        };
        std::vector<std::string> fieldLabels = {
            "X Start", "Y Start", "Z Start", "X End", "Y End", "Z End",
            "X Steps", "Y Steps", "Z Steps"
        };
        
        std::string validationMessages;
        bool hasErrors = false;
        
        // Validate each input field
        for (size_t i = 0; i < 9; ++i) {
            std::string value = gui->getEntryValue(fieldNames[i]);
            
            if (value.empty()) {
                params[i] = defaults[i];
                validationMessages += fieldLabels[i] + " was empty, using default: " + 
                                    std::to_string(defaults[i]) + "\n";
            } else {
                try {
                    if (i >= 6) { // Steps fields (nx, ny, nz) should be integers
                        int intVal = std::stoi(value);
                        if (intVal < 0) {
                            throw std::invalid_argument("Steps must be non-negative");
                        }
                        params[i] = static_cast<double>(intVal);
                    } else {
                        params[i] = std::stod(value);
                    }
                } catch (const std::exception&) {
                    params[i] = defaults[i];
                    validationMessages += fieldLabels[i] + " '" + value + 
                                        "' is not a valid number, using default: " + 
                                        std::to_string(defaults[i]) + "\n";
                }
            }
        }
        
        // Show validation messages if any defaults were used
        if (!validationMessages.empty()) {
            gui->showInfo("Input Validation:\n" + validationMessages + 
                         "\nProceeding with corrected values...");
        }
        
        // Debug output to console
        std::cout << "Creating coordinates with parameters:" << std::endl;
        std::cout << "X: " << params[0] << " to " << params[3] << " (" << params[6] << " steps)" << std::endl;
        std::cout << "Y: " << params[1] << " to " << params[4] << " (" << params[7] << " steps)" << std::endl;
        std::cout << "Z: " << params[2] << " to " << params[5] << " (" << params[8] << " steps)" << std::endl;
        
        gui->coordCreator->createCoordinates(params);
        
        // Update status
        std::string statusMsg = "Successfully created " + std::to_string(gui->coordCreator->getCoordinateCount()) + " coordinates";
        Tcl_Eval(interp, (".main.status configure -text \"" + statusMsg + "\" -fg green").c_str());
        
        // Enable save button
        Tcl_Eval(interp, ".main.buttons.save configure -state normal");
        
    } catch (const std::exception& e) {
        gui->showError("Error creating coordinates: " + std::string(e.what()));
        Tcl_Eval(interp, ".main.status configure -text \"Error creating coordinates\" -fg red");
    }
    
    return TCL_OK;
}

int AutoStageGUI::saveToFileCallback(ClientData clientData, Tcl_Interp *interp, int argc, const char *argv[]) {
    AutoStageGUI* gui = static_cast<AutoStageGUI*>(clientData);
    
    // Use Tcl's file dialog
    const char* fileDialogScript = R"(
        set filename [tk_getSaveFile -title "Save Coordinates" -defaultextension ".txt" -filetypes {{"Text files" ".txt"} {"All files" "*"}}]
    )";
    
    if (Tcl_Eval(interp, fileDialogScript) == TCL_OK) {
        std::string filename = Tcl_GetStringResult(interp);
        
        if (!filename.empty() && filename != "0") {
            try {
                gui->coordCreator->writeCoordinates(filename);
                
                std::string statusMsg = "Coordinates saved to: " + filename;
                Tcl_Eval(interp, (".main.status configure -text \"" + statusMsg + "\" -fg green").c_str());
                
                gui->showInfo("Coordinates successfully saved to:\n" + filename);
                
            } catch (const std::exception& e) {
                gui->showError("Failed to save coordinates: " + std::string(e.what()));
                Tcl_Eval(interp, ".main.status configure -text \"Error saving coordinates\" -fg red");
            }
        }
    }
    
    return TCL_OK;
}

std::string AutoStageGUI::getEntryValue(const std::string& widgetName) {
    std::string cmd = widgetName + " get";
    if (Tcl_Eval(interp, cmd.c_str()) == TCL_OK) {
        return Tcl_GetStringResult(interp);
    }
    return "";
}

void AutoStageGUI::showError(const std::string& message) {
    std::string cmd = "tk_messageBox -icon error -title \"Error\" -message \"" + message + "\"";
    Tcl_Eval(interp, cmd.c_str());
}

void AutoStageGUI::showInfo(const std::string& message) {
    std::string cmd = "tk_messageBox -icon info -title \"Success\" -message \"" + message + "\"";
    Tcl_Eval(interp, cmd.c_str());
}

void AutoStageGUI::run() {
    if (interp) {
        Tk_MainLoop();
    }
}
