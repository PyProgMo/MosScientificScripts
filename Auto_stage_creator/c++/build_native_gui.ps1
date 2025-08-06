# Alternative approach: Build GUI with Windows API instead of Tcl/Tk
# This creates a native Windows GUI that looks similar to tkinter

Write-Host "Building Windows Native GUI (Alternative to Tcl/Tk)" -ForegroundColor Cyan

$nativeGuiCode = @'
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
        // Labels and input fields - similar layout to tkinter version
        CreateWindow("STATIC", "X Start:", WS_VISIBLE | WS_CHILD,
            10, 20, 80, 20, hWnd, NULL, NULL, NULL);
        hXStart = CreateWindow("EDIT", "", WS_VISIBLE | WS_CHILD | WS_BORDER,
            100, 18, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindow("STATIC", "X End:", WS_VISIBLE | WS_CHILD,
            220, 20, 80, 20, hWnd, NULL, NULL, NULL);
        hXEnd = CreateWindow("EDIT", "", WS_VISIBLE | WS_CHILD | WS_BORDER,
            300, 18, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindow("STATIC", "Y Start:", WS_VISIBLE | WS_CHILD,
            10, 50, 80, 20, hWnd, NULL, NULL, NULL);
        hYStart = CreateWindow("EDIT", "", WS_VISIBLE | WS_CHILD | WS_BORDER,
            100, 48, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindow("STATIC", "Y End:", WS_VISIBLE | WS_CHILD,
            220, 50, 80, 20, hWnd, NULL, NULL, NULL);
        hYEnd = CreateWindow("EDIT", "", WS_VISIBLE | WS_CHILD | WS_BORDER,
            300, 48, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindow("STATIC", "Z Start:", WS_VISIBLE | WS_CHILD,
            10, 80, 80, 20, hWnd, NULL, NULL, NULL);
        hZStart = CreateWindow("EDIT", "", WS_VISIBLE | WS_CHILD | WS_BORDER,
            100, 78, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindow("STATIC", "Z End:", WS_VISIBLE | WS_CHILD,
            220, 80, 80, 20, hWnd, NULL, NULL, NULL);
        hZEnd = CreateWindow("EDIT", "", WS_VISIBLE | WS_CHILD | WS_BORDER,
            300, 78, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindow("STATIC", "X Steps:", WS_VISIBLE | WS_CHILD,
            10, 110, 80, 20, hWnd, NULL, NULL, NULL);
        hNX = CreateWindow("EDIT", "", WS_VISIBLE | WS_CHILD | WS_BORDER,
            100, 108, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindow("STATIC", "Y Steps:", WS_VISIBLE | WS_CHILD,
            220, 110, 80, 20, hWnd, NULL, NULL, NULL);
        hNY = CreateWindow("EDIT", "", WS_VISIBLE | WS_CHILD | WS_BORDER,
            300, 108, 100, 22, hWnd, NULL, NULL, NULL);
            
        CreateWindow("STATIC", "Z Steps:", WS_VISIBLE | WS_CHILD,
            10, 140, 80, 20, hWnd, NULL, NULL, NULL);
        hNZ = CreateWindow("EDIT", "", WS_VISIBLE | WS_CHILD | WS_BORDER,
            100, 138, 100, 22, hWnd, NULL, NULL, NULL);
            
        // Buttons
        hCreateBtn = CreateWindow("BUTTON", "Create Coordinates", 
            WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON,
            50, 180, 150, 30, hWnd, (HMENU)1001, NULL, NULL);
            
        hSaveBtn = CreateWindow("BUTTON", "Save to File", 
            WS_VISIBLE | WS_CHILD | BS_PUSHBUTTON,
            220, 180, 150, 30, hWnd, (HMENU)1002, NULL, NULL);
        EnableWindow(hSaveBtn, FALSE);
            
        // Status label
        hStatus = CreateWindow("STATIC", "Ready to create coordinates...", 
            WS_VISIBLE | WS_CHILD,
            10, 230, 450, 20, hWnd, NULL, NULL, NULL);
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
'@

$nativeGuiCode | Out-File -FilePath "windows_gui_main.cpp" -Encoding UTF8

Write-Host "Created windows_gui_main.cpp - Native Windows GUI" -ForegroundColor Green
Write-Host "This provides the same functionality as tkinter but uses Windows API" -ForegroundColor Yellow

# Create build script for Windows GUI
$winGuiBatch = @"
@echo off
echo Building Native Windows GUI version...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
cd /d "%~dp0"

if not exist build_wingui mkdir build_wingui
cd build_wingui

cl /EHsc /std:c++17 ..\windows_gui_main.cpp ..\AutoStageCoordCreator.cpp /Fe:AutoStageGUI.exe /link user32.lib gdi32.lib comctl32.lib comdlg32.lib

if %ERRORLEVEL% EQU 0 (
    echo Windows GUI build successful!
    echo Executable: build_wingui\AutoStageGUI.exe
    echo Starting the GUI...
    AutoStageGUI.exe
) else (
    echo Windows GUI build failed
)
pause
"@

$winGuiBatch | Out-File -FilePath "compile_windows_gui.bat" -Encoding ASCII
Write-Host "Created compile_windows_gui.bat" -ForegroundColor Green
Write-Host "Run this to build and start the Windows native GUI" -ForegroundColor Yellow
