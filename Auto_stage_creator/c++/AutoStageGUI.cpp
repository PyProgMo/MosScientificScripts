#include "AutoStageGUI.h"
#include <iostream>
#include <sstream>
#include <fstream>
#include <iomanip>

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
    Tcl_Eval(interp, "wm geometry . 500x500");
    
    createWidgets();
    setupCallbacks();
}

void AutoStageGUI::createWidgets() {
    // Create main frame
    Tcl_Eval(interp, "frame .main -padx 10 -pady 10");
    Tcl_Eval(interp, "pack .main -fill both -expand true");
    
    // Create headline frame and labels
    Tcl_Eval(interp, "frame .main.header");
    Tcl_Eval(interp, "pack .main.header -fill x -pady 5");
    
    // Add headline with instructions
    Tcl_Eval(interp, "label .main.header.title -text \"Insert coordinates in micrometers\" -font {Arial 12 bold} -fg darkblue");
    Tcl_Eval(interp, "label .main.header.subtitle -text \"Minimum step size 1 nm\" -font {Arial 10} -fg gray");
    Tcl_Eval(interp, "pack .main.header.title -anchor w");
    Tcl_Eval(interp, "pack .main.header.subtitle -anchor w");
    
    // Create input frame
    Tcl_Eval(interp, "labelframe .main.input -text \"Coordinate Parameters\" -padx 5 -pady 5");
    Tcl_Eval(interp, "pack .main.input -fill x -pady 5");
    
    // Create grid of input fields with default values and tab order
    const char* inputScript = R"(
        # Row 0: X Start and X End
        label .main.input.lbl_x_start -text "X Start:"
        entry .main.input.x_start -width 15
        .main.input.x_start insert 0 "0.000"
        label .main.input.lbl_x_end -text "X End:"
        entry .main.input.x_end -width 15
        .main.input.x_end insert 0 "300.000"
        
        grid .main.input.lbl_x_start -row 0 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.x_start -row 0 -column 1 -padx 2 -pady 2
        grid .main.input.lbl_x_end -row 0 -column 2 -sticky w -padx 2 -pady 2
        grid .main.input.x_end -row 0 -column 3 -padx 2 -pady 2
        
        # Row 1: Y Start and Y End
        label .main.input.lbl_y_start -text "Y Start:"
        entry .main.input.y_start -width 15
        .main.input.y_start insert 0 "0.000"
        label .main.input.lbl_y_end -text "Y End:"
        entry .main.input.y_end -width 15
        .main.input.y_end insert 0 "300.000"
        
        grid .main.input.lbl_y_start -row 1 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.y_start -row 1 -column 1 -padx 2 -pady 2
        grid .main.input.lbl_y_end -row 1 -column 2 -sticky w -padx 2 -pady 2
        grid .main.input.y_end -row 1 -column 3 -padx 2 -pady 2
        
        # Row 2: Z Start and Z End
        label .main.input.lbl_z_start -text "Z Start:"
        entry .main.input.z_start -width 15
        .main.input.z_start insert 0 "0.000"
        label .main.input.lbl_z_end -text "Z End:"
        entry .main.input.z_end -width 15
        .main.input.z_end insert 0 "300.000"
        
        grid .main.input.lbl_z_start -row 2 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.z_start -row 2 -column 1 -padx 2 -pady 2
        grid .main.input.lbl_z_end -row 2 -column 2 -sticky w -padx 2 -pady 2
        grid .main.input.z_end -row 2 -column 3 -padx 2 -pady 2
        
        # Row 3: X Steps and Y Steps
        label .main.input.lbl_nx -text "X Steps:"
        entry .main.input.nx -width 15
        .main.input.nx insert 0 "0.001"
        label .main.input.lbl_ny -text "Y Steps:"
        entry .main.input.ny -width 15
        .main.input.ny insert 0 "0.001"
        
        grid .main.input.lbl_nx -row 3 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.nx -row 3 -column 1 -padx 2 -pady 2
        grid .main.input.lbl_ny -row 3 -column 2 -sticky w -padx 2 -pady 2
        grid .main.input.ny -row 3 -column 3 -padx 2 -pady 2
        
        # Row 4: Z Steps
        label .main.input.lbl_nz -text "Z Steps:"
        entry .main.input.nz -width 15
        .main.input.nz insert 0 "0.001"
        
        grid .main.input.lbl_nz -row 4 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.nz -row 4 -column 1 -padx 2 -pady 2
        
        # Add stepsize display section
        label .main.input.lbl_stepsize -text "Calculated Stepsizes:" -font {Arial 10 bold} -fg darkgreen
        grid .main.input.lbl_stepsize -row 5 -column 0 -columnspan 4 -sticky w -padx 2 -pady {10 2}
        
        # X and Y stepsize display
        label .main.input.lbl_x_stepsize -text "X Stepsize:"
        label .main.input.x_stepsize -text "N/A" -relief sunken -width 15 -bg white
        label .main.input.lbl_y_stepsize -text "Y Stepsize:"
        label .main.input.y_stepsize -text "N/A" -relief sunken -width 15 -bg white
        
        grid .main.input.lbl_x_stepsize -row 6 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.x_stepsize -row 6 -column 1 -padx 2 -pady 2
        grid .main.input.lbl_y_stepsize -row 6 -column 2 -sticky w -padx 2 -pady 2
        grid .main.input.y_stepsize -row 6 -column 3 -padx 2 -pady 2
        
        # Z stepsize display
        label .main.input.lbl_z_stepsize -text "Z Stepsize:"
        label .main.input.z_stepsize -text "N/A" -relief sunken -width 15 -bg white
        
        grid .main.input.lbl_z_stepsize -row 7 -column 0 -sticky w -padx 2 -pady 2
        grid .main.input.z_stepsize -row 7 -column 1 -padx 2 -pady 2
        
        # Set up tab order for keyboard navigation
        # Tab order: x_start -> x_end -> y_start -> y_end -> z_start -> z_end -> nx -> ny -> nz
        bind .main.input.x_start <Tab> {focus .main.input.x_end; break}
        bind .main.input.x_end <Tab> {focus .main.input.y_start; break}
        bind .main.input.y_start <Tab> {focus .main.input.y_end; break}
        bind .main.input.y_end <Tab> {focus .main.input.z_start; break}
        bind .main.input.z_start <Tab> {focus .main.input.z_end; break}
        bind .main.input.z_end <Tab> {focus .main.input.nx; break}
        bind .main.input.nx <Tab> {focus .main.input.ny; break}
        bind .main.input.ny <Tab> {focus .main.input.nz; break}
        bind .main.input.nz <Tab> {focus .main.input.x_start; break}
        
        # Shift+Tab for reverse navigation
        bind .main.input.x_start <Shift-Tab> {focus .main.input.nz; break}
        bind .main.input.x_end <Shift-Tab> {focus .main.input.x_start; break}
        bind .main.input.y_start <Shift-Tab> {focus .main.input.x_end; break}
        bind .main.input.y_end <Shift-Tab> {focus .main.input.y_start; break}
        bind .main.input.z_start <Shift-Tab> {focus .main.input.y_end; break}
        bind .main.input.z_end <Shift-Tab> {focus .main.input.z_start; break}
        bind .main.input.nx <Shift-Tab> {focus .main.input.z_end; break}
        bind .main.input.ny <Shift-Tab> {focus .main.input.nx; break}
        bind .main.input.nz <Shift-Tab> {focus .main.input.ny; break}
        
        # Set initial focus to first field
        focus .main.input.x_start
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
    
    // Create status display with text widget and scrollbar
    Tcl_Eval(interp, "frame .main.statusframe");
    Tcl_Eval(interp, "text .main.statusframe.status -height 5 -width 60 -wrap word -bg lightgray -fg black -state disabled -relief sunken -borderwidth 2");
    Tcl_Eval(interp, "scrollbar .main.statusframe.scroll -command \".main.statusframe.status yview\"");
    Tcl_Eval(interp, ".main.statusframe.status configure -yscrollcommand \".main.statusframe.scroll set\"");
    Tcl_Eval(interp, "pack .main.statusframe.scroll -side right -fill y");
    Tcl_Eval(interp, "pack .main.statusframe.status -side left -fill both -expand true");
    Tcl_Eval(interp, "pack .main.statusframe -fill both -expand true -pady 5");
    
    // Insert initial message
    Tcl_Eval(interp, ".main.statusframe.status configure -state normal");
    Tcl_Eval(interp, ".main.statusframe.status insert end \"Ready to create coordinates...\"");
    Tcl_Eval(interp, ".main.statusframe.status configure -state disabled");
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
        
        // Default values to use if conversion fails (matching the GUI defaults)
        std::vector<double> defaults = {0.0, 0.0, 0.0, 300.0, 300.0, 300.0, 0.001, 0.001, 0.001};
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
        gui->updateStatus(statusMsg);
        
        // Enable save button
        Tcl_Eval(interp, ".main.buttons.save configure -state normal");
        
        // Update stepsize display
        gui->updateStepsizeDisplay();
        
    } catch (const std::exception& e) {
        gui->showError("Error creating coordinates: " + std::string(e.what()));
        gui->updateStatus("Error creating coordinates: " + std::string(e.what()));
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
                gui->updateStatus(statusMsg);
                
                gui->showInfo("Coordinates successfully saved to:\n" + filename);
                
            } catch (const std::exception& e) {
                gui->showError("Failed to save coordinates: " + std::string(e.what()));
                gui->updateStatus("Error saving coordinates: " + std::string(e.what()));
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

void AutoStageGUI::updateStatus(const std::string& message) {
    // Clear the text widget and insert new message
    Tcl_Eval(interp, ".main.statusframe.status configure -state normal");
    Tcl_Eval(interp, ".main.statusframe.status delete 1.0 end");
    std::string escapedMsg = message;
    // Escape quotes in the message
    size_t pos = 0;
    while ((pos = escapedMsg.find("\"", pos)) != std::string::npos) {
        escapedMsg.replace(pos, 1, "\\\"");
        pos += 2;
    }
    Tcl_Eval(interp, (".main.statusframe.status insert end \"" + escapedMsg + "\"").c_str());
    Tcl_Eval(interp, ".main.statusframe.status configure -state disabled");
    // Scroll to the end
    Tcl_Eval(interp, ".main.statusframe.status see end");
}

void AutoStageGUI::updateStepsizeDisplay() {
    try {
        // Get the coordinate vectors from the coordCreator
        const auto& coords = coordCreator->getCoordinates();
        
        if (coords.size() >= 2) {
            // Calculate stepsize as difference between 0th and 1st coordinate
            double xStepsize = std::abs(std::get<0>(coords[1]) - std::get<0>(coords[0]));
            double yStepsize = std::abs(std::get<1>(coords[1]) - std::get<1>(coords[0])); 
            double zStepsize = std::abs(std::get<2>(coords[1]) - std::get<2>(coords[0]));
            
            // Format stepsizes with 6 decimal places
            std::ostringstream xss, yss, zss;
            xss << std::fixed << std::setprecision(6) << xStepsize;
            yss << std::fixed << std::setprecision(6) << yStepsize;
            zss << std::fixed << std::setprecision(6) << zStepsize;
            
            // Update the display labels
            Tcl_Eval(interp, (".main.input.x_stepsize configure -text \"" + xss.str() + "\"").c_str());
            Tcl_Eval(interp, (".main.input.y_stepsize configure -text \"" + yss.str() + "\"").c_str());
            Tcl_Eval(interp, (".main.input.z_stepsize configure -text \"" + zss.str() + "\"").c_str());
        } else {
            // Not enough coordinates to calculate stepsize
            Tcl_Eval(interp, ".main.input.x_stepsize configure -text \"N/A\"");
            Tcl_Eval(interp, ".main.input.y_stepsize configure -text \"N/A\"");
            Tcl_Eval(interp, ".main.input.z_stepsize configure -text \"N/A\"");
        }
    } catch (const std::exception& e) {
        // Error calculating stepsize
        Tcl_Eval(interp, ".main.input.x_stepsize configure -text \"Error\"");
        Tcl_Eval(interp, ".main.input.y_stepsize configure -text \"Error\"");
        Tcl_Eval(interp, ".main.input.z_stepsize configure -text \"Error\"");
    }
}

void AutoStageGUI::run() {
    if (interp) {
        Tk_MainLoop();
    }
}
