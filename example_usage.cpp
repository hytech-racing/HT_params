#include <iostream>
#include "Parameters.h"

template<typename T>
void setParameter(T& paramType, float value) {
    paramType.set(value);
}

template<typename T>
auto getParameter(T& paramType){
    return paramType.get();
}

int main() {
    // Set parameter value
    setParameter(Parameters::MaxSpeedInstance, 160);

    setParameter(Parameters::ThresholdInstance, 20);
    // Get parameter value
    auto speed = getParameter(Parameters::MaxSpeedInstance);
    std::cout << "MaxSpeed: " << speed << std::endl;
    
    Parameters::floatLookupMap.at("b1fc2577")->set(69);
    speed = getParameter(Parameters::MaxSpeedInstance);
    std::cout << "MaxSpeed: " << speed << std::endl;
    
    return 0;
}
