#ifndef AUTOSTAGEGUI_H
#define AUTOSTAGEGUI_H

#include <tcl.h>
#include <tk.h>
#include <string>
#include <memory>
#include "AutoStageCoordCreator.h"

class AutoStageGUI {
public:
    AutoStageGUI();
    ~AutoStageGUI();
    
    void run();
    
private:
    // Tcl/Tk interpreter
    Tcl_Interp *interp;
    
    // Core functionality
    std::unique_ptr<AutoStageCoordCreator> coordCreator;
    
    // GUI setup
    void setupUI();
    void createWidgets();
    void setupCallbacks();
    
    // Callback functions
    static int createCoordinatesCallback(ClientData clientData, Tcl_Interp *interp, int argc, const char *argv[]);
    static int saveToFileCallback(ClientData clientData, Tcl_Interp *interp, int argc, const char *argv[]);
    
    // Helper functions
    bool validateInputs();
    void showError(const std::string& message);
    void showInfo(const std::string& message);
    std::string getEntryValue(const std::string& widgetName);
};

#endif // AUTOSTAGEGUI_H
