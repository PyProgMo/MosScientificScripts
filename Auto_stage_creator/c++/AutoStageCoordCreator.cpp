#include "AutoStageCoordCreator.h"
#include <fstream>
#include <sstream>
#include <iomanip>
#include <iostream>
#include <cmath>

AutoStageCoordCreator::AutoStageCoordCreator(double xmin, double xmax, 
                                           double ymin, double ymax, 
                                           double zmin, double zmax)
    : xmin(xmin), xmax(xmax), ymin(ymin), ymax(ymax), zmin(zmin), zmax(zmax),
      roundx(2), roundy(2), roundz(2) {
}

void AutoStageCoordCreator::setRounding(int x_round, int y_round, int z_round) {
    roundx = x_round;
    roundy = y_round;
    roundz = z_round;
}

void AutoStageCoordCreator::createCoordinates(const std::vector<double>& params) {
    if (params.size() != 9) {
        throw std::invalid_argument("Parameters array must contain exactly 9 elements");
    }
    
    double x_start = params[0];
    double y_start = params[1];
    double z_start = params[2];
    double x_end = params[3];
    double y_end = params[4];
    double z_end = params[5];
    int nx = static_cast<int>(params[6]);
    int ny = static_cast<int>(params[7]);
    int nz = static_cast<int>(params[8]);
    
    // Debug output to show what we received
    std::cout << "Received parameters:" << std::endl;
    std::cout << "X: " << x_start << " to " << x_end << " (" << nx << " steps)" << std::endl;
    std::cout << "Y: " << y_start << " to " << y_end << " (" << ny << " steps)" << std::endl;
    std::cout << "Z: " << z_start << " to " << z_end << " (" << nz << " steps)" << std::endl;
    
    // Apply bounds checking - only clamp if outside bounds (matching Python logic)
    // Note: The Python version has some inconsistent logic, but we'll implement proper clamping
    if (x_start < xmin) x_start = xmin;
    if (x_start > xmax) x_start = xmax;
    if (x_end < xmin) x_end = xmin;
    if (x_end > xmax) x_end = xmax;
    
    if (y_start < ymin) y_start = ymin;
    if (y_start > ymax) y_start = ymax;
    if (y_end < ymin) y_end = ymin;
    if (y_end > ymax) y_end = ymax;
    
    if (z_start < zmin) z_start = zmin;
    if (z_start > zmax) z_start = zmax;
    if (z_end < zmin) z_end = zmin;
    if (z_end > zmax) z_end = zmax;
    
    std::cout << "After bounds checking:" << std::endl;
    std::cout << "X: " << x_start << " to " << x_end << " (" << nx << " steps)" << std::endl;
    std::cout << "Y: " << y_start << " to " << y_end << " (" << ny << " steps)" << std::endl;
    std::cout << "Z: " << z_start << " to " << z_end << " (" << nz << " steps)" << std::endl;
    
    // Generate coordinate arrays
    std::vector<double> x_coords = linspace(x_start, x_end, nx);
    std::vector<double> y_coords = linspace(y_start, y_end, ny);
    std::vector<double> z_coords = linspace(z_start, z_end, nz);
    
    // Handle empty coordinate arrays
    if (x_coords.empty()) x_coords.push_back(x_start);
    if (y_coords.empty()) y_coords.push_back(y_start);
    if (z_coords.empty()) z_coords.push_back(z_start);
    
    std::cout << "Length of x_coords: " << x_coords.size() 
              << ", y_coords: " << y_coords.size() 
              << ", z_coords: " << z_coords.size() << std::endl;
    std::cout << "Will create " << x_coords.size() << " * " << y_coords.size() 
              << " * " << z_coords.size() << " = " 
              << (x_coords.size() * y_coords.size() * z_coords.size()) 
              << " coordinates" << std::endl;
    
    // Clear previous coordinates
    coordinates.clear();
    
    // Generate all coordinate combinations
    for (double x : x_coords) {
        for (double y : y_coords) {
            for (double z : z_coords) {
                coordinates.emplace_back(x, y, z);
            }
        }
    }
}

void AutoStageCoordCreator::writeCoordinates(const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open file for writing: " + filename);
    }
    
    if (coordinates.empty()) {
        throw std::runtime_error("No coordinates to write");
    }
    
    // Write first coordinate without newline prefix
    auto [x, y, z] = coordinates[0];
    file << formatDouble(x, roundx) << "," 
         << formatDouble(y, roundy) << "," 
         << formatDouble(z, roundz);
    
    // Write remaining coordinates with newline prefix
    for (size_t i = 1; i < coordinates.size(); ++i) {
        auto [x, y, z] = coordinates[i];
        file << "\n" << formatDouble(x, roundx) << "," 
             << formatDouble(y, roundy) << "," 
             << formatDouble(z, roundz);
    }
    
    file.close();
}

void AutoStageCoordCreator::clearCoordinates() {
    coordinates.clear();
}

std::vector<double> AutoStageCoordCreator::linspace(double start, double end, int num) {
    std::vector<double> result;
    
    if (num <= 0) {
        return result;
    }
    
    if (num == 1) {
        result.push_back(start);
        return result;
    }
    
    double step = (end - start) / (num - 1);
    for (int i = 0; i < num; ++i) {
        result.push_back(start + i * step);
    }
    
    return result;
}

std::string AutoStageCoordCreator::formatDouble(double value, int precision) {
    std::ostringstream oss;
    oss << std::fixed << std::setprecision(precision) << value;
    return oss.str();
}
