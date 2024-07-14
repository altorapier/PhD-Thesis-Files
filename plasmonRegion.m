function [plasmonArea] = plasmonRegion(diameter, wavelength,L_left,L_right,b)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
kB = 1.380649*10^-23;%J/K
T = 273.15 + 185;%K 
Vis = 1;%aSeVis(T);
time = 30*60; %s
x = linspace(-L_left,L_right,100000);
R = (diameter)*10^-9 / 2;
D = kB*T./(b*pi*Vis*R);
stat = exp(-x.^2./(4*D*time))./sqrt(4*pi*D*time);
normstat = stat/max(stat);
[alpha] = aSe_absorption(wavelength)*100;
light_dist_right = exp(-(L_right - x)*alpha);
normlightDist = light_dist_right/max(light_dist_right);
cross_right = min(normlightDist,normstat);
plasmonArea = trapz(cross_right);
end

