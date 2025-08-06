#ifndef AUTOSTAGECOORDCREATOR_H
#define AUTOSTAGECOORDCREATOR_H

#include <vector>
#include <string>

class AutoStageCoordCreator {
public:
    AutoStageCoordCreator(double xmin = 0, double xmax = 300, 
                         double ymin = 0, double ymax = 300, 
                         double zmin = 0, double zmax = 300);
    
    void setRounding(int x_round = 2, int y_round = 2, int z_round = 2);
    void createCoordinates(const std::vector<double>& params);
    void writeCoordinates(const std::string& filename);
    void clearCoordinates();
    
    size_t getCoordinateCount() const { return coordinates.size(); }
    
private:
    double xmin, xmax, ymin, ymax, zmin, zmax;
    int roundx, roundy, roundz;
    std::vector<std::tuple<double, double, double>> coordinates;
    
    std::vector<double> linspace(double start, double end, int num);
    std::string formatDouble(double value, int precision);
};

#endif // AUTOSTAGECOORDCREATOR_H
