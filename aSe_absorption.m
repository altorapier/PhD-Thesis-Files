function [alpha] = aSe_absorption(wavelength)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes herewavelength in nm, absioption in cm^-1
x = wavelength;
y0 = 5.7842;
A = -0.00595;
R0 = 0.0093;

y = y0 + A.*exp(R0.*x); 
alpha = 10.^y;
end

