#include "AutoStageCoordCreator.h"
#include <windows.h>
#include <commctrl.h>
#include <commdlg.h>
#include <richedit.h>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>

#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "comdlg32.lib")

class WindowsGUI {
private:
    HWND hWnd, hXStart, hYStart, hZStart, hXEnd, hYEnd, hZEnd;
    HWND hNX, hNY, hNZ, hCreateBtn, hSaveBtn, hStatus;
    HWND hXStepsize, hYStepsize, hZStepsize; // Stepsize display controls
    HWND hScramble; // Random Scramble Checkbox
    HWND hScanX, hScanY, hScanZ; // Scan direction radio buttons
    AutoStageCoordCreator coordCreator;
    std::vector<HWND> tabOrder; // For tab navigation
    
public:
    static LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
        WindowsGUI* gui = reinterpret_cast<WindowsGUI*>(GetWindowLongPtrA(hwnd, GWLP_USERDATA));
        
        switch (uMsg) {
        case WM_CREATE:
            return 0;
        case WM_COMMAND:
            if (gui) {
                if (LOWORD(wParam) == 1001) { // Create button
                    gui->createCoordinates();
                } else if (LOWORD(wParam) == 1002) { // Save button
                    gui->saveToFile();
                }
            }
            return 0;
        case WM_KEYDOWN:
            if (gui && wParam == VK_TAB) {
                // Handle tab navigation
                HWND currentFocus = GetFocus();
                bool shiftPressed = GetKeyState(VK_SHIFT) & 0x8000;
                gui->handleTabNavigation(currentFocus, shiftPressed);
                return 0;
            }
            break;
        case WM_CHAR:
            if (gui && wParam == VK_TAB) {
                // Prevent default tab handling
                return 0;
            }
            break;
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
        }
        return DefWindowProcA(hwnd, uMsg, wParam, lParam);
    }
    
    void createWindow() {
        const char* className = "AutoStageGUI";
        WNDCLASSA wc = {};
        wc.lpfnWndProc = WindowProc;
        wc.hInstance = GetModuleHandleA(NULL);
        wc.lpszClassName = className;
        wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
        wc.hCursor = LoadCursorA(NULL, (LPCSTR)IDC_ARROW);
        
        RegisterClassA(&wc);
        
        hWnd = CreateWindowExA(
            0, className, "AutoStage Coordinate Creator",
            WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 500, 460,
            NULL, NULL, GetModuleHandleA(NULL), NULL
        );
        
        SetWindowLongPtrA(hWnd, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(this));
        createControls();
        ShowWindow(hWnd, SW_SHOW);
    }
    
    void createControls() {
        // Create header text
        CreateWindowA("STATIC", "Insert coordinates in micrometers", 
            WS_VISIBLE | WS_CHILD | SS_LEFT,
            10, 10, 450, 20, hWnd, NULL, NULL, NULL);
        CreateWindowA("STATIC", "Minimum step size 1 nm", 
            WS_VISIBLE | WS_CHILD | SS_LEFT,
            10, 25, 450, 15, hWnd, NULL, NULL, NULL);
            
        // Labels and input fields with default values - similar layout to tkinter version
        CreateWindowA("STATIC", "X Start:", WS_VISIBLE | WS_CHILD,
            10, 50, 80, 20, hWnd, NULL, NULL, NULL);
        hXStart = CreateWindowA("EDIT", "0.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 48, 100, 22, hWnd, (HMENU)2001, NULL, NULL);
            
        CreateWindowA("STATIC", "X End:", WS_VISIBLE | WS_CHILD,
            220, 50, 80, 20, hWnd, NULL, NULL, NULL);
        hXEnd = CreateWindowA("EDIT", "300.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            300, 48, 100, 22, hWnd, (HMENU)2002, NULL, NULL);
            
        CreateWindowA("STATIC", "Y Start:", WS_VISIBLE | WS_CHILD,
            10, 80, 80, 20, hWnd, NULL, NULL, NULL);
        hYStart = CreateWindowA("EDIT", "0.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 78, 100, 22, hWnd, (HMENU)2003, NULL, NULL);
            
        CreateWindowA("STATIC", "Y End:", WS_VISIBLE | WS_CHILD,
            220, 80, 80, 20, hWnd, NULL, NULL, NULL);
        hYEnd = CreateWindowA("EDIT", "300.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            300, 78, 100, 22, hWnd, (HMENU)2004, NULL, NULL);
            
        CreateWindowA("STATIC", "Z Start:", WS_VISIBLE | WS_CHILD,
            10, 110, 80, 20, hWnd, NULL, NULL, NULL);
        hZStart = CreateWindowA("EDIT", "0.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 108, 100, 22, hWnd, (HMENU)2005, NULL, NULL);
            
        CreateWindowA("STATIC", "Z End:", WS_VISIBLE | WS_CHILD,
            220, 110, 80, 20, hWnd, NULL, NULL, NULL);
        hZEnd = CreateWindowA("EDIT", "300.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            300, 108, 100, 22, hWnd, (HMENU)2006, NULL, NULL);
            
        CreateWindowA("STATIC", "X Steps:", WS_VISIBLE | WS_CHILD,
            10, 140, 80, 20, hWnd, NULL, NULL, NULL);
        hNX = CreateWindowA("EDIT", "1", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 138, 100, 22, hWnd, (HMENU)2007, NULL, NULL);
            
        CreateWindowA("STATIC", "Y Steps:", WS_VISIBLE | WS_CHILD,
            220, 140, 80, 20, hWnd, NULL, NULL, NULL);
        hNY = CreateWindowA("EDIT", "1", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            300, 138, 100, 22, hWnd, (HMENU)2008, NULL, NULL);
            
        CreateWindowA("STATIC", "Z Steps:", WS_VISIBLE | WS_CHILD,
            10, 170, 80, 20, hWnd, NULL, NULL, NULL);
        hNZ = CreateWindowA("EDIT", "0", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 168, 100, 22, hWnd, (HMENU)2009, NULL, NULL);
            
        // Stepsize display section
        CreateWindowA("STATIC", "X Stepsize:", WS_VISIBLE | WS_CHILD,
            10, 200, 80, 20, hWnd, NULL, NULL, NULL);
        hXStepsize = CreateWindowA("STATIC", "N/A", WS_VISIBLE | WS_CHILD | WS_BORDER | SS_CENTER,
            100, 198, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindowA("STATIC", "Y Stepsize:", WS_VISIBLE | WS_CHILD,
            220, 200, 80, 20, hWnd, NULL, NULL, NULL);
        hYStepsize = CreateWindowA("STATIC", "N/A", WS_VISIBLE | WS_CHILD | WS_BORDER | SS_CENTER,
            300, 198, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindowA("STATIC", "Z Stepsize:", WS_VISIBLE | WS_CHILD,
            10, 230, 80, 20, hWnd, NULL, NULL, NULL);
        hZStepsize = CreateWindowA("STATIC", "N/A", WS_VISIBLE | WS_CHILD | WS_BORDER | SS_CENTER,
            100, 228, 100, 22, hWnd, NULL, NULL, NULL);

        // Random Scramble Checkbox
        hScramble = CreateWindowA("BUTTON", "Random Scramble Coordinates", 
            WS_VISIBLE | WS_CHILD | BS_AUTOCHECKBOX | WS_TABSTOP,
            10, 260, 250, 20, hWnd, (HMENU)2010, NULL, NULL);

        // Scan Direction Radio Buttons
        CreateWindowA("STATIC", "Scan Direction:", WS_VISIBLE | WS_CHILD,
            10, 290, 100, 20, hWnd, NULL, NULL, NULL);
        hScanX = CreateWindowA("BUTTON", "X", 
            WS_VISIBLE | WS_CHILD | BS_AUTORADIOBUTTON | WS_TABSTOP,
            120, 290, 40, 20, hWnd, (HMENU)2011, NULL, NULL);
        hScanY = CreateWindowA("BUTTON", "Y", 
            WS_VISIBLE | WS_CHILD | BS_AUTORADIOBUTTON | WS_TABSTOP,
            170, 290, 40, 20, hWnd, (HMENU)2012, NULL, NULL);
        hScanZ = CreateWindowA("BUTTON", "Z", 
            WS_VISIBLE | WS_CHILD | BS_AUTORADIOBUTTON | WS_TABSTOP,
            220, 290, 40, 20, hWnd, (HMENU)2013, NULL, NULL);
        SendMessage(hScanX, BM_SETCHECK, BST_CHECKED, 0); // Default to X
            
        // Buttons (adjusted position for stepsize display and checkbox)
        hCreateBtn = CreateWindowA("BUTTON", "Create Coordinates", 
            WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON | WS_TABSTOP,
            50, 320, 150, 30, hWnd, (HMENU)1001, NULL, NULL);
            
        hSaveBtn = CreateWindowA("BUTTON", "Save to File", 
            WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON | WS_TABSTOP,
            220, 320, 150, 30, hWnd, (HMENU)1002, NULL, NULL);
        EnableWindow(hSaveBtn, FALSE);
            
        // Status display (multi-line edit control with scrollbar)
        hStatus = CreateWindowA("EDIT", "Ready to create coordinates...", 
            WS_VISIBLE | WS_CHILD | WS_BORDER | ES_MULTILINE | ES_AUTOVSCROLL | ES_READONLY | WS_VSCROLL,
            10, 360, 470, 100, hWnd, NULL, NULL, NULL);
            
        // Set up tab order: X Start -> X End -> Y Start -> Y End -> Z Start -> Z End -> X Steps -> Y Steps -> Z Steps -> Scramble -> ScanX -> ScanY -> ScanZ -> Create -> Save
        tabOrder = {hXStart, hXEnd, hYStart, hYEnd, hZStart, hZEnd, hNX, hNY, hNZ, hScramble, hScanX, hScanY, hScanZ, hCreateBtn, hSaveBtn};
        
        // Set initial focus to first input field
        SetFocus(hXStart);
    }
    
    std::string getWindowText(HWND hwnd) {
        int len = GetWindowTextLengthA(hwnd);
        std::string result(len, '\0');
        GetWindowTextA(hwnd, &result[0], len + 1);
        return result;
    }
    
    void createCoordinates() {
        try {
            std::vector<double> params = {
                std::stod(getWindowText(hXStart)),
                std::stod(getWindowText(hYStart)),
                std::stod(getWindowText(hZStart)),
                std::stod(getWindowText(hXEnd)),
                std::stod(getWindowText(hYEnd)),
                std::stod(getWindowText(hZEnd)),
                std::stod(getWindowText(hNX)),
                std::stod(getWindowText(hNY)),
                std::stod(getWindowText(hNZ))
            };
            
            if (SendMessage(hScanX, BM_GETCHECK, 0, 0) == BST_CHECKED) {
                coordCreator.setScanDirection(AutoStageCoordCreator::ScanDirection::SCAN_X);
            } else if (SendMessage(hScanY, BM_GETCHECK, 0, 0) == BST_CHECKED) {
                coordCreator.setScanDirection(AutoStageCoordCreator::ScanDirection::SCAN_Y);
            } else {
                coordCreator.setScanDirection(AutoStageCoordCreator::ScanDirection::SCAN_Z);
            }

            coordCreator.createCoordinates(params);
            
            std::string status = "Successfully created " + 
                std::to_string(coordCreator.getCoordinateCount()) + " coordinates";
            SetWindowTextA(hStatus, status.c_str());
            EnableWindow(hSaveBtn, TRUE);
            
            // Update stepsize display
            updateStepsizeDisplay();
            
        } catch (const std::exception& e) {
            MessageBoxA(hWnd, e.what(), "Error", MB_OK | MB_ICONERROR);
            SetWindowTextA(hStatus, "Error creating coordinates");
        }
    }
    
    void saveToFile() {
        OPENFILENAMEA ofn = {};
        char fileName[260] = "coordinates.txt";
        
        ofn.lStructSize = sizeof(ofn);
        ofn.hwndOwner = hWnd;
        ofn.lpstrFile = fileName;
        ofn.nMaxFile = sizeof(fileName);
        ofn.lpstrFilter = "Text Files\0*.txt\0All Files\0*.*\0";
        ofn.nFilterIndex = 1;
        ofn.Flags = OFN_PATHMUSTEXIST | OFN_OVERWRITEPROMPT;
        
        if (GetSaveFileNameA(&ofn)) {
            try {
                bool scramble = (SendMessage(hScramble, BM_GETCHECK, 0, 0) == BST_CHECKED);
                coordCreator.writeCoordinates(fileName, scramble);
                
                std::string status = "Coordinates saved to: " + std::string(fileName);
                if (scramble) status += " (Scrambled)";
                SetWindowTextA(hStatus, status.c_str());
                MessageBoxA(hWnd, ("Coordinates successfully saved to:\n" + 
                    std::string(fileName)).c_str(), "Success", MB_OK | MB_ICONINFORMATION);
            } catch (const std::exception& e) {
                MessageBoxA(hWnd, e.what(), "Error", MB_OK | MB_ICONERROR);
                SetWindowTextA(hStatus, "Error saving coordinates");
            }
        }
    }
    
    void updateStepsizeDisplay() {
        try {
            // Get inputs directly to calculate proper step sizes
            // We can't rely just on coords[1]-coords[0] because of the loop nesting
            
            double xStart = std::stod(getWindowText(hXStart));
            double xEnd = std::stod(getWindowText(hXEnd));
            int nx = std::stoi(getWindowText(hNX));
            
            double yStart = std::stod(getWindowText(hYStart));
            double yEnd = std::stod(getWindowText(hYEnd));
            int ny = std::stoi(getWindowText(hNY));
            
            double zStart = std::stod(getWindowText(hZStart));
            double zEnd = std::stod(getWindowText(hZEnd));
            int nz = std::stoi(getWindowText(hNZ));
            
            // Apply bounds checking (matching logic in AutoStageCoordCreator)
            double xmin = 0, xmax = 300;
            double ymin = 0, ymax = 300;
            double zmin = 0, zmax = 300;
            
            if (xStart < xmin) xStart = xmin;
            if (xStart > xmax) xStart = xmax;
            if (xEnd < xmin) xEnd = xmin;
            if (xEnd > xmax) xEnd = xmax;
            
            if (yStart < ymin) yStart = ymin;
            if (yStart > ymax) yStart = ymax;
            if (yEnd < ymin) yEnd = ymin;
            if (yEnd > ymax) yEnd = ymax;
            
            if (zStart < zmin) zStart = zmin;
            if (zStart > zmax) zStart = zmax;
            if (zEnd < zmin) zEnd = zmin;
            if (zEnd > zmax) zEnd = zmax;

            // Calculate stepsizes
            double xStepsize = (nx > 1) ? std::abs(xEnd - xStart) / (nx - 1) : 0.0;
            double yStepsize = (ny > 1) ? std::abs(yEnd - yStart) / (ny - 1) : 0.0;
            double zStepsize = (nz > 1) ? std::abs(zEnd - zStart) / (nz - 1) : 0.0;
            
            // Format and display the stepsizes
            std::string xStepsizeStr = std::to_string(xStepsize);
            std::string yStepsizeStr = std::to_string(yStepsize);
            std::string zStepsizeStr = std::to_string(zStepsize);
            
            // Limit to 6 decimal places
            if (xStepsizeStr.find('.') != std::string::npos) {
                xStepsizeStr = xStepsizeStr.substr(0, xStepsizeStr.find('.') + 7);
            }
            if (yStepsizeStr.find('.') != std::string::npos) {
                yStepsizeStr = yStepsizeStr.substr(0, yStepsizeStr.find('.') + 7);
            }
            if (zStepsizeStr.find('.') != std::string::npos) {
                zStepsizeStr = zStepsizeStr.substr(0, zStepsizeStr.find('.') + 7);
            }
            
            SetWindowTextA(hXStepsize, xStepsizeStr.c_str());
            SetWindowTextA(hYStepsize, yStepsizeStr.c_str());
            SetWindowTextA(hZStepsize, zStepsizeStr.c_str());
        } catch (const std::exception& e) {
            SetWindowTextA(hXStepsize, "Error");
            SetWindowTextA(hYStepsize, "Error");
            SetWindowTextA(hZStepsize, "Error");
        }
    }
    
    void handleTabNavigation(HWND currentFocus, bool shiftPressed) {
        // Find current control in tab order
        auto it = std::find(tabOrder.begin(), tabOrder.end(), currentFocus);
        if (it != tabOrder.end()) {
            int currentIndex = std::distance(tabOrder.begin(), it);
            int nextIndex;
            
            if (shiftPressed) {
                // Shift+Tab: go to previous control
                nextIndex = (currentIndex - 1 + tabOrder.size()) % tabOrder.size();
            } else {
                // Tab: go to next control
                nextIndex = (currentIndex + 1) % tabOrder.size();
            }
            
            SetFocus(tabOrder[nextIndex]);
        }
    }
    
    void run() {
        createWindow();
        MSG msg = {};
        while (GetMessage(&msg, NULL, 0, 0)) {
            // Use IsDialogMessage for proper tab navigation
            if (!IsDialogMessage(hWnd, &msg)) {
                TranslateMessage(&msg);
                DispatchMessage(&msg);
            }
        }
    }
};

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    WindowsGUI gui;
    gui.run();
    return 0;
}
