#include "AutoStageCoordCreator.h"
#include <windows.h>
#include <commctrl.h>
#include <commdlg.h>
#include <string>
#include <sstream>

#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "comdlg32.lib")

class WindowsGUI {
private:
    HWND hWnd, hXStart, hYStart, hZStart, hXEnd, hYEnd, hZEnd;
    HWND hNX, hNY, hNZ, hCreateBtn, hSaveBtn, hStatus;
    AutoStageCoordCreator coordCreator;
    
public:
    static LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
        WindowsGUI* gui = reinterpret_cast<WindowsGUI*>(GetWindowLongPtr(hwnd, GWLP_USERDATA));
        
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
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
        }
        return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
    
    void createWindow() {
        const char* className = "AutoStageGUI";
        WNDCLASS wc = {};
        wc.lpfnWndProc = WindowProc;
        wc.hInstance = GetModuleHandle(NULL);
        wc.lpszClassName = className;
        wc.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
        wc.hCursor = LoadCursor(NULL, IDC_ARROW);
        
        RegisterClass(&wc);
        
        hWnd = CreateWindowEx(
            0, className, "AutoStage Coordinate Creator",
            WS_OVERLAPPEDWINDOW, CW_USEDEFAULT, CW_USEDEFAULT, 500, 400,
            NULL, NULL, GetModuleHandle(NULL), NULL
        );
        
        SetWindowLongPtr(hWnd, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(this));
        createControls();
        ShowWindow(hWnd, SW_SHOW);
    }
    
    void createControls() {
        // Create header text
        CreateWindow("STATIC", "Insert coordinates in micrometers", 
            WS_VISIBLE | WS_CHILD | SS_LEFT,
            10, 10, 450, 20, hWnd, NULL, NULL, NULL);
        CreateWindow("STATIC", "Minimum step size 1 nm", 
            WS_VISIBLE | WS_CHILD | SS_LEFT,
            10, 25, 450, 15, hWnd, NULL, NULL, NULL);
            
        // Labels and input fields with default values - similar layout to tkinter version
        CreateWindow("STATIC", "X Start:", WS_VISIBLE | WS_CHILD,
            10, 50, 80, 20, hWnd, NULL, NULL, NULL);
        hXStart = CreateWindow("EDIT", "0.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 48, 100, 22, hWnd, (HMENU)2001, NULL, NULL);
            
        CreateWindow("STATIC", "X End:", WS_VISIBLE | WS_CHILD,
            220, 50, 80, 20, hWnd, NULL, NULL, NULL);
        hXEnd = CreateWindow("EDIT", "300.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            300, 48, 100, 22, hWnd, (HMENU)2002, NULL, NULL);
            
        CreateWindow("STATIC", "Y Start:", WS_VISIBLE | WS_CHILD,
            10, 80, 80, 20, hWnd, NULL, NULL, NULL);
        hYStart = CreateWindow("EDIT", "0.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 78, 100, 22, hWnd, (HMENU)2003, NULL, NULL);
            
        CreateWindow("STATIC", "Y End:", WS_VISIBLE | WS_CHILD,
            220, 80, 80, 20, hWnd, NULL, NULL, NULL);
        hYEnd = CreateWindow("EDIT", "300.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            300, 78, 100, 22, hWnd, (HMENU)2004, NULL, NULL);
            
        CreateWindow("STATIC", "Z Start:", WS_VISIBLE | WS_CHILD,
            10, 110, 80, 20, hWnd, NULL, NULL, NULL);
        hZStart = CreateWindow("EDIT", "0.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 108, 100, 22, hWnd, (HMENU)2005, NULL, NULL);
            
        CreateWindow("STATIC", "Z End:", WS_VISIBLE | WS_CHILD,
            220, 110, 80, 20, hWnd, NULL, NULL, NULL);
        hZEnd = CreateWindow("EDIT", "300.000", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            300, 108, 100, 22, hWnd, (HMENU)2006, NULL, NULL);
            
        CreateWindow("STATIC", "X Steps:", WS_VISIBLE | WS_CHILD,
            10, 140, 80, 20, hWnd, NULL, NULL, NULL);
        hNX = CreateWindow("EDIT", "0.001", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 138, 100, 22, hWnd, (HMENU)2007, NULL, NULL);
            
        CreateWindow("STATIC", "Y Steps:", WS_VISIBLE | WS_CHILD,
            220, 140, 80, 20, hWnd, NULL, NULL, NULL);
        hNY = CreateWindow("EDIT", "0.001", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            300, 138, 100, 22, hWnd, (HMENU)2008, NULL, NULL);
            
        CreateWindow("STATIC", "Z Steps:", WS_VISIBLE | WS_CHILD,
            10, 170, 80, 20, hWnd, NULL, NULL, NULL);
        hNZ = CreateWindow("EDIT", "0.001", WS_VISIBLE | WS_CHILD | WS_BORDER | WS_TABSTOP,
            100, 168, 100, 22, hWnd, (HMENU)2009, NULL, NULL);
            
        // Buttons (adjusted position for header)
        hCreateBtn = CreateWindow("BUTTON", "Create Coordinates", 
            WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON | WS_TABSTOP,
            50, 210, 150, 30, hWnd, (HMENU)1001, NULL, NULL);
            
        hSaveBtn = CreateWindow("BUTTON", "Save to File", 
            WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON | WS_TABSTOP,
            220, 210, 150, 30, hWnd, (HMENU)1002, NULL, NULL);
        EnableWindow(hSaveBtn, FALSE);
            
        // Status label (adjusted position for header)
        hStatus = CreateWindow("STATIC", "Ready to create coordinates...", 
            WS_VISIBLE | WS_CHILD,
            10, 260, 450, 20, hWnd, NULL, NULL, NULL);
    }
    
    std::string getWindowText(HWND hwnd) {
        int len = GetWindowTextLength(hwnd);
        std::string result(len, '\0');
        GetWindowText(hwnd, &result[0], len + 1);
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
            
            coordCreator.createCoordinates(params);
            
            std::string status = "Successfully created " + 
                std::to_string(coordCreator.getCoordinateCount()) + " coordinates";
            SetWindowText(hStatus, status.c_str());
            EnableWindow(hSaveBtn, TRUE);
            
        } catch (const std::exception& e) {
            MessageBox(hWnd, e.what(), "Error", MB_OK | MB_ICONERROR);
            SetWindowText(hStatus, "Error creating coordinates");
        }
    }
    
    void saveToFile() {
        OPENFILENAME ofn = {};
        char fileName[260] = "coordinates.txt";
        
        ofn.lStructSize = sizeof(ofn);
        ofn.hwndOwner = hWnd;
        ofn.lpstrFile = fileName;
        ofn.nMaxFile = sizeof(fileName);
        ofn.lpstrFilter = "Text Files\0*.txt\0All Files\0*.*\0";
        ofn.nFilterIndex = 1;
        ofn.Flags = OFN_PATHMUSTEXIST | OFN_OVERWRITEPROMPT;
        
        if (GetSaveFileName(&ofn)) {
            try {
                coordCreator.writeCoordinates(fileName);
                std::string status = "Coordinates saved to: " + std::string(fileName);
                SetWindowText(hStatus, status.c_str());
                MessageBox(hWnd, ("Coordinates successfully saved to:\n" + 
                    std::string(fileName)).c_str(), "Success", MB_OK | MB_ICONINFORMATION);
            } catch (const std::exception& e) {
                MessageBox(hWnd, e.what(), "Error", MB_OK | MB_ICONERROR);
                SetWindowText(hStatus, "Error saving coordinates");
            }
        }
    }
    
    void run() {
        createWindow();
        MSG msg = {};
        while (GetMessage(&msg, NULL, 0, 0)) {
            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }
    }
};

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    WindowsGUI gui;
    gui.run();
    return 0;
}
