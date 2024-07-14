kB = 1.380649*10^-23;%J/K
T = 273.15 + 185;%K 
Vis = 1;%aSeVis(T);
time = 30*60; %s
L_left = 79*10^-6; %m
L_right = 79*10^-6; %m
b = 4; %Au NP to a-Se stick factor , 4 to 6
diameter = [1.8:0.1:50];
wavelength = [450,451];
plasmonArea = zeros(length(diameter),length(wavelength));
x = linspace(-L_left,L_right,100000);
for ir = 1:length(diameter) 
    R = (diameter(ir))*10^-9 / 2;
    D = kB*T/(b*pi*Vis*R);
    
    stat = exp(-x.^2/(4*D*time))/sqrt(4*pi*D*time);
    normstat = stat/max(stat);
    for iw = 1:length(wavelength)
        w = wavelength(iw);%m
        [alpha] = aSe_absorption(w)*100;
        light_dist_right = exp(-(L_right - x)*alpha);
        normlightDist = light_dist_right/max(light_dist_right);
        cross_right = min(normlightDist,normstat);
        plasmonArea(ir,iw) = trapz(cross_right);
    end
end
NormArea = 10.3005;
for iw = 1:length(wavelength)
NormPlasmonArea(:,iw) = plasmonArea(:,iw)/NormArea;
end
%stat(end)
figure(1)
surf(wavelength,diameter, NormPlasmonArea)

